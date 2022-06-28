"""Message templates for the bot"""
import discord

async def error(ctx, msg):
    """Display an error message"""
    message = discord.Embed(title="Error", color=0xFF0000, description=msg)
    await ctx.send(embed=message)

async def success(ctx, msg):
    """Display a success message"""
    message = discord.Embed(title="Success", color=0x00FF00, description=msg)
    await ctx.send(embed=message)

async def info(ctx, msg):
    """Misc message"""
    message = discord.Embed(title="Info", color=0x00FFA2, description=msg)
    await ctx.send(embed=message)

help_message = discord.Embed(title="Commands", color=0x00FFA2, description="""
    staff only commands:
    t!register <team-role-name> <pingplayer> (creates a new team role, the person you ping becomes leader)
    t!delete <team-role-name> (deletes the team)
    t!rosterlock (toggles roster lock)

    moderation commands:
    t!kick <pingplayer> (kick a member)
    t!ban <pingplayer> (ban a member)
    t!mute <pingplayer> (mute a member)
    t!unmute <pingplayer> (unmute a member)

    team leader/cl only commands:
    t!recruit <pingplayer> (asks a player to join, they can confirm or reject.)
    t!coleader <pingplayer> (appoint a co leader)
    t!boot <pingplayer> (remove a player from the team)
    t!tag <clan-tag> (set the clan tag)

    anyone commands:
    t!help (shows this message)
    t!ping (get bot latency)
    t!info <pingplayer> (get info about a member)
    t!list <team-role-name> (list all members of a team)
    t!confirm (confirm the recruitment)
    t!reject (reject the recruitment)
    t!leave (leave the team)
""")
