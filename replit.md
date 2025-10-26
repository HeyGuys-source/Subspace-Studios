# Discord Moderation Bot - Project Documentation

## Project Overview
Advanced Discord moderation bot with comprehensive administrative features, health monitoring, and automated reporting system. Built with Discord.py and Flask.

## Current Status
- **Status**: Fully functional and running
- **Bot Name**: Subspace Studios#1079
- **Commands Synced**: 24 slash commands
- **Health Check**: Active on port 5000
- **Last Updated**: October 26, 2025

## Architecture

### Core Components
1. **bot.py** - Main Discord bot logic with all commands and event handlers
2. **health_server.py** - Flask server for health check endpoint
3. **main.py** - Entry point that runs both bot and health server in parallel threads

### Key Features Implemented

#### 1. Health Check System
- Flask server on port 5000 with `/health` endpoint
- Designed for Render.com uptime monitoring
- Ensures bot runs indefinitely

#### 2. Unique Administrative Commands
- **`/echo`**: Send messages anonymously with format options (embed/plain/code), reply support, and attachment URLs
- **`/masslock`**: Lock 2-10 channels simultaneously with optional auto-unlock timer
- **`/massmute`**: Mute 2-5 members at once with optional timer and reason

#### 3. Standard Administrative Commands (20+)
- User moderation: ban, kick, mute, unmute, warn, clear
- Channel management: lock, unlock, slowmode, purge, channelinfo
- Role management: addrole, removerole
- Member management: nickname, moveall
- Information: serverinfo, userinfo, roleinfo
- Utilities: announce, poll, unban

#### 4. Subspace Report System
- **Trigger**: React with emoji ID `1432054365862105099` on any message
- **Report Channel**: ID `1407034866226430063`
- **Report Format**: Light purple embed with comprehensive details
- **Interactive Buttons**:
  - Resolve Case: Closes case without punishment, notifies reporter
  - Persecute Case: Opens modal for punishment selection (5m, 10m, 1h, 10h, 24h, 48h mute)
  - Send Public Message: Posts public statement about the case
- **DM Notifications**: Automatically notifies reporter and reported users

#### 5. Automated Reaction System
- Adds upvote (ID: `1432070542831255724`) and downvote (ID: `1432070594551353364`) to all messages
- Automatically adds star emoji (ID: `1432070448245641346`) when message reaches 5 upvotes
- **Active Channels**: 
  - 1338311408156278844
  - 1397275881008791723
  - 1397276528873701448
  - 1407895335711408209

## Configuration

### Environment Variables
- `DISCORD_BOT_TOKEN`: Discord bot authentication token (required)
- `SESSION_SECRET`: Flask session secret (auto-configured)

### Emoji & Channel IDs
All configured in `bot.py`:
```python
REPORT_EMOJI_ID = 1432054365862105099
REPORT_CHANNEL_ID = 1407034866226430063
REPORT_EMBED_EMOJI_ID = 1432059800258347049
UPVOTE_EMOJI_ID = 1432070542831255724
DOWNVOTE_EMOJI_ID = 1432070594551353364
STAR_EMOJI_ID = 1432070448245641346
```

## Technical Details

### Dependencies
- discord.py 2.6.4 - Discord API wrapper
- flask 3.1.2 - Health check web server
- python-dotenv 1.2.1 - Environment variable management
- aiohttp 3.13.1 - Async HTTP client

### Error Handling
- Guild guards on all server-specific commands
- Channel type checking for text-based operations
- Graceful error messages for users
- Exception logging for debugging

### Security
- Secrets managed through Replit environment
- No hardcoded tokens or sensitive data
- DM privacy for report notifications
- Anonymous echo command (doesn't expose command user)

## Deployment

### Render.com Deployment
1. Connect repository to Render.com
2. Set environment variable: `DISCORD_BOT_TOKEN`
3. Configure health check endpoint: `/health`
4. Bot will run indefinitely with automatic restarts

### Local Development
1. Set `DISCORD_BOT_TOKEN` in environment or secrets
2. Run: `python main.py`
3. Health check available at `http://localhost:5000/health`

## Recent Changes
- Fixed modal interaction handlers to properly send embeds to report channel
- Added guild and channel type guards throughout for safety
- Implemented proper error handling for all interactive components
- Tested and verified all 24 commands sync correctly

## Known Limitations
- 69 LSP type-checking warnings (non-critical, don't affect functionality)
- Bot requires specific emoji and channel IDs to be present in the Discord server
- Reaction system only works in configured channels

## Future Enhancements
- Database integration for persistent case tracking
- Advanced logging dashboard
- Auto-moderation rules (spam detection, word filters)
- Web dashboard for bot management
- Appeal system for punishments
