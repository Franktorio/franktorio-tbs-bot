# src\commands\prefixed\embeds.py
# Prefixed commands to test out embeds

# Standard library imports
import datetime

# Third-party imports

# Local imports
import src.core.embeds as core_embeds
from src.core.fetching import get_role_or_fetch
from src.bot import bot
import config.config_explorer as cfg_exp

@bot.command(name="embeds_test", help="Displays every embed type for testing purposes.")
async def embeds_test(ctx):
    # Example user and leader data
    user = ctx.author

    bogus_wins = [{"game": "Example Game", "date": "2023-01-01"}, {"game": "Another Game", "date": "2023-02-01"}, {"game": "Third Game", "date": "2023-03-01"}]
    
    def _get_bogus_leader_data(tier: str, on_break: bool) -> dict:
        return {
            "leader_tier": tier.lower(),
            "on_break_since": 0,
            "last_win_at": datetime.datetime.now().timestamp() - 5 * 86400,
            "last_host_at": datetime.datetime.now().timestamp() - 3 * 86400,
            "promoted_at": datetime.datetime.now().timestamp() - 30 * 86400,
            "on_break_since": datetime.datetime.now().timestamp() - 2 * 86400 if on_break else 0
        }
    for tier in cfg_exp.LEADER_TIERS:
        data = _get_bogus_leader_data(tier, on_break=(tier=="graduate"))
        role_id = cfg_exp.get_leader_role_id(tier) if data.get("on_break_since", 0) == 0 else cfg_exp.get_on_break_role_id()
        role = await get_role_or_fetch(ctx.guild, role_id) if role_id else None
        embed = core_embeds.create_leader_info_embed(user, data, bogus_wins, role)
        await ctx.send(embed=embed)


