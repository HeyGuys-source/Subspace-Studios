# Advanced Discord Moderation Bot

A comprehensive Discord bot with advanced moderation features, health monitoring, and automated reporting system.

## Features

### Health Check System
- `/health` endpoint for Render.com uptime monitoring
- Keeps the bot running indefinitely on Render.com

### Unique Administrative Commands
- `/echo` - Send messages as the bot with customizable format (embed/plain/code), reply support, and attachments
- `/masslock` - Lock 2-10 channels simultaneously with optional timer
- `/massmute` - Mute 2-5 members at once with optional timer and reason

### Standard Administrative Commands
- `/ban` - Ban a member from the server
- `/kick` - Kick a member from the server  
- `/mute` - Timeout a member for specified duration
- `/unmute` - Remove timeout from a member
- `/warn` - Issue a warning to a member
- `/purge` - Delete multiple messages
- `/slowmode` - Set slowmode for a channel
- `/lock` - Lock a channel
- `/unlock` - Unlock a channel
- `/addrole` - Add a role to a member
- `/removerole` - Remove a role from a member
- `/nickname` - Change a member's nickname
- `/serverinfo` - Display server information
- `/userinfo` - Display user information
- `/announce` - Send an announcement
- `/poll` - Create a poll
- `/clear` - Clear messages from a specific user
- `/unban` - Unban a user
- `/roleinfo` - Display role information
- `/moveall` - Move all members between voice channels
- `/channelinfo` - Display channel information

### Subspace Report System
- React to any message with the report emoji to create a detailed report
- Automated report generation with comprehensive details
- Interactive buttons for moderators:
  - **Resolve Case** - Close the case with no punishment
  - **Persecute Case** - Apply punishment (5m, 10m, 1h, 10h, 24h, 48h mute)
  - **Send Public Message** - Post a public statement about the case
- Automatic DM notifications to reporters and reported users

### Automated Reaction System
- Automatically adds upvote and downvote reactions to messages in designated channels
- Adds a star reaction when a message reaches 5 upvotes
- Works in channels: 1338311408156278844, 1397275881008791723, 1397276528873701448, 1407895335711408209

## Setup

1. Set your Discord bot token as an environment variable named `DISCORD_BOT_TOKEN`
2. Run the bot with `python main.py`
3. The health check server will start on port 5000
4. The bot will connect to Discord and sync slash commands

## Configuration

The bot uses these emoji and channel IDs (configured in bot.py):
- Report trigger emoji: 1432054365862105099
- Report channel: 1407034866226430063
- Upvote emoji: 1432070542831255724
- Downvote emoji: 1432070594551353364
- Star emoji: 1432070448245641346

## Deployment to Render.com

The bot includes a `/health` endpoint specifically for Render.com monitoring, ensuring it stays online indefinitely.

Set the following environment variables on Render.com:
- `DISCORD_BOT_TOKEN` - Your Discord bot token
