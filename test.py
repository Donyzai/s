import subprocess

try:
    subprocess.run(["sleep 10"],timeout=5,shell=True)
except Exception as e:
    print(e)