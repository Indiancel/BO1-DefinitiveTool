import os
import time
import re

# Define directories
log_dir = r"C:\Program Files (x86)\Steam\steamapps\common\Call of Duty Black Ops\logs"
output_dir = os.path.join(log_dir, "output")
output_file = os.path.join(output_dir, "AHK_TIM_Logs.txt")

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Initialize tracking variables
last_position = 0
powerup_counter = 0
quick_revive_counter = 0
player_down_counter = 0
down_rounds = []  # Track rounds where downs occurred
death_rounds = []
cycle_count = 1
current_round_value = None  # Store the current round value
dog_round_flag = False  # Flag to check if a dog round was detected

# Round information based on the Pastebin content
round_info = [
    "6",            # Round 1 
    "8",               # Round 2
    "13",             # Round 3
    "18",              # Round 4
    "24 (1)",                 # Round 5
    "27 (1.12)",             # Round 6
    "28 (1.16)",             # Round 7
    "28 (1.16)",             # Round 8
    "29 (1.20)",             # Round 9
    "33 (1.37)",             # Round 10
    "34 (1.41)",             # Round 11
    "36 (1.5)",               # Round 12
    "39 (1.62)",             # Round 13
    "41 (1.70)",             # Round 14
    "44 (1.83)",             # Round 15
    "47 (1.95)",             # Round 16
    "50 (2.08)",             # Round 17
    "53 (2.20)",             # Round 18
    "56 (2.33) | Prenades: 1",    # Round 19
    "60 (2.5) | Prenades: 2",      # Round 20
    "63 (2.62) | Prenades: 3",    # Round 21
    "67 (2.79) | Prenades: 4",    # Round 22
    "71 (2.95) | Prenades: 5",    # Round 23
    "75 (3.12) | Prenades: 6",    # Round 24
    "80 (3.33) | Prenades: 7",    # Round 25
    "84 (3.5) | Prenades: 8",      # Round 26
    "89 (3.70) | Prenades: 10",   # Round 27
    "94 (3.91) | Prenades: 12",   # Round 28
    "99 (4.12) | Prenades: 14",   # Round 29
    "105 (4.37) | Prenades: 16",  # Round 30
    "110 (4.58) | Prenades: 18",  # Round 31
    "116 (4.83) | Prenades: 20",  # Round 32
    "122 (5.08) | Prenades: 22",  # Round 33
    "128 (5.33) | Prenades: 24",  # Round 34
    "134 (5.58) | Prenades: 28",  # Round 35
    "140 (5.83) | Prenades: 33",  # Round 36
    "147 (6.12) | Prenades: 36",  # Round 37
    "153 (6.37) | Prenades: 40",  # Round 38
    "160 (6.667) | Prenades: 44",  # Round 39
    "168 (7) | Prenades: 50",      # Round 40
    "175 (7.29) | Prenades: 56",  # Round 41
    "182 (7.58) | Prenades: 64",  # Round 42
    "190 (7.91) | Prenades: 72",  # Round 43
    "198 (8.25) | Prenades: 80",   # Round 44
    "206 (8.58) | Prenades: 90",  # Round 45
    "214 (8.91) | Prenades: 100", # Round 46
    "222 (9.25) | Prenades: 117",  # Round 47
    "231 (9.62) | Prenades: 129", # Round 48
    "240 (10) | Prenades: 142",    # Round 49
    "249 (10.37) | Prenades: 156",# Round 50
    "258 (10.7) | Prenades: 172", # Round 51
    "267 (11.12) | Prenades: 189",# Round 52
    "276 (11.5) | Prenades: 208",  # Round 53
    "286 (11.91) | Prenades: 229", # Round 54
    "296 (12.33) | Prenades: 252", # Round 55
    "306 (12.75) | Prenades: 277",  # Round 56
    "316 (13.16) | Prenades: 305", # Round 57
    "326 (13.58) | Prenades: 336", # Round 58
    "337 (14.04) | Prenades: 369", # Round 59
    "348 (14.5)"              # Round 60
]






def get_newest_log_file(directory):
    log_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.txt')]
    if not log_files:
        return None
    return max(log_files, key=os.path.getctime)

def process_log_file(file_path):
    global last_position, powerup_counter, quick_revive_counter, player_down_counter, cycle_count
    global current_round_value, dog_round_flag

    with open(file_path, 'r', encoding='utf-8') as file:
        file.seek(last_position)
        lines = file.readlines()  # Read all lines at once

        for i in range(len(lines)):
            line = lines[i]

            # Check for round number update
            if "Received update for round_number, value:" in line:
                round_value_match = re.search(r'value: (\d+)', line)
                if round_value_match:
                    current_round_value = int(round_value_match.group(1))
                    if current_round_value > len(round_info):  # Prevent out-of-range errors
                        continue  # Skip further processing for this round value

                    # Get the corresponding extra information from round_info
                    extra_info = round_info[current_round_value - 1] if current_round_value <= len(round_info) else ""

                    # Check if it’s a dog round
                    if i + 1 < len(lines) and 'VMNotifcationReceived: "dog_round_starting", Value: 1' in lines[i + 1]:
                        write_output(f"/me Round {current_round_value} (dogs) {extra_info}")
                        dog_round_flag = False  # Reset flag after processing
                    else:
                        write_output(f"/me Round {current_round_value} - {extra_info}")
                        break  # Ensure it doesn't process the same line twice in the current loop

            elif 'VMNotifcationReceived: "dog_round_starting", Value: 1' in line:
                dog_round_flag = True
                continue

            # Process other lines (same as your original logic)
            if "Map change detected! New map:" in line:
                map_name_match = re.search(r'\(([^)]+)\)', line)
                if map_name_match:
                    map_name = map_name_match.group(1)
                    write_output(f"/me {map_name}")

            elif "Map restart detected!" in line:
                reset_counters()
                write_output("/me MAP RESTARTED")

            elif 'VMNotifcationReceived: "powerup_grabbed"' in line:
                process_powerup_grabbed()
            
            elif 'Got chat message: "!dropmissed"' in line:
                write_output("/me DROP MISSED")
                process_powerup_grabbed()
         
            elif ":!downs" in line:
                if down_rounds:
                    rounds_message = " ".join(f"[{round}]" for round in down_rounds)
                    write_output(f"/me Downs: {player_down_counter} | {rounds_message}")
                    break  # Ensure it doesn't process the same line twice in the current loop
                else:
                    write_output("/me Downs: 0")
                    break  # Ensure it doesn't process the same line twice in the current loop
         
            # Door-opening events
            elif 'VMNotifcationReceived: "center_building_upstairs_buy"' in line or \
                 'VMNotifcationReceived: "outside_east_zone", Value:' in line or \
                 'VMNotifcationReceived: "outside_west_zone", Value:' in line or \
                 'VMNotifcationReceived: "north_downstairs_zone", Value:' in line or \
                 'VMNotifcationReceived: "junk purchased", Value:' in line or \
                 'VMNotifcationReceived: "airlock_bridge_zone", Value:' in line or \
                 'VMNotifcationReceived: "hallway3_level1", Value:' in line or \
                 'VMNotifcationReceived: "vip_zone", Value: 1' in line or \
                 'VMNotifcationReceived: "crematorium_zone", Value:' in line or \
                 'VMNotifcationReceived: "upstairs_zone", Value:' in line or \
                 'VMNotifcationReceived: "box_zone", Value:' in line:
                write_output("/me You OPENED the F#@%!NG door!!")

            elif 'Black Ops exited!' in line:
                write_output("/me GAME CLOSED")

            elif 'Black Ops successfully hooked!' in line:
                write_output("/me GAME STARTED")

            elif 'VMNotifcationReceived: "end_game"' in line:
                if current_round_value is not None:
                    # Track the current round as the death round
                    death_rounds.append(current_round_value)

                # Keep only the last 5 games in the list
                if len(death_rounds) > 5:
                    death_rounds.pop(0)  # Remove the oldest entry if we exceed 5
            
                # Keep the original behavior of outputting the game over round
                write_output(f"/me GAME OVER ROUND {current_round_value}")
            
            elif ":!last" in line:
                if death_rounds:
                    death_rounds_message = ", ".join(str(round) for round in death_rounds)
                    write_output(f"/me LAST 5 GAMES: {death_rounds_message}")
                else:
                    write_output("/me NO PREVIOUS GAMES YET")


            elif 'Received PlayerCmd update for event "giveweapon" for player #0:' in line:
                if '"m14_zm"' in line:
                    write_output("/me Player bought M14")
                elif '"rottweil72_zm"' in line:
                    write_output("/me Player bought Olympia")
                elif '"zombie_m1carbine"' in line:
                    write_output("/me Player bought M1 Carbine")
                elif '"zombie_kar98k"' in line:
                    write_output("/me Player bought Kar98K")
                elif '"zombie_m1garand"' in line:
                    write_output("/me Player bought M1 Garand")
                elif '"zombie_gewehr43"' in line:
                    write_output("/me Player bought Gewher 43")
                elif '"zombie_type99_rifle"' in line:
                    write_output("/me Player bought Arisaka")
                    
            elif 'Received PlayerCmd update for event "giveweapon" for player #1:' in line:
                if '"m14_zm"' in line:
                    write_output("/me Player 2 bought M14")
                elif '"rottweil72_zm"' in line:
                    write_output("/me Player 2 bought Olympia")
                elif '"zombie_m1carbine"' in line:
                    write_output("/me Player 2 bought M1 Carbine")
                elif '"zombie_kar98k"' in line:
                    write_output("/me Player 2 bought Kar98K")
                elif '"zombie_m1garand"' in line:
                    write_output("/me Player 2 bought M1 Garand")
                elif '"zombie_gewehr43"' in line:
                    write_output("/me Player 2 bought Gewher-43")
                elif '"zombie_type99_rifle"' in line:
                    write_output("/me Player 2 bought Arisaka")
            
            elif 'Received PlayerCmd update for event "giveweapon" for player #2:' in line:
                if '"m14_zm"' in line:
                    write_output("/me Player 3 bought M14")
                elif '"rottweil72_zm"' in line:
                    write_output("/me Player 3 bought Olympia")
                elif '"zombie_m1carbine"' in line:
                    write_output("/me Player 3 bought M1 Carbine")
                elif '"zombie_kar98k"' in line:
                    write_output("/me Player 3 bought Kar98K")
                elif '"zombie_m1garand"' in line:
                    write_output("/me Player 3 bought M1 Garand")
                elif '"zombie_gewehr43"' in line:
                    write_output("/me Player 3 bought Gewher-43")
                elif '"zombie_type99_rifle"' in line:
                    write_output("/me Player 3 bought Arisaka")
                    
            elif 'Received PlayerCmd update for event "giveweapon" for player #3:' in line:
                if '"m14_zm"' in line:
                    write_output("/me Player 4 bought M14")
                elif '"rottweil72_zm"' in line:
                    write_output("/me Player 4 bought Olympia")
                elif '"zombie_m1carbine"' in line:
                    write_output("/me Player 4 bought M1 Carbine")
                elif '"zombie_kar98k"' in line:
                    write_output("/me Player 4 bought Kar98K")
                elif '"zombie_m1garand"' in line:
                    write_output("/me Player 4 bought M1 Garand")
                elif '"zombie_gewehr43"' in line:
                    write_output("/me Player 4 bought Gewher-43")
                elif '"zombie_type99_rifle"' in line:
                    write_output("/me Player 4 bought Arisaka")

            elif 'Received PlayerCmd update for event "setperk" for player #0: "specialty_quickrevive"' in line:
                process_quick_revive()

            elif 'Received PlayerCmd update for event "unsetperk" for player #0: "specialty_quickrevive"' in line:
                process_player_down()

        # Update last position in the file
        last_position = file.tell()

def write_output(content):
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(content + '\n')

def reset_counters():
    global powerup_counter, quick_revive_counter, player_down_counter, cycle_count, dog_round_flag, current_round_value, down_rounds
    powerup_counter = 0
    quick_revive_counter = 0
    player_down_counter = 0
    cycle_count = 1
    dog_round_flag = False
    current_round_value = None
    down_rounds = []

def process_powerup_grabbed():
    global powerup_counter, cycle_count
    powerup_counter += 1
    if powerup_counter % 4 == 0:
        message = f"/me {ordinal(cycle_count)} DROP CYCLE"
        cycle_count += 1
        powerup_counter = 0
    else:
        cycle_position = powerup_counter % 4
        message = f"/me DROP {cycle_position}/4 CYCLE: {cycle_count}"
    write_output(message)

def process_quick_revive():
    global quick_revive_counter
    quick_revive_counter += 1
    message = f"/me BOUGHT QUICK REVIVE ({quick_revive_counter})"
    write_output(message)
    
def process_player_down():
    global player_down_counter, down_rounds, current_round_value
    player_down_counter += 1
    if current_round_value is not None:
        down_rounds.append(current_round_value)  # Track the round of the down
    message = f"/me DOWNED ({player_down_counter})"
    write_output(message)
    
    
    

def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[((n//10%10!=1)*(n%10<4)*n%10)::4])

# Main loop to continuously check the log file
while True:
    newest_file = get_newest_log_file(log_dir)
    if newest_file:
        process_log_file(newest_file)
    time.sleep(0.1)  # Check every 100 milliseconds
