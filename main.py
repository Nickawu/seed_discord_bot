import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVERTOK = os.getenv('SERVER_ID')

client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    for server in client.guilds:
        if server == SERVERTOK:
            break
    print(f'{client.user} is connected to the following guild:\n'f'{server.name}(id: {server.id})')

client.run(TOKEN)