import threading
import os
from health_server import run_server
from bot import bot

def start_health_server():
    print("Starting health check server...")
    run_server()

def start_bot():
    print("Starting Discord bot...")
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not TOKEN:
        print("ERROR: DISCORD_BOT_TOKEN not found in environment variables!")
        print("Please set your Discord bot token in the secrets.")
        return
    bot.run(TOKEN)

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_health_server, daemon=True)
    server_thread.start()
    
    print("=" * 50)
    print("Discord Moderation Bot Starting...")
    print("Health check available at /health")
    print("=" * 50)
    
    start_bot()
