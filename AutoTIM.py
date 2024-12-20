import os
import sys
import asyncio
import time
from twitchio.ext import commands
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from colorama import init, Fore

# Twitch Bot Configuration
TOKEN_1 = 'TOKEN'

CHANNEL = 'CHANNEL'

# Path to the log file
LOG_FILE_PATH = r'C:\Program Files (x86)\Steam\steamapps\common\Call of Duty Black Ops\logs\output\AHK_TIM_Logs.txt'

# Initialize colorama
init(autoreset=True)

class Bot(commands.Bot):
    def __init__(self, token):
        super().__init__(token=token, prefix='!', initial_channels=[CHANNEL])
        self.current_token = token
        self.paused = False  # Pause flag for message control
        self.recent_messages = {}  # Cache to track recently sent messages

    async def event_ready(self):
        """Override to customize the login output"""
        print(Fore.GREEN + f'Logged in as | {self.nick}')  # Print login in green color
        print(Fore.WHITE + "Log: " + Fore.LIGHTBLACK_EX + LOG_FILE_PATH)  # "Log:" in white, path in grey

    async def send_message(self, message):
        """Send a message to Twitch chat only if bot is not paused and message is not a duplicate."""
        current_time = time.time()

        # Check if the message was recently sent (within 5 seconds)
        if message in self.recent_messages:
            last_sent_time = self.recent_messages[message]
            if current_time - last_sent_time < 5:
                return

        # Send the message if not paused and not a duplicate
        if not self.paused:
            channel = self.get_channel(CHANNEL)
            if channel:
                await channel.send(message)
                print(Fore.MAGENTA + message + Fore.WHITE + " sent to chat")  # Purple message + white "sent to chat"
                self.recent_messages[message] = current_time  # Update the message timestamp
            else:
                print(Fore.RED + "Channel not found. Message not sent.")
        else:
            print(Fore.RED + "Message not sent.")

        # Clean up old messages from the cache (optional, for long-running sessions)
        self.recent_messages = {msg: ts for msg, ts in self.recent_messages.items() if current_time - ts < 5}

    # Command to pause the bot (restricted to broadcaster and moderators)
    @commands.command(name='pause')
    async def pause_command(self, ctx):
        if ctx.author.is_broadcaster or ctx.author.is_mod:  # Allow broadcaster and moderators
            self.paused = True
            await ctx.send("Bot paused.")
            print(Fore.RED + "Bot is paused.")

    # Command to unpause the bot (restricted to broadcaster and moderators)
    @commands.command(name='unpause')
    async def unpause_command(self, ctx):
        if ctx.author.is_broadcaster or ctx.author.is_mod:  # Allow broadcaster and moderators
            self.paused = False
            await ctx.send("Bot unpaused.")
            print(Fore.GREEN + "Bot unpaused.")

class LogFileHandler(FileSystemEventHandler):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.last_position = self.get_initial_position()

    def get_initial_position(self):
        """Set initial position to the end of the file to skip existing content."""
        try:
            with open(LOG_FILE_PATH, 'r') as f:
                return f.seek(0, os.SEEK_END)
        except FileNotFoundError:
            return 0

    def on_modified(self, event):
        if event.src_path == LOG_FILE_PATH:
            print(Fore.YELLOW + "File modified")  # Orange color (Yellow is closest in colorama)

            try:
                with open(LOG_FILE_PATH, 'r') as f:
                    f.seek(self.last_position)
                    new_lines = f.readlines()

                    if new_lines:
                        for line in new_lines:
                            line = line.strip()
                            if line:
                                # Just send the new line as a message without token switching
                                asyncio.run_coroutine_threadsafe(self.bot.send_message(line), self.bot.loop)

                        self.last_position = f.tell()
                    else:
                        print("No new lines to read.")

            except PermissionError:
                print(Fore.RED + f"Permission denied for {LOG_FILE_PATH}. Check file permissions.")
            except Exception as e:
                print(Fore.RED + f"Error reading file: {e}")

# Initialize and Run the Bot and Observer
if __name__ == '__main__':
    # Start with the provided token
    new_token = sys.argv[1] if len(sys.argv) > 1 else TOKEN_1
    bot = Bot(new_token)  # Start with TOKEN_1
    event_handler = LogFileHandler(bot)
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(LOG_FILE_PATH), recursive=False)

    # Start the file observer
    observer.start()
    try:
        # Run the bot
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
