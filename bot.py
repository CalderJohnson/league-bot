"""Command handlers"""
import json
import discord
from discord.ext.commands import Bot
from discord.ext import commands
import messages

#constants

TOKEN = "token"
PREFIX = "t!"
INTENTS = discord.Intents.all()
MAX_ROSTER_SIZE = 15

BOT = Bot(command_prefix=PREFIX, intents=INTENTS)
BOT.remove_command("help")

pending_recruitments : dict = {}

@BOT.event
async def on_ready():
    """Triggers when the bot is running"""
    activity = discord.Game(name="t!help", type=2)
    await BOT.change_presence(status=discord.Status.online, activity=activity)
    with open ("teams.json", encoding="utf-8", mode="r") as teamsfile:
        teamslist = json.load(teamsfile)
        global pending_recruitments
        pending_recruitments = {team: [] for team in teamslist["teams"]}
    print("Bot online")

#staff only commands

@BOT.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def register(ctx, team, user):
    """Create a new team and appoint the leader"""
    with open("teams.json", encoding="utf-8", mode="r+") as teamsfile:
        teamslist = json.load(teamsfile)
        if team not in teamslist["teams"]:
            teamslist["teams"].append(team)
        else:
            await messages.error(ctx, "Teams already exists")
            return
        teamsfile.seek(0)
        json.dump(teamslist, teamsfile)
        teamsfile.truncate()
    await ctx.guild.create_role(name=team)
    teamrole = discord.utils.get(ctx.guild.roles, name=team)
    leaderrole = discord.utils.get(ctx.guild.roles, name="Team Leader")
    user_object = ctx.guild.get_member(int(user[2:-1]))
    await user_object.add_roles(teamrole)
    await user_object.add_roles(leaderrole)
    await messages.success(ctx, "Team created successfully")

@BOT.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def delete(ctx, team):
    """Delete a team"""
    with open("teams.json", encoding="utf-8", mode="r+") as teamsfile:
        teamslist = json.load(teamsfile)
        try:
            teamslist["teams"].remove(team)
        except ValueError:
            await messages.error(ctx, "Team not found")
            return
        teamsfile.seek(0)
        json.dump(teamslist, teamsfile)
        teamsfile.truncate()
    role_object = discord.utils.get(ctx.message.guild.roles, name=team)
    await role_object.delete()
    await messages.success(ctx, "Team deleted successfully")

@BOT.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def rosterlock(ctx):
    """Toggle roster lock"""
    with open("teams.json", encoding="utf-8", mode="r+") as teamsfile:
        teamslist = json.load(teamsfile)
        if teamslist["rosterlock"]: 
            teamslist["rosterlock"] = False
        else:
            teamslist["rosterlock"] = True
        teamsfile.seek(0)
        json.dump(teamslist, teamsfile)
        teamsfile.truncate()
    await messages.info(ctx, "Roster lock toggled")

#tl/cl only commands

@BOT.command(pass_context=True)
@commands.has_any_role("Team Leader")
async def coleader(ctx, user):
    """Appoint a co leader"""
    co_role = discord.utils.get(ctx.guild.roles, name="Team Co-Leader")
    user_object = ctx.guild.get_member(int(user[2:-1]))
    with open("teams.json", encoding="utf-8", mode="r+") as teamsfile:
        teamslist = json.load(teamsfile)
        for role in ctx.message.author.roles:
            if str(role) in teamslist["teams"] and role in [r for r in user_object.roles]:
                await user_object.add_roles(co_role)
                await messages.success(ctx, "Co appointed successfully")
                return
    await messages.error(ctx, "Could not find that user, or they weren't on your team")

@BOT.command(pass_context=True)
@commands.has_any_role("Team Leader", "Team Co-Leader")
async def recruit(ctx, user):
    """Recruit a player"""
    user_object = ctx.guild.get_member(int(user[2:-1]))
    with open("teams.json", encoding="utf-8", mode="r+") as teamsfile:
        teamslist = json.load(teamsfile)
        if teamslist["rosterlock"]:
            await messages.error(ctx, "Roster lock is enabled")
            return
        for role in user_object.roles:
            if str(role) in teamslist["teams"]:
                await messages.error(ctx, "That player is already on a team")
                return
        for role in ctx.message.author.roles:
            if str(role) in teamslist["teams"]:
                if len(role.members) >= MAX_ROSTER_SIZE:
                    await messages.error(ctx, "Roster is full")
                    return
                pending_recruitments[str(role)] = []
                pending_recruitments[str(role)].append(int(user[2:-1]))
                await ctx.channel.send(f"{user} type t!confirm if you wish to join the team, and t!reject if you do not")
                await messages.info(ctx, "Recruitment pending")
                return
    await messages.error(ctx, "Something went wrong")

@BOT.command(pass_context=True)
@commands.has_any_role("Team Leader", "Team Co-Leader")
async def kick(ctx, user):
    """Remove a player from your team"""
    user_object = ctx.guild.get_member(int(user[2:-1]))
    if not user_object:
        await messages.error(ctx, "User not found")
        return
    with open("teams.json", encoding="utf-8", mode="r+") as teamsfile:
        teamslist = json.load(teamsfile)
        for role in user_object.roles:
            if str(role) == "Team Leader":
                await messages.error(ctx, "Can't kick the team leader")
                return
        for role in user_object.roles:
            if str(role) in teamslist["teams"]:
                if role in ctx.author.roles:
                    await user_object.remove_roles(role)
                    await messages.success(ctx, f"Successfully kicked {user}")
                    return
                await messages.error(ctx, "Can't kick players that aren't on your team")
                return
    await messages.error(ctx, f"Couldn't kick {user}, not on your team")

@BOT.command(pass_context=True)
@commands.has_any_role("Team Leader", "Team Co-Leader")
async def tag(ctx, clantag):
    """Set a clans tag"""
    with open("teams.json", encoding="utf-8", mode="r+") as teamsfile:
        teamslist = json.load(teamsfile)
        for role in ctx.author.roles:
            if str(role) in teamslist["teams"]:
                for team_member in role.members:
                    try:
                        await team_member.edit(nick=(clantag + " " + team_member.name))
                    except discord.errors.Forbidden:
                        await messages.error(ctx, f"Couldn't change {team_member.name}'s nickname, lacking permissions")
                await messages.success(ctx, "Clan tag updated")
                return
    await messages.error(ctx, "Something went wrong")

#anyone commands

@BOT.command(pass_context=True)
async def help(ctx):
    """List all commands available"""
    await ctx.channel.send(embed=messages.help_message)

@BOT.command(pass_context=True)
async def list(ctx, team):
    """List all team members"""
    members = discord.utils.get(ctx.guild.roles, name=team).members
    message = str(len(members)) + " members:\n"
    for m in members:
        message += m.name + "#" + m.discriminator + "\n"
    if not members:
        await messages.error(ctx, "Team not found, please write the name out exactly")
    await messages.info(ctx, message)

@BOT.command(pass_context=True)
async def confirm(ctx):
    """Confirm a pending recruit"""
    user_object = ctx.author
    for team, players in pending_recruitments.items():
        if user_object.id in players:
            teamrole = discord.utils.get(ctx.guild.roles, name=team)
            await user_object.add_roles(teamrole)
            pending_recruitments[team].remove(user_object.id)
            await messages.success(ctx, f"Confirmed, you are now on {team}")
            return
    await messages.error(ctx, "No pending recruitment")

@BOT.command(pass_context=True)
async def reject(ctx):
    """Reject a pending recruit"""
    user_object = ctx.author
    for team, players in pending_recruitments.items():
        if user_object.id in players:
            pending_recruitments[team].remove(user_object.id)
            await messages.success(ctx, f"Recruitment rejected for {team}")
            return
    await messages.error(ctx, "No pending recruitment")

@BOT.command(pass_context=True)
async def leave(ctx):
    """Leave your current team"""
    with open("teams.json", mode="r+", encoding="utf-8") as teamsfile:
        teamslist = json.load(teamsfile)
        for role in ctx.message.author.roles:
            if str(role) in teamslist["teams"]:
                await ctx.author.remove_roles(role)
                await messages.success(ctx, "Left the team")
                return
    await messages.error(ctx, "You're not on a team")

BOT.run(TOKEN)
