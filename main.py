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

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    for server in bot.guilds:
        if server == SERVERTOK:
            break
    print(f'{bot.user.name} is connected to the following guild:\n'f'{server.name}(id: {server.id})')
    # await bot.logout()

@bot.command(name='setmain', help='<main-name>')
async def setmainname(ctx):
    msg = ctx.message.content
    msg = msg[9:]
    if ctx.message.author.display_name in nicks.keys():
        del nicks[ctx.message.author.display_name]
        nickname_utils.writenicks(nicks)
    if msg in nicks.keys():
        await ctx.send("you cant have the same main as someone else...")
    if nickname_utils.addmaintonick(nicks,msg):
        await ctx.send("successfully added %s as a main name!" % msg)
        await ctx.message.author.edit(nick=msg)
    else:
        await ctx.send("failed to add %s as a main name, are you sure it wasn't added already?" % msg)

@bot.command(name='addnickname', help='<nickname-to-add>')
async def addnickname(ctx, nickname):
    if nickname_utils.addnick(nicks, ctx.message.author.display_name, nickname):
        await ctx.send("successfully added nickname %s for main %s" % (nickname, ctx.message.author.display_name))
        await ctx.send("your nicknames: %s" % nickname_utils.getnicks(nicks, ctx.message.author.display_name))
    else:
        await ctx.send("failed to add nickname %s, did you setmain? is your nickname the same as someone else's?" % nickname)

@bot.command(name='removenickname', help='<nickname-to-remove>')
async def removenickname(ctx, nickname):
    if nickname_utils.removenick(nicks, ctx.message.author.display_name, nickname):
        await ctx.send("successfully removed nickname %s for main %s" % (nickname, ctx.message.author.display_name))
        await ctx.send("your nicknames: %s" % nickname_utils.getnicks(nicks,ctx.message.author.display_name))
    else:
        await ctx.send("failed to remove nickname %s for main %s, does main exist? does the nickname exist currently?" % (nickname, ctx.message.author.display_name))
        await ctx.send("current nicknames for main %s: %s" % (ctx.message.author.display_name, nickname_utils.getnicks(nicks,ctx.message.author.display_name)))

@bot.command(name='getnicknames',help='<someones-main-name>')
async def getnickname(ctx, mainname):
    msg = ctx.message.content
    msg = msg[14:]
    await ctx.send("nicknames registered to main %s: %s" % (msg, nickname_utils.getnicks(nicks,msg)))

@bot.command(name='attend', help='<level/star or raid name> <people>')
async def attends(ctx):
    added = seedbot_utils.add_points(nicks, ctx.message.content) #do we need await?
    if added == False:
        await ctx.send("did you enter the level/star or raid name correctly? I don't think so...")
    else:
        if len(added) == 0:
            await ctx.send("success!")
        else:
            await ctx.send("ERROR: did not add points for the following --> %s" % added)
            await ctx.send("did you spell their nickname right? does it exist?")
        #maybe print the amount of kills each person has now...

@bot.command(name='removeattend', help='<level/star or raid name>')
async def removeattends(ctx, ids):
    retval = seedbot_utils.remove_points(ctx.message.author.display_name,ids)
    if retval == False:
        await ctx.send("did you setmain? do you have more than 0 points? did you do <level/star or raid name> right?")
    else:
        await ctx.send("success!")


@bot.command(name='getmypoints', help='**no args to put in**')
async def mypoints(ctx):
    ret = seedbot_utils.getallpoints(ctx.message.author.display_name)
    if ret == False:
        await ctx.send("ERROR: your main's name not found in spreadsheet... did you register?")
    else:
        await ctx.send(ret)

bot.run(TOKEN)

# @client.event
# async def on_member_join(member):
#     await member.create_dm()
#     await member.dm_channel.send(f'Hi {member.name}, welcome to Seed discord, have a pancake')
#     await member.dm_channel.send('please dm me like this: "!setmain your-main-name-here"')

#write dict to file here, after bot stops running...