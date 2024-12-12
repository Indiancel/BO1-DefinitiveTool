import subprocess
import os

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Change directory to the script's directory
os.chdir(current_directory)

# Start both scripts
subprocess.Popen(["python", "TExport.py"])
subprocess.Popen(["python", "AutoTIM.py"])

# Keep the console open by waiting for user input (like the 'pause' in a batch file)
input("Press Enter to close...")
