# src\commands\prefixed\embeds.py
# Prefixed commands to test out embeds

# Standard library imports
import datetime

# Third-party imports

# Local imports
import src.core.embeds as core_embeds
from src.bot import bot
from config.config_explorer import LEADER_TIERS


@bot.command(name="embeds_test", help="Displays every embed type for testing purposes.")
async def embeds_test(ctx):
    # Example user and leader data
    user = ctx.author

    bogus_wins = [{"game": "Example Game", "date": "2023-01-01"}, {"game": "Another Game", "date": "2023-02-01"}, {"game": "Third Game", "date": "2023-03-01"}]
    

    for role in LEADER_TIERS:
        leader_data = {
            "user_id": user.id,
            "leader_tier": role,
            "on_break_since": 0,
            "promoted_at": int(datetime.datetime.now().timestamp()) - 604800,  # Promoted 1 week ago
            "last_win_at": datetime.datetime.now().timestamp(),
            "last_host_at": datetime.datetime.now().timestamp()
        }
        embed = core_embeds.create_leader_info_embed(user, leader_data, bogus_wins)
        await ctx.channel.send(embed=embed)
    
    # Example of on_break status
    leader_data = {
        "user_id": user.id,
        "leader_tier": "Master",
        "promoted_at": int(datetime.datetime.now().timestamp()) - 604800,  # Promoted 1 week ago
        "on_break_since": int(datetime.datetime.now().timestamp()) - 86400,  # On break since 1 day ago
        "last_win_at": datetime.datetime.now().timestamp(),
        "last_host_at": datetime.datetime.now().timestamp()
    }
    embed = core_embeds.create_leader_info_embed(user, leader_data, bogus_wins)
    await ctx.channel.send(embed=embed)

    embed = core_embeds.create_success_embed(title="Successfully sent embeds", description="All leader info embeds have been displayed above.")
    await ctx.channel.send(embed=embed)

    embed = core_embeds.create_error_embed(title="Error Example", description="This is an example error embed.")
    await ctx.channel.send(embed=embed)

