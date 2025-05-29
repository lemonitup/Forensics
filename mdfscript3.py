#!/usr/bin/env python3
import os
import hashlib
import subprocess

# Directories to pull from Android device
DIRS_TO_PULL = ["/system", "/vendor", "/data", "/etc"]
LOCAL_DUMP_DIR = "./android_dump"

# Dynamically get supported algorithms from hashlib
SUPPORTED_HASHES = hashlib.algorithms_guaranteed

def adb_pull_directories():
    os.makedirs(LOCAL_DUMP_DIR, exist_ok=True)
    for directory in DIRS_TO_PULL:
        local_path = os.path.join(LOCAL_DUMP_DIR, directory.strip("/").replace("/", "_"))
        print(f"[+] Pulling {directory} to {local_path}")
        subprocess.run(["adb", "pull", directory, local_path], stderr=subprocess.DEVNULL)

def compute_hash(file_path, hash_type):
    try:
        hash_func = hashlib.new(hash_type)
    except ValueError:
        print(f"[x] Unsupported hash type: {hash_type}")
        return None

    try:
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

if __name__ == "__main__":
    adb_pull_directories()

    # Add your known hashes here; you can add any type from hashlib.algorithms_guaranteed
    targets = [
        ("sha256", "d82543b4c8b8aa4e67c21f6f76ae28d0a87d293593d8a865337b1e9be03cf382"),
        # ("sha1", "your_sha1_hash_here"),
        # ("sha224", "your_sha224_hash_here"),
        # ("md5", "your_md5_hash_here")
    ]

    for htype, hval in targets:
        if htype in SUPPORTED_HASHES:
            find_file_by_hash(hval, htype)
        else:
            print(f"[x] Skipping unsupported hash type: {htype}")
