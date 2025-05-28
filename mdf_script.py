#!/usr/bin/env python3
import os
import hashlib
import subprocess

# Directories to pull
DIRS_TO_PULL = ["/system", "/vendor", "/data", "/etc"]
LOCAL_DUMP_DIR = "./android_dump"

def adb_pull_directories():
    os.makedirs(LOCAL_DUMP_DIR, exist_ok=True)
    for directory in DIRS_TO_PULL:
        local_path = os.path.join(LOCAL_DUMP_DIR, directory.strip("/").replace("/", "_"))
        print(f"[+] Pulling {directory} to {local_path}")
        subprocess.run(["adb", "pull", directory, local_path], stderr=subprocess.DEVNULL)

def compute_hash(file_path, hash_type):
    hash_func = getattr(hashlib, hash_type)()
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

##CHANGE THE HASH OR ADD IF YOU WANT
if __name__ == "__main__":
    adb_pull_directories()
    # Sample: replace below values with dynamic input if needed
    targets = [
        ("sha224", "640456927de5e7e532a46b3fbf82147439c0abd6e60b023acbf3c8dd"),
        ("sha256", "e3346422e123170f43f232be9344d66a7f7eea3d066cd4593e31bac3b7237a68"),
        ("sha384", "75b1758e118c381da731565bfca047273c6d2bc1665bbe8b91db4237bbe57ba27c1401e5a2e73e4c098b942e06d81e63")
    ]
    for htype, hval in targets:
        find_file_by_hash(hval, htype)
