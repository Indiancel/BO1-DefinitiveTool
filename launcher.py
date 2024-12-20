import subprocess
import os
import webbrowser  # Import the webbrowser module to open URLs
from colorama import init, Fore

# Initialize colorama
init(autoreset=True)

# Ensure the working directory is where the launcher.py is located
script_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_directory)

# File to store the token, channel, and log directory
CONFIG_FILE = os.path.join(script_directory, "config.txt")

def load_config():
    """Load the token, channel, and log directory from the config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            lines = file.readlines()
            if len(lines) >= 3:
                return lines[0].strip(), lines[1].strip(), lines[2].strip()
    return None, None, None

def save_config(token, channel, log_dir):
    """Save the token, channel, and log directory to the config file."""
    try:
        with open(CONFIG_FILE, "w") as file:
            file.write(f"{token}\n{channel}\n{log_dir}")
        print(f"Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"Error saving configuration: {e}")
        exit(1)

def ensure_oauth_prefix(token):
    """Ensure that the 'oauth:' prefix is added to the token if missing."""
    if not token.startswith("oauth:"):
        token = "oauth:" + token
    return token

def setup_or_load_config():
    """Ensure configuration exists, prompting user if necessary."""
    current_token, current_channel, current_log_dir = load_config()

    if not current_token or not current_channel or not current_log_dir:
        print(Fore.RED + f"Configuration file not found!")  # Colored in red
        
        # Ask the user for the TIM log folder directory
        current_log_dir = input("Enter your full TIM log folder directory (Call of Duty Black Ops\\logs):").strip()

        if not os.path.isdir(current_log_dir):
            print("Error: The provided directory does not exist.")
            exit(1)

        # Ask if the user already has a token
        user_response = input("Do you already have a Twitch Bot Chat token? (Y/N): ").strip().upper()
        
        if user_response == "Y":
            current_token = input("Enter your Twitch Bot Chat Token: ").strip()
        elif user_response == "N":
            print("Generate your Twitch Bot Chat Token:")
            print("https://twitchtokengenerator.com/")  # Print the URL, clickable in some terminals
            current_token = input("Enter your generated Twitch Bot Chat Token: ").strip()
        else:
            print("Invalid input. Please enter Y or N.")
            exit(1)

        # Ensure the token has the 'oauth:' prefix if missing
        current_token = ensure_oauth_prefix(current_token)

        current_channel = input("Enter the Twitch channel to join: ").strip()

        if not current_token or not current_channel or not current_log_dir:
            print("Error: Bot Chat Token, Channel, and Log Directory are required to start the program.")
            exit(1)

        save_config(current_token, current_channel, current_log_dir)

    return current_token, current_channel, current_log_dir

def update_autotim_file(token, channel, log_dir):
    """Write the token, channel, and log directory to the AutoTIM.py file."""
    auto_tim_path = os.path.join(script_directory, "AutoTIM.py")
    try:
        with open(auto_tim_path, "r") as file:
            content = file.read()

        content = content.replace("TOKEN_1 = 'TOKEN'", f"TOKEN_1 = '{token}'")
        content = content.replace("CHANNEL = 'CHANNEL'", f"CHANNEL = '{channel}'")

        with open(auto_tim_path, "w") as file:
            file.write(content)
        print(f"AutoTIM.py updated with token and channel.")
    except Exception as e:
        print(f"Failed to update AutoTIM.py: {e}")
        exit(1)

    # Now update TExport.py to set the log_dir path
    t_export_path = os.path.join(script_directory, "TExport.py")
    try:
        with open(t_export_path, "r") as file:
            content = file.read()

        # Update the log_dir assignment
        content = content.replace('log_dir = ""', f'log_dir = r"{log_dir}"')

        with open(t_export_path, "w") as file:
            file.write(content)
        print(f"TExport.py updated with log directory.")
    except Exception as e:
        print(f"Failed to update TExport.py: {e}")
        exit(1)

# Main flow
try:
    current_token, current_channel, current_log_dir = setup_or_load_config()
    update_autotim_file(current_token, current_channel, current_log_dir)

    # Start both scripts
    subprocess.Popen(["python", "TExport.py"])
    subprocess.Popen(["python", "AutoTIM.py"])
    print("Twitch Bot scripts are now running.")
except Exception as e:
    print(f"An error occurred: {e}")

# Keep the console open by waiting for user input (like the 'pause' in a batch file)
input("")
