# backend/ingester.py
import os
import subprocess
import shutil
import tempfile

def clone_repository(repo_url: str) -> str:
    temp_dir = tempfile.mkdtemp(prefix="code_chatter_")
    try:
        print(f"Cloning {repo_url} into {temp_dir}...")
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, temp_dir],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        return temp_dir
    except subprocess.CalledProcessError as e:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        raise RuntimeError(f"Failed to clone repository: {e.stderr.decode().strip()}")