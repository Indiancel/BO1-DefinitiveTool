import os
import sys
import asyncio
from twitchio.ext import commands
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Twitch Bot Configuration
TOKEN_1 = 'oauth:'  # Token for Twitch bot

CHANNEL = 'CHANNEL'

# Path to the log file
LOG_FILE_PATH = r'C:\Program Files (x86)\Steam\steamapps\common\Call of Duty Black Ops\logs\output\AHK_TIM_Logs.txt'



class Bot(commands.Bot):
    def __init__(self, token):
        super().__init__(token=token, prefix='!', initial_channels=[CHANNEL])
        self.current_token = token
        self.paused = False  # Pause flag for message control

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')

    async def send_message(self, message):
        """Send a message to Twitch chat only if bot is not paused."""
        if not self.paused:
            channel = self.get_channel(CHANNEL)
            if channel:
                await channel.send(message)
                print(f"Message sent to chat: {message}")
        else:
            print("Bot is paused. Message not sent.")

    async def restart_bot(self, new_token):
        """Restart the bot with a new token."""
        print(f"Restarting bot with new token: {new_token}")
        os.execv(sys.executable, ['python'] + sys.argv + [new_token])  # Restart the script with the new token

    # Command to pause the bot (restricted to broadcaster and moderators)
    @commands.command(name='pause')
    async def pause_command(self, ctx):
        if ctx.author.is_broadcaster or ctx.author.is_mod:  # Allow broadcaster and moderators
            self.paused = True
            await ctx.send("Bot paused.")
        else:
            print("Only the broadcaster or a moderator can use this command.")

    # Command to unpause the bot (restricted to broadcaster and moderators)
    @commands.command(name='unpause')
    async def unpause_command(self, ctx):
        if ctx.author.is_broadcaster or ctx.author.is_mod:  # Allow broadcaster and moderators
            self.paused = False
            await ctx.send("Bot unpaused.")
        else:
            print("Only the broadcaster or a moderator can use this command.")

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

    async def check_and_change_token(self, line):
        if "/me Player bought Gewher 43" in line:
            if self.bot.current_token == TOKEN_2:
                await self.bot.send_message("/me Juggside")
                await self.bot.restart_bot(TOKEN_1)

        if "/me Player bought M1 Garand" in line:
            if self.bot.current_token == TOKEN_1:
                await self.bot.send_message("/me Quickside")
                await self.bot.restart_bot(TOKEN_2)
     
        if '/me "Five"' in line:
            if self.bot.current_token == TOKEN_1:
                await self.bot.send_message("/me Five")
                await self.bot.restart_bot(TOKEN_3)
    
        if "/me Shi No Numa" in line:
            if self.bot.current_token == TOKEN_1:
                await self.bot.send_message("/me Shi No Numa")
                await self.bot.restart_bot(TOKEN_4)
     
        if "/me Shangri-La" in line:
            if self.bot.current_token == TOKEN_1:
                await self.bot.send_message("/me Shangri-La")
                await self.bot.restart_bot(TOKEN_5)

    def on_modified(self, event):
        if event.src_path == LOG_FILE_PATH:
            print(f"File modified: {event.src_path}")

            try:
                with open(LOG_FILE_PATH, 'r') as f:
                    f.seek(self.last_position)
                    new_lines = f.readlines()

                    if new_lines:
                        for line in new_lines:
                            line = line.strip()
                            if line:
                                print(f"Processing line: {line}")
                                
                                # Check for token changes and send the message
                                asyncio.run_coroutine_threadsafe(self.check_and_change_token(line), self.bot.loop)
                                asyncio.run_coroutine_threadsafe(self.bot.send_message(line), self.bot.loop)

                        self.last_position = f.tell()
                    else:
                        print("No new lines to read.")

            except PermissionError:
                print(f"Permission denied for {LOG_FILE_PATH}. Check file permissions.")
            except Exception as e:
                print(f"Error reading file: {e}")

# Initialize and Run the Bot and Observer
if __name__ == '__main__':
    # Check if a new token is passed as a command-line argument
    new_token = sys.argv[1] if len(sys.argv) > 1 else TOKEN_1
    bot = Bot(new_token)  # Start with the provided token
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
