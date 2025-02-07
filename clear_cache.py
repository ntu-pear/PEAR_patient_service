import os
import shutil

def clear_pycache():
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                dir_path = os.path.join(root, dir_name)
                shutil.rmtree(dir_path)
                print(f"Removed: {dir_path}")
        for file_name in files:
            if file_name.endswith(".pyc"):
                file_path = os.path.join(root, file_name)
                os.remove(file_path)
                print(f"Removed: {file_path}")

if __name__ == "__main__":
    clear_pycache()
    print("All caches cleared!")
