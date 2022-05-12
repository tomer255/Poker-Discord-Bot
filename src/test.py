import discord
import os
from dotenv import load_dotenv
load_dotenv()

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message):
        print(message.content)
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'ping':
            await message.channel.send('pong')

intents = discord.Intents.default()
client = MyClient(intents=intents)
client.run(os.getenv('TOKEN'))