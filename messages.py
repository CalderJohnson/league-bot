"""Message templates for the bot"""
import discord

async def error(ctx, msg):
    """Display an error message"""
    message = discord.Embed(title="Error", color=0xFF0000, description=msg)
    await ctx.channel.send(embed=message)

async def success(ctx, msg):
    """Display a success message"""
    message = discord.Embed(title="Success", color=0x00FF00, description=msg)
    await ctx.channel.send(embed=message)

async def info(ctx, msg):
    """Misc message"""
    message = discord.Embed(title="Info", color=0x00FFA2, description=msg)
    await ctx.channel.send(embed=message)

help_message = discord.Embed(title="Commands", color=0x00FFA2, description="""
    staff only commands:
    t!register <team-role-name> <pingplayer> (creates a new team role and registers it in the bot, the player you ping will get the role and the leader role)
    t!delete <team-role-name> (deletes the team)
    t!rosterlock (toggles roster lock)

    team leader/cl only commands:
    t!recruit <pingplayer> (asks a player to join, they can confirm or reject. does not work if your roster is full.)
    t!coleader <pingplayer> (appoint a co leader)
    t!kick <pingplayer> (remove a player from the team)
    t!tag <clan-tag> (remove everyone on the teams nicknames and set the tag)

    anyone commands:
    t!help (shows these commands)
    t!list <team-role-name> (list all members of a team)
    t!confirm (if a recruit is pending for them, it will add them to that team)
    t!reject (if a recruit is pending for them, it will delete that pending recruit)
    t!leave (leaves your current team)
""")
