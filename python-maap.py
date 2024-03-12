import os
import sys
import platform

print("Python version")
print(sys.version)
print("Version info.")
print(sys.version_info)
print("Platform info.")
print(platform.platform())
print("System info.")
print(platform.system())
print("Machine info.")
print(platform.machine())
name = "PATH"
print(f"PATH: {os.environ.get(name)}")