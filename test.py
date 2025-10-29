import os

if os.system(f"ping -c 1 12.1.1.1"):
#if os.system(f"curl http://192.168.60.138:1322121351 -I GET 2>/dev/null"):
    print(True)
else:
    print(False)