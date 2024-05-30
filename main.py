import os
import time
import hashlib
import sys
import logging

def calculate_md5(file_path):
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
    return md5_hash.hexdigest()

def sync_folders(source_folder, replica_folder, log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(console_handler)

    while True:
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                source_file_path = os.path.join(root, file)
                replica_file_path = source_file_path.replace(source_folder, replica_folder)
                replica_file_dir = os.path.dirname(replica_file_path)
                if not os.path.exists(replica_file_dir):
                    os.makedirs(replica_file_dir)
                if not os.path.exists(replica_file_path):
                    logging.info(f"Copying file {source_file_path} to {replica_file_path}")
                    with open(source_file_path, "rb") as src, open(replica_file_path, "wb") as dst:
                        dst.write(src.read())
                elif calculate_md5(source_file_path) != calculate_md5(replica_file_path):
                    logging.info(f"Updating file {source_file_path} to {replica_file_path}")
                    with open(source_file_path, "rb") as src, open(replica_file_path, "wb") as dst:
                        dst.write(src.read())

        for root, dirs, files in os.walk(replica_folder, topdown=False):
            for file in files:
                replica_file_path = os.path.join(root, file)
                source_file_path = replica_file_path.replace(replica_folder, source_folder)
                if not os.path.exists(source_file_path):
                    logging.info(f"Removing file {replica_file_path}")
                    os.remove(replica_file_path)

        time.sleep(int(sys.argv[3]))

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python sync_folders.py <source_folder> <replica_folder> <sync_interval> <log_file>")
        sys.exit(1)

    source_folder = sys.argv[1]
    replica_folder = sys.argv[2]
    sync_interval = sys.argv[3]
    log_file = sys.argv[4]

    sync_folders(source_folder, replica_folder, log_file)