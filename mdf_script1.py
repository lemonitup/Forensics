#!/usr/bin/env python3
import os
import hashlib
import subprocess
import argparse
import sys

LOCAL_DUMP_DIR = "./android_dump"

def adb_connect(ip):
    print(f"[+] Connecting to {ip}:5555 via ADB...")
    result = subprocess.run(["adb", "connect", f"{ip}:5555"], capture_output=True, text=True)
    if "connected" in result.stdout.lower():
        print("[+] Connected successfully.")
    else:
        print("[x] Failed to connect to the device.")
        print(result.stdout)
        sys.exit(1)

def adb_pull_directories(directories):
    os.makedirs(LOCAL_DUMP_DIR, exist_ok=True)
    for directory in directories:
        local_path = os.path.join(LOCAL_DUMP_DIR, directory.strip("/").replace("/", "_"))
        print(f"[+] Pulling {directory} to {local_path}")
        subprocess.run(["adb", "pull", directory, local_path])

def compute_hash(file_path, hash_type):
    try:
        hash_func = hashlib.new(hash_type)
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        return None

def find_file_by_hash(target_hash, hash_type):
    print(f"[+] Searching for hash: {target_hash} ({hash_type})")
    for root, dirs, files in os.walk(LOCAL_DUMP_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            file_hash = compute_hash(full_path, hash_type)
            if file_hash and file_hash.lower() == target_hash.lower():
                relative_path = os.path.relpath(full_path, LOCAL_DUMP_DIR)
                print(f"[!] Match found: {relative_path}")
                return relative_path
    print("[x] No match found.")
    return None

def main():
    parser = argparse.ArgumentParser(description="ADB pull + hash match scanner")
    parser.add_argument("hash_type", help="Hash type (e.g., sha224, sha256, sha512)")
    parser.add_argument("target_hash", help="Target hash value to search for")
    parser.add_argument("--ip", help="Device IP to connect over ADB")
    parser.add_argument("--remote-dir", nargs="*", default=["/system", "/vendor", "/data", "/etc"], help="List of directories to pull")
    args = parser.parse_args()

    if args.hash_type.lower() not in hashlib.algorithms_guaranteed:
        print(f"[x] Unsupported hash type: {args.hash_type}")
        print("[!] Supported types:", ", ".join(sorted(hashlib.algorithms_guaranteed)))
        sys.exit(1)

    if args.ip:
        adb_connect(args.ip)

    adb_pull_directories(args.remote_dir)
    find_file_by_hash(args.target_hash, args.hash_type.lower())

if __name__ == "__main__":
    main()
