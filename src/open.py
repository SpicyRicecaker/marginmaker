import sys
import subprocess
import os


def open_file_cross_platform(path):
	if sys.platform == "win32":
		os.startfile(path)
	elif sys.platform == "darwin":  # macOS
		subprocess.run(["open", path])
	else:  # Linux / Unix
		subprocess.run(["xdg-open", path])
