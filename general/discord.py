import asyncio
import threading

from discord.ext import commands
import discord
from django.conf import settings

# Replace with your actual bot token
TOKEN = settings.DISCORD_BOT_TOKEN

# Replace with the ID of the channel where you want to send the message
CHANNEL_ID = settings.DISCORD_CHANNEL_ID

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

class MyDiscordBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.token = settings.DISCORD_BOT_TOKEN
        super().__init__(*args, **kwargs, intents=intents)
        self.message_id = None
        self.ready = False  # New attribute to track bot's readiness
        self.event = threading.Event()  # Create an event for synchronization

    async def on_ready(self):
        print(f'We have logged in as {self.user}')
        self.ready = True
        self.event.set()  # Signal that the bot is ready

    async def send_message(self, message):
        # Wait for the bot to be ready
        while not self.ready:
            await asyncio.sleep(0.1)

        channel = self.get_channel(CHANNEL_ID)

        if channel is None:
            print(f"Channel with ID {CHANNEL_ID} not found.")
            return

        msg = await channel.send(message)
        self.message_id = msg.id

    async def get_reaction_users(self, message_id):
        """
        Retrieves the IDs of users who reacted to a specific message.

        Args:
            message_id: The ID of the message to check reactions for.

        Returns:
            A list of user IDs who reacted to the message.
        """
        try:
            channel = self.get_channel(CHANNEL_ID)
            message = await channel.fetch_message(message_id)

            user_ids = []
            for reaction in message.reactions:
                async for user in reaction.users():
                    if not user.bot:  # Exclude bot reactions
                        user_ids.append(user.id)
            return user_ids

        except discord.NotFound:
            print(f"Message with ID {message_id} not found.")
            return []
        except discord.Forbidden:
            print("Forbidden: Unable to access message reactions.")
            return []

    @commands.command()
    async def get_reactions(self, ctx, message_id: int):
        try:
            user_ids = await self.get_reaction_users(message_id)
            await ctx.send(f"Users who reacted: {user_ids}")
        except ValueError:
            await ctx.send("Invalid message ID.")

# ... (rest of your Django project code)

# Create an instance of your bot
#bot = MyDiscordBot(command_prefix='$')

# Run the bot in a separate thread or process
# This is crucial to avoid blocking your Django server
# ... (Implement threading or multiprocessing here)

# Example using threading
#import threading

#def run_discord_bot():
#    bot.run(TOKEN)

#thread = threading.Thread(target=run_discord_bot)
#thread.start()