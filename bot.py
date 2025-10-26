import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Literal
import json

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

REPORT_EMOJI_ID = 1432054365862105099
REPORT_CHANNEL_ID = 1407034866226430063
REPORT_EMBED_EMOJI_ID = 1432059800258347049
UPVOTE_EMOJI_ID = 1432070542831255724
DOWNVOTE_EMOJI_ID = 1432070594551353364
STAR_EMOJI_ID = 1432070448245641346
ALLOWED_REACTION_CHANNELS = [1338311408156278844, 1397275881008791723, 1397276528873701448, 1407895335711408209]

case_counter = 1

@bot.event
async def on_ready():
    print(f'Bot is ready! Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Error syncing commands: {e}')

@bot.tree.command(name="echo", description="Send a message as the bot")
@app_commands.describe(
    content="The message content to send",
    format="Message format: embed, plain, or code",
    reply_to="Message ID to reply to (optional)",
    attachment_url="Attachment URL (optional)"
)
async def echo(
    interaction: discord.Interaction,
    content: str,
    format: Optional[Literal["embed", "plain", "code"]] = "plain",
    reply_to: Optional[str] = None,
    attachment_url: Optional[str] = None
):
    await interaction.response.defer(ephemeral=True)
    
    if not isinstance(interaction.channel, (discord.TextChannel, discord.Thread)):
        await interaction.followup.send("This command can only be used in text channels.", ephemeral=True)
        return
    
    try:
        target_message = None
        if reply_to:
            try:
                target_message = await interaction.channel.fetch_message(int(reply_to))
            except:
                await interaction.followup.send("Invalid message ID provided.", ephemeral=True)
                return
        
        if format == "embed":
            embed = discord.Embed(description=content, color=discord.Color.blue())
            if attachment_url:
                embed.set_image(url=attachment_url)
            
            if target_message:
                await target_message.reply(embed=embed)
            else:
                await interaction.channel.send(embed=embed)
        
        elif format == "code":
            message_content = f"```\n{content}\n```"
            if target_message:
                await target_message.reply(message_content)
            else:
                await interaction.channel.send(message_content)
        
        else:
            if target_message:
                await target_message.reply(content)
            else:
                await interaction.channel.send(content)
            
            if attachment_url:
                await interaction.channel.send(attachment_url)
        
        await interaction.followup.send("Message sent successfully!", ephemeral=True)
    
    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)

@bot.tree.command(name="masslock", description="Lock multiple channels at once")
@app_commands.describe(
    channels="Channels to lock (mention them separated by spaces, 2-10 channels)",
    timer="Auto-unlock timer in minutes (optional)"
)
async def masslock(
    interaction: discord.Interaction,
    channels: str,
    timer: Optional[int] = None
):
    await interaction.response.defer(ephemeral=True)
    
    if not interaction.guild:
        await interaction.followup.send("This command can only be used in a server.", ephemeral=True)
        return
    
    channel_mentions = [int(ch.strip('<#>')) for ch in channels.split() if ch.startswith('<#')]
    
    if len(channel_mentions) < 2:
        await interaction.followup.send("You must specify at least 2 channels to lock.", ephemeral=True)
        return
    
    if len(channel_mentions) > 10:
        await interaction.followup.send("You can only lock up to 10 channels at once.", ephemeral=True)
        return
    
    locked_channels = []
    
    for channel_id in channel_mentions:
        try:
            channel = interaction.guild.get_channel(channel_id)
            if channel and isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.ForumChannel)):
                await channel.set_permissions(interaction.guild.default_role, send_messages=False)
                locked_channels.append(channel.mention)
        except Exception as e:
            print(f"Error locking channel {channel_id}: {e}")
    
    if locked_channels:
        response = f"🔒 Successfully locked {len(locked_channels)} channel(s): {', '.join(locked_channels)}"
        if timer:
            response += f"\n⏰ Channels will auto-unlock in {timer} minute(s)."
            asyncio.create_task(auto_unlock_channels(channel_mentions, timer, interaction.guild))
        
        await interaction.followup.send(response, ephemeral=True)
    else:
        await interaction.followup.send("Failed to lock any channels.", ephemeral=True)

async def auto_unlock_channels(channel_ids, minutes, guild):
    await asyncio.sleep(minutes * 60)
    for channel_id in channel_ids:
        try:
            channel = guild.get_channel(channel_id)
            if channel:
                await channel.set_permissions(guild.default_role, send_messages=None)
        except Exception as e:
            print(f"Error auto-unlocking channel {channel_id}: {e}")

@bot.tree.command(name="massmute", description="Mute multiple members at once")
@app_commands.describe(
    members="Members to mute (mention them separated by spaces, 2-5 members)",
    timer="Auto-unmute timer in minutes (optional)",
    reason="Reason for muting (optional)"
)
async def massmute(
    interaction: discord.Interaction,
    members: str,
    timer: Optional[int] = None,
    reason: Optional[str] = "No reason provided"
):
    await interaction.response.defer(ephemeral=True)
    
    if not interaction.guild:
        await interaction.followup.send("This command can only be used in a server.", ephemeral=True)
        return
    
    member_mentions = []
    for mention in members.split():
        if mention.startswith('<@') and mention.endswith('>'):
            user_id = int(mention.strip('<@!>'))
            member = interaction.guild.get_member(user_id)
            if member:
                member_mentions.append(member)
    
    if len(member_mentions) < 2:
        await interaction.followup.send("You must specify at least 2 members to mute.", ephemeral=True)
        return
    
    if len(member_mentions) > 5:
        await interaction.followup.send("You can only mute up to 5 members at once.", ephemeral=True)
        return
    
    muted_members = []
    timeout_duration = timedelta(minutes=timer) if timer else timedelta(days=27)
    
    for member in member_mentions:
        try:
            await member.timeout(timeout_duration, reason=reason)
            muted_members.append(member.mention)
        except Exception as e:
            print(f"Error muting member {member.id}: {e}")
    
    if muted_members:
        response = f"🔇 Successfully muted {len(muted_members)} member(s): {', '.join(muted_members)}\nReason: {reason}"
        if timer:
            response += f"\n⏰ Members will auto-unmute in {timer} minute(s)."
        
        await interaction.followup.send(response, ephemeral=True)
    else:
        await interaction.followup.send("Failed to mute any members.", ephemeral=True)

@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.describe(member="The member to ban", reason="Reason for ban")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = "No reason provided"):
    await interaction.response.defer(ephemeral=True)
    try:
        await member.ban(reason=reason)
        await interaction.followup.send(f"✅ Banned {member.mention} - Reason: {reason}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to ban member: {str(e)}", ephemeral=True)

@bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.describe(member="The member to kick", reason="Reason for kick")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = "No reason provided"):
    await interaction.response.defer(ephemeral=True)
    try:
        await member.kick(reason=reason)
        await interaction.followup.send(f"✅ Kicked {member.mention} - Reason: {reason}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to kick member: {str(e)}", ephemeral=True)

@bot.tree.command(name="mute", description="Timeout a member")
@app_commands.describe(member="The member to mute", duration="Duration in minutes", reason="Reason for mute")
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int, reason: Optional[str] = "No reason provided"):
    await interaction.response.defer(ephemeral=True)
    try:
        await member.timeout(timedelta(minutes=duration), reason=reason)
        await interaction.followup.send(f"✅ Muted {member.mention} for {duration} minute(s) - Reason: {reason}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to mute member: {str(e)}", ephemeral=True)

@bot.tree.command(name="unmute", description="Remove timeout from a member")
@app_commands.describe(member="The member to unmute")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer(ephemeral=True)
    try:
        await member.timeout(None)
        await interaction.followup.send(f"✅ Unmuted {member.mention}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to unmute member: {str(e)}", ephemeral=True)

@bot.tree.command(name="warn", description="Warn a member")
@app_commands.describe(member="The member to warn", reason="Reason for warning")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    await interaction.response.defer(ephemeral=True)
    
    if not interaction.guild or not isinstance(interaction.channel, (discord.TextChannel, discord.Thread)):
        await interaction.followup.send("This command can only be used in a server text channel.", ephemeral=True)
        return
    
    try:
        embed = discord.Embed(
            title="⚠️ Warning Issued",
            description=f"{member.mention} has been warned.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
        embed.timestamp = datetime.utcnow()
        
        await interaction.channel.send(embed=embed)
        await interaction.followup.send(f"✅ Warned {member.mention}", ephemeral=True)
        
        try:
            await member.send(f"You have been warned in {interaction.guild.name} for: {reason}")
        except:
            pass
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to warn member: {str(e)}", ephemeral=True)

@bot.tree.command(name="purge", description="Delete multiple messages")
@app_commands.describe(amount="Number of messages to delete (1-100)")
async def purge(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    
    if not isinstance(interaction.channel, (discord.TextChannel, discord.Thread)):
        await interaction.followup.send("This command can only be used in text channels.", ephemeral=True)
        return
    
    if amount < 1 or amount > 100:
        await interaction.followup.send("Please specify a number between 1 and 100.", ephemeral=True)
        return
    
    try:
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"✅ Deleted {len(deleted)} message(s)", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to purge messages: {str(e)}", ephemeral=True)

@bot.tree.command(name="slowmode", description="Set slowmode for a channel")
@app_commands.describe(seconds="Slowmode delay in seconds (0 to disable)", channel="Channel to apply slowmode (optional)")
async def slowmode(interaction: discord.Interaction, seconds: int, channel: Optional[discord.TextChannel] = None):
    await interaction.response.defer(ephemeral=True)
    target_channel = channel or interaction.channel
    
    try:
        await target_channel.edit(slowmode_delay=seconds)
        if seconds == 0:
            await interaction.followup.send(f"✅ Slowmode disabled in {target_channel.mention}", ephemeral=True)
        else:
            await interaction.followup.send(f"✅ Slowmode set to {seconds} second(s) in {target_channel.mention}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to set slowmode: {str(e)}", ephemeral=True)

@bot.tree.command(name="lock", description="Lock a channel")
@app_commands.describe(channel="Channel to lock (optional)")
async def lock(interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
    await interaction.response.defer(ephemeral=True)
    target_channel = channel or interaction.channel
    
    try:
        await target_channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.followup.send(f"🔒 Locked {target_channel.mention}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to lock channel: {str(e)}", ephemeral=True)

@bot.tree.command(name="unlock", description="Unlock a channel")
@app_commands.describe(channel="Channel to unlock (optional)")
async def unlock(interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
    await interaction.response.defer(ephemeral=True)
    target_channel = channel or interaction.channel
    
    try:
        await target_channel.set_permissions(interaction.guild.default_role, send_messages=None)
        await interaction.followup.send(f"🔓 Unlocked {target_channel.mention}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to unlock channel: {str(e)}", ephemeral=True)

@bot.tree.command(name="addrole", description="Add a role to a member")
@app_commands.describe(member="The member", role="The role to add")
async def addrole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    await interaction.response.defer(ephemeral=True)
    try:
        await member.add_roles(role)
        await interaction.followup.send(f"✅ Added {role.mention} to {member.mention}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to add role: {str(e)}", ephemeral=True)

@bot.tree.command(name="removerole", description="Remove a role from a member")
@app_commands.describe(member="The member", role="The role to remove")
async def removerole(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    await interaction.response.defer(ephemeral=True)
    try:
        await member.remove_roles(role)
        await interaction.followup.send(f"✅ Removed {role.mention} from {member.mention}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to remove role: {str(e)}", ephemeral=True)

@bot.tree.command(name="nickname", description="Change a member's nickname")
@app_commands.describe(member="The member", nickname="New nickname (leave empty to reset)")
async def nickname(interaction: discord.Interaction, member: discord.Member, nickname: Optional[str] = None):
    await interaction.response.defer(ephemeral=True)
    try:
        await member.edit(nick=nickname)
        if nickname:
            await interaction.followup.send(f"✅ Changed {member.mention}'s nickname to {nickname}", ephemeral=True)
        else:
            await interaction.followup.send(f"✅ Reset {member.mention}'s nickname", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to change nickname: {str(e)}", ephemeral=True)

@bot.tree.command(name="serverinfo", description="Display server information")
async def serverinfo(interaction: discord.Interaction):
    await interaction.response.defer()
    
    if not interaction.guild:
        await interaction.followup.send("This command can only be used in a server.", ephemeral=True)
        return
    
    guild = interaction.guild
    
    embed = discord.Embed(title=f"{guild.name} Information", color=discord.Color.blue())
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Server ID", value=str(guild.id), inline=True)
    if guild.owner:
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Members", value=str(guild.member_count), inline=True)
    embed.add_field(name="Channels", value=str(len(guild.channels)), inline=True)
    embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="userinfo", description="Display user information")
@app_commands.describe(member="The member to get info about (optional)")
async def userinfo(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    await interaction.response.defer()
    target = member or interaction.user
    
    embed = discord.Embed(title=f"{target.name} Information", color=target.color)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="User ID", value=target.id, inline=True)
    embed.add_field(name="Nickname", value=target.nick or "None", inline=True)
    embed.add_field(name="Account Created", value=target.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Joined Server", value=target.joined_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="Roles", value=len(target.roles) - 1, inline=True)
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="announce", description="Send an announcement")
@app_commands.describe(channel="Channel to send announcement", message="Announcement message")
async def announce(interaction: discord.Interaction, channel: discord.TextChannel, message: str):
    await interaction.response.defer(ephemeral=True)
    
    try:
        embed = discord.Embed(
            title="📢 Announcement",
            description=message,
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Announced by {interaction.user.name}")
        embed.timestamp = datetime.utcnow()
        
        await channel.send(embed=embed)
        await interaction.followup.send(f"✅ Announcement sent to {channel.mention}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to send announcement: {str(e)}", ephemeral=True)

@bot.tree.command(name="poll", description="Create a poll")
@app_commands.describe(question="Poll question", options="Poll options (separate with |)")
async def poll(interaction: discord.Interaction, question: str, options: str):
    await interaction.response.defer()
    
    option_list = [opt.strip() for opt in options.split('|')]
    
    if len(option_list) < 2:
        await interaction.followup.send("Please provide at least 2 options separated by |", ephemeral=True)
        return
    
    if len(option_list) > 10:
        await interaction.followup.send("Maximum 10 options allowed", ephemeral=True)
        return
    
    embed = discord.Embed(
        title=f"📊 {question}",
        description="\n".join([f"{chr(127462 + i)} {opt}" for i, opt in enumerate(option_list)]),
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Poll by {interaction.user.name}")
    
    message = await interaction.followup.send(embed=embed)
    
    for i in range(len(option_list)):
        await message.add_reaction(chr(127462 + i))

@bot.tree.command(name="clear", description="Clear messages from a specific user")
@app_commands.describe(member="The member whose messages to delete", amount="Number of messages to check (1-100)")
async def clear(interaction: discord.Interaction, member: discord.Member, amount: int = 50):
    await interaction.response.defer(ephemeral=True)
    
    if amount < 1 or amount > 100:
        await interaction.followup.send("Please specify a number between 1 and 100.", ephemeral=True)
        return
    
    try:
        def check(msg):
            return msg.author == member
        
        deleted = await interaction.channel.purge(limit=amount, check=check)
        await interaction.followup.send(f"✅ Deleted {len(deleted)} message(s) from {member.mention}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to clear messages: {str(e)}", ephemeral=True)

@bot.tree.command(name="unban", description="Unban a user")
@app_commands.describe(user_id="The user ID to unban")
async def unban(interaction: discord.Interaction, user_id: str):
    await interaction.response.defer(ephemeral=True)
    
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await interaction.followup.send(f"✅ Unbanned {user.name}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to unban user: {str(e)}", ephemeral=True)

@bot.tree.command(name="roleinfo", description="Display role information")
@app_commands.describe(role="The role to get info about")
async def roleinfo(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.defer()
    
    embed = discord.Embed(title=f"Role: {role.name}", color=role.color)
    embed.add_field(name="Role ID", value=role.id, inline=True)
    embed.add_field(name="Members", value=len(role.members), inline=True)
    embed.add_field(name="Mentionable", value=role.mentionable, inline=True)
    embed.add_field(name="Hoisted", value=role.hoist, inline=True)
    embed.add_field(name="Position", value=role.position, inline=True)
    embed.add_field(name="Created", value=role.created_at.strftime("%Y-%m-%d"), inline=True)
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="moveall", description="Move all members from one voice channel to another")
@app_commands.describe(from_channel="Source voice channel", to_channel="Destination voice channel")
async def moveall(interaction: discord.Interaction, from_channel: discord.VoiceChannel, to_channel: discord.VoiceChannel):
    await interaction.response.defer(ephemeral=True)
    
    moved = 0
    try:
        for member in from_channel.members:
            try:
                await member.move_to(to_channel)
                moved += 1
            except:
                pass
        
        await interaction.followup.send(f"✅ Moved {moved} member(s) from {from_channel.mention} to {to_channel.mention}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to move members: {str(e)}", ephemeral=True)

@bot.tree.command(name="channelinfo", description="Display channel information")
@app_commands.describe(channel="The channel to get info about (optional)")
async def channelinfo(interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
    await interaction.response.defer()
    target = channel or interaction.channel
    
    embed = discord.Embed(title=f"Channel: {target.name}", color=discord.Color.blue())
    embed.add_field(name="Channel ID", value=target.id, inline=True)
    embed.add_field(name="Category", value=target.category.name if target.category else "None", inline=True)
    embed.add_field(name="NSFW", value=target.nsfw, inline=True)
    embed.add_field(name="Slowmode", value=f"{target.slowmode_delay}s" if target.slowmode_delay else "Disabled", inline=True)
    embed.add_field(name="Created", value=target.created_at.strftime("%Y-%m-%d"), inline=True)
    
    await interaction.followup.send(embed=embed)

class ReportView(discord.ui.View):
    def __init__(self, case_id, reported_user, reporter, message, message_link, report_channel_id):
        super().__init__(timeout=None)
        self.case_id = case_id
        self.reported_user = reported_user
        self.reporter = reporter
        self.message = message
        self.message_link = message_link
        self.report_channel_id = report_channel_id
    
    @discord.ui.button(label="Resolve Case", style=discord.ButtonStyle.green, custom_id="resolve_case")
    async def resolve_case(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        try:
            if not interaction.message:
                await interaction.followup.send("❌ Error: Could not find report message.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="<a:ModeratorReport:1432059883716346089> Case Resolved",
                description=f"Case #{self.case_id} has been resolved with no punishments.",
                color=discord.Color.green()
            )
            embed.add_field(name="Resolved By", value=interaction.user.mention, inline=False)
            embed.timestamp = datetime.utcnow()
            
            await interaction.message.edit(embed=interaction.message.embeds[0], view=None)
            await interaction.message.reply(embed=embed)
            
            try:
                reporter_dm = discord.Embed(
                    title="<a:ModeratorReport:1432059883716346089> Case Update",
                    description=f"Your report (Case #{self.case_id}) has been resolved.",
                    color=discord.Color.green()
                )
                reporter_dm.add_field(name="Status", value="Case closed with no punishments", inline=False)
                reporter_dm.timestamp = datetime.utcnow()
                
                await self.reporter.send(embed=reporter_dm)
            except:
                pass
            
            await interaction.followup.send("✅ Case resolved and reporter notified.", ephemeral=True)
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error resolving case: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="Persecute Case", style=discord.ButtonStyle.red, custom_id="persecute_case")
    async def persecute_case(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = PunishmentModal(self.case_id, self.reported_user, self.reporter, self.message_link, self.report_channel_id, interaction.guild)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Send a public message", style=discord.ButtonStyle.blurple, custom_id="public_message")
    async def public_message(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = PublicMessageModal(self.case_id, interaction.channel)
        await interaction.response.send_modal(modal)

class PunishmentModal(discord.ui.Modal, title="Apply Punishment"):
    def __init__(self, case_id, reported_user, reporter, message_link, report_channel_id, guild):
        super().__init__()
        self.case_id = case_id
        self.reported_user = reported_user
        self.reporter = reporter
        self.message_link = message_link
        self.report_channel_id = report_channel_id
        self.guild = guild
    
    punishment_type = discord.ui.TextInput(
        label="Punishment Duration",
        placeholder="Choose: 5m, 10m, 1h, 10h, 24h, or 48h",
        required=True,
        max_length=4
    )
    
    reason = discord.ui.TextInput(
        label="Reason for Punishment",
        placeholder="Enter the reason for this punishment",
        required=True,
        style=discord.TextStyle.paragraph
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        duration_map = {
            "5m": 5,
            "10m": 10,
            "1h": 60,
            "10h": 600,
            "24h": 1440,
            "48h": 2880
        }
        
        duration_str = self.punishment_type.value.lower()
        
        if duration_str not in duration_map:
            await interaction.followup.send("❌ Invalid punishment duration. Use: 5m, 10m, 1h, 10h, 24h, or 48h", ephemeral=True)
            return
        
        duration_minutes = duration_map[duration_str]
        
        try:
            if isinstance(self.reported_user, discord.Member):
                await self.reported_user.timeout(timedelta(minutes=duration_minutes), reason=self.reason.value)
            
            embed = discord.Embed(
                title="<a:ModeratorReport:1432059883716346089> Case Persecuted",
                description=f"Case #{self.case_id} - Punishment applied.",
                color=discord.Color.red()
            )
            embed.add_field(name="Punished User", value=self.reported_user.mention if isinstance(self.reported_user, discord.Member) else str(self.reported_user), inline=False)
            embed.add_field(name="Punishment", value=f"Muted for {duration_str}", inline=True)
            embed.add_field(name="Reason", value=self.reason.value, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.timestamp = datetime.utcnow()
            
            report_channel = bot.get_channel(self.report_channel_id)
            if report_channel and isinstance(report_channel, (discord.TextChannel, discord.Thread)):
                await report_channel.send(embed=embed)
            
            try:
                guild_name = self.guild.name if self.guild else "the server"
                reported_dm = discord.Embed(
                    title="<a:ModeratorReport:1432059883716346089> You Have Been Punished",
                    description=f"You have been muted in {guild_name}.",
                    color=discord.Color.red()
                )
                reported_dm.add_field(name="Duration", value=duration_str, inline=True)
                reported_dm.add_field(name="Reason", value=self.reason.value, inline=False)
                reported_dm.add_field(name="Case ID", value=f"#{self.case_id}", inline=True)
                reported_dm.timestamp = datetime.utcnow()
                
                if isinstance(self.reported_user, discord.Member):
                    await self.reported_user.send(embed=reported_dm)
            except:
                pass
            
            try:
                reporter_dm = discord.Embed(
                    title="<a:ModeratorReport:1432059883716346089> Case Update",
                    description=f"Your report (Case #{self.case_id}) has been processed.",
                    color=discord.Color.green()
                )
                reporter_dm.add_field(name="Action Taken", value=f"User muted for {duration_str}", inline=False)
                reporter_dm.add_field(name="Reason", value=self.reason.value, inline=False)
                reporter_dm.timestamp = datetime.utcnow()
                
                await self.reporter.send(embed=reporter_dm)
            except:
                pass
            
            await interaction.followup.send("✅ Punishment applied and parties notified.", ephemeral=True)
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error applying punishment: {str(e)}", ephemeral=True)

class PublicMessageModal(discord.ui.Modal, title="Send Public Message"):
    def __init__(self, case_id, channel):
        super().__init__()
        self.case_id = case_id
        self.channel = channel
    
    message_content = discord.ui.TextInput(
        label="Public Message",
        placeholder="Enter the message to send to the public",
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=2000
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            embed = discord.Embed(
                title="<a:ModeratorReport:1432059883716346089> Public Statement",
                description=self.message_content.value,
                color=discord.Color.blue()
            )
            embed.add_field(name="Case Reference", value=f"#{self.case_id}", inline=True)
            embed.add_field(name="Posted By", value=interaction.user.mention, inline=True)
            embed.timestamp = datetime.utcnow()
            
            if self.channel and isinstance(self.channel, (discord.TextChannel, discord.Thread)):
                await self.channel.send(embed=embed)
                await interaction.followup.send("✅ Public message sent.", ephemeral=True)
            else:
                await interaction.followup.send("❌ Could not send message to channel.", ephemeral=True)
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error sending public message: {str(e)}", ephemeral=True)

@bot.event
async def on_raw_reaction_add(payload):
    global case_counter
    
    if payload.user_id == bot.user.id:
        return
    
    if not hasattr(payload.emoji, 'id') or payload.emoji.id is None:
        return
    
    if payload.emoji.id == REPORT_EMOJI_ID:
        try:
            channel = bot.get_channel(payload.channel_id)
            if not channel or not isinstance(channel, (discord.TextChannel, discord.Thread)):
                return
            
            message = await channel.fetch_message(payload.message_id)
            guild = bot.get_guild(payload.guild_id)
            if not guild:
                return
            
            reporter = guild.get_member(payload.user_id)
            if not reporter:
                return
            
            report_channel = bot.get_channel(REPORT_CHANNEL_ID)
            
            if not report_channel:
                print(f"Report channel {REPORT_CHANNEL_ID} not found")
                return
            
            embed = discord.Embed(
                title=f"<:emoji:{REPORT_EMBED_EMOJI_ID}> Subspace Report System",
                description="A new report has been submitted.",
                color=0xD8BFD8
            )
            
            embed.add_field(name="📋 Case ID", value=f"#{case_counter}", inline=True)
            embed.add_field(name="👤 Reported User", value=message.author.mention, inline=True)
            embed.add_field(name="🚨 Reporter", value=reporter.mention, inline=True)
            embed.add_field(name="📍 Channel", value=channel.mention, inline=True)
            embed.add_field(name="🕐 Report Time (UTC)", value=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            embed.add_field(name="⏰ Message Time (UTC)", value=message.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            embed.add_field(name="💬 Message Content", value=message.content[:1024] if message.content else "*[No text content]*", inline=False)
            embed.add_field(name="🔗 Message Link", value=f"[Jump to Message]({message.jump_url})", inline=False)
            
            if message.attachments:
                attachment_links = "\n".join([f"[Attachment {i+1}]({att.url})" for i, att in enumerate(message.attachments)])
                embed.add_field(name="📎 Attachments", value=attachment_links, inline=False)
            
            embed.set_footer(text=f"Server: {guild.name} | Message ID: {message.id}")
            embed.timestamp = datetime.utcnow()
            
            view = ReportView(case_counter, message.author, reporter, message, message.jump_url, REPORT_CHANNEL_ID)
            
            await report_channel.send(embed=embed, view=view)
            
            case_counter += 1
            
            try:
                await message.remove_reaction(payload.emoji, reporter)
            except:
                pass
        
        except Exception as e:
            print(f"Error handling report reaction: {e}")
    
    if payload.emoji.id == UPVOTE_EMOJI_ID and payload.channel_id in ALLOWED_REACTION_CHANNELS:
        try:
            channel = bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            
            upvote_count = 0
            for reaction in message.reactions:
                if reaction.emoji == f"<:upvote:{UPVOTE_EMOJI_ID}>":
                    upvote_count = reaction.count
                    break
            
            if upvote_count >= 5:
                star_emoji = None
                for reaction in message.reactions:
                    if hasattr(reaction.emoji, 'id') and reaction.emoji.id == STAR_EMOJI_ID:
                        star_emoji = reaction
                        break
                
                if not star_emoji:
                    await message.add_reaction(f"<a:star:{STAR_EMOJI_ID}>")
        
        except Exception as e:
            print(f"Error handling upvote reaction: {e}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if message.channel.id in ALLOWED_REACTION_CHANNELS:
        try:
            await message.add_reaction(f"<:upvote:{UPVOTE_EMOJI_ID}>")
            await message.add_reaction(f"<:downvote:{DOWNVOTE_EMOJI_ID}>")
        except Exception as e:
            print(f"Error adding reactions: {e}")
    
    await bot.process_commands(message)

if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN not found in environment variables!")
        exit(1)
    
    bot.run(TOKEN)
