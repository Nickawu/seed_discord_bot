import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import seedbot_utils
import nickname_utils

# https://www.reddit.com/r/discordapp/comments/7ir4ag/discordpy_stop_bot_from_running_in_command_prompt/
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SERVERTOK = os.getenv('SERVER_ID')

nicks = nickname_utils.loadnicks()
print(nicks)
#we could update sheets from the dict file, the main col with names could be dict keys... (only when we add main though)
# client = discord.Client()

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    for server in bot.guilds:
        if server == SERVERTOK:
            break
    print(f'{bot.user.name} is connected to the following guild:\n'f'{server.name}(id: {server.id})')
    # await bot.logout()

@bot.command(name='setmain', help='Sets your main\'s name')
async def setmainname(ctx, mainname):
    if nickname_utils.addmaintonick(nicks,mainname):
        sender = "successfully added %s as a main name!" % mainname
        await ctx.send(sender)
        await ctx.send(nickname_utils.getnicks(nicks,mainname))
    else:
        await ctx.send("failed to add %s as a main name, are you sure it wasn't added already?")


bot.run(TOKEN)


# @client.event
# async def on_ready():
#     print(f'{client.user} has connected to Discord!')
#     for server in client.guilds:
#         if server == SERVERTOK:
#             break
#     print(f'{client.user} is connected to the following guild:\n'f'{server.name}(id: {server.id})')
#     await client.logout()

# @client.event
# async def on_member_join(member):
#     await member.create_dm()
#     await member.dm_channel.send(f'Hi {member.name}, welcome to Seed discord, have a pancake')
#     await member.dm_channel.send('please dm me like this: "!setmain your-main-name-here"')

# @client.event
# async def on_message(message: discord.Message):
#     if message.guild is None and not message.author.bot:
        

# client.run(TOKEN)








# nickname_utils.removenick(nicks,"H0pe", "testadd")
# print(nicks)
# print(nickname_utils.getnicks(nicks,"Owenry Magruder"))
# nickname_utils.addmaintonick(nicks,"Erinbella10")
# print(nickname_utils.getnicks(nicks,"Erinbella10"))
# nickname_utils.addnick(nicks,"Erinbella10","maybealt")
# print(nickname_utils.getnicks(nicks,"Erinbella10"))
# if(nickname_utils.addnick(nicks,"shouldntwork", "testadd2")):
    # print("added %s as a nickname for %s", "H0pe", "testadd")
# else:
    # print("did you spell your main name correctly? add your main name to nickname file if you see this...")


#write dict to file here, after bot stops running...