import discord
import os
from src.discord_table import Discord_Table
from dotenv import load_dotenv
load_dotenv()

class Discord_bot(discord.Client):
    async def on_ready(self):
        # table.load_players_balance()
        print(f'We have logged in as {client.user}')

    async def on_message(self, message):
        if message.author == client.user:
            return


        await table.handel_message(message)

table = Discord_Table()
client = Discord_bot()
def main():
    client.run(os.getenv('TOKEN'))


if __name__ == "__main__":
    main()


