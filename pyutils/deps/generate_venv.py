def generate_venv(foldername : str):
    import subprocess
    import sys
    import os

    # setup venv
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    venv_python = os.path.join("venv", "bin", "python")
    subprocess.run([venv_python, "-m", "pip", "install", "pipreqs"], check=True)

    # Install generate requirements and install
    subprocess.run(["pipreqs", foldername], check=True)
    command = f"source venv/bin/activate && pip install -r {foldername}/requirements.txt"
    subprocess.run(command, shell=True, executable='/bin/bash', check=True)