# src\commands\slashed\leader.py
# Slash commands for managing leaders

PRINT_PREFIX = "COMMANDS - SLASHED - LEADER"

# Third-party imports
import re
import discord
from discord import app_commands
from typing import Optional

# Local imports
from src.bot import bot
from src.db.bot_db import leaders, users
from src.commands.permissions import is_developer
from config.config_explorer import (
    LEADER_TIERS_CHOICE,
    get_all_leader_role_ids,
    get_general_leader_role_id,
    get_on_break_role_id,
)
from src.core.users.roles import edit_user_roles, add_role_to_user
from src.core.fetching import get_role_or_fetch
from src.core.embeds import create_error_embed, create_success_embed

async def _get_leader_roles(
    guild: discord.Guild, tier_role_id: int
) -> tuple[Optional[discord.Role], Optional[discord.Role]]:
    """Fetch the tier-specific and general leader roles.
    
    Args:
        guild: The Discord guild
        tier_role_id: The role ID for the specific leader tier
        
    Returns:
        Tuple of (tier_role, general_leader_role), either can be None if not found
    """
    tier_role = await get_role_or_fetch(guild, tier_role_id)
    general_role = await get_role_or_fetch(guild, get_general_leader_role_id())
    
    if tier_role is None:
        print(f"[ERROR] [{PRINT_PREFIX}] Could not find role with ID {tier_role_id} in guild.")
    
    if general_role is None:
        general_role_id = get_general_leader_role_id()
        print(f"[ERROR] [{PRINT_PREFIX}] Could not find general leader role with ID {general_role_id} in guild.")
    
    return tier_role, general_role


def _calculate_roles_to_remove(tier: str) -> list[int]:
    """Calculate which leader roles should be removed when assigning a new tier.
    
    Args:
        tier: The tier being assigned
        
    Returns:
        List of role IDs to remove
    """
    all_tier_roles = get_all_leader_role_ids()
    roles_to_remove = [rid for t, rid in all_tier_roles.items() if t != tier]
    roles_to_remove.append(get_on_break_role_id())
    return roles_to_remove


def _build_new_role_list(
    current_roles: list[discord.Role],
    tier_role: discord.Role,
    general_role: discord.Role,
    roles_to_remove: list[int],
) -> list[discord.Role]:
    """Build the new role list for a leader.
    
    Args:
        current_roles: Member's current roles
        tier_role: The tier-specific role to assign
        general_role: The general leader role to assign
        roles_to_remove: Role IDs that should be removed
        
    Returns:
        New list of roles for the member
    """
    # Filter out old leader roles
    new_roles = [
        role for role in current_roles
        if role.id not in roles_to_remove
        and role.id != tier_role.id
        and role.id != general_role.id
    ]
    # Add the new leader roles
    new_roles.extend([tier_role, general_role])
    return new_roles


async def _assign_proper_leader_role(member: discord.Member, tier: str) -> bool:
    """Assign the proper leader role to the member based on the tier.
    
    Args:
        member: The Discord member to promote
        tier: The leader tier to assign
        
    Returns:
        True if successful, False otherwise
    """
    # Validate tier and get role ID
    role_ids = get_all_leader_role_ids()
    tier_role_id = role_ids.get(tier)
    
    if tier_role_id is None:
        print(f"[WARN] [{PRINT_PREFIX}] No role ID found for tier '{tier}'. Cannot assign role.")
        return False
    
    # Fetch required roles
    tier_role, general_role = await _get_leader_roles(member.guild, tier_role_id)
    if tier_role is None or general_role is None:
        return False
    
    # Calculate which roles to remove and build new role list
    roles_to_remove = _calculate_roles_to_remove(tier)
    new_roles = _build_new_role_list(
        member.roles, tier_role, general_role, roles_to_remove
    )
    
    # Apply the role changes
    try:
        success = await edit_user_roles(
            member.id, new_roles, reason="Promoted to leader"
        )
        
        if success:
            print(f"[INFO] [{PRINT_PREFIX}] Assigned leader role '{tier}' to user {member.id}.")
        else:
            print(f"[ERROR] [{PRINT_PREFIX}] Failed to assign leader role '{tier}' to user {member.id}.")
        
        return success
        
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Exception while assigning leader role '{tier}' to user {member.id}: {e}")
        return False
    
async def _remove_leader_roles(member: discord.Member) -> bool:
    """Remove all leader roles from the member.
    
    Args:
        member: The Discord member to demote
        
    Returns:
        True if successful, False otherwise
    """
    # Gather all leader-related role IDs
    all_tier_roles = get_all_leader_role_ids()
    roles_to_remove = [
        *all_tier_roles.values(),
        get_on_break_role_id(),
        get_general_leader_role_id(),
    ]
    
    # Filter out all leader roles
    new_roles = [role for role in member.roles if role.id not in roles_to_remove]
    
    try:
        success = await edit_user_roles(
            member.id, new_roles, reason="Demoted from leader"
        )
        
        if success:
            print(f"[INFO] [{PRINT_PREFIX}] Removed leader roles from user {member.id}.")
        else:
            print(f"[ERROR] [{PRINT_PREFIX}] Failed to remove leader roles from user {member.id}.")
        
        return success
        
    except Exception as e:
        print(f"[ERROR] [{PRINT_PREFIX}] Exception while removing leader roles from user {member.id}: {e}")
        return False


class LeaderCommands(app_commands.Group):

    def __init__(self):
        super().__init__(
            name="leader",
            description="Commands for managing leaders. (Manage-roles only)",
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Verify the user has permission to use leader commands.
        
        Args:
            interaction: The command interaction
            
        Returns:
            True if user has permission, False otherwise
        """
        has_permission = (
            interaction.user.guild_permissions.manage_roles
            or is_developer(interaction.user)
        )
        
        if not has_permission:
            await interaction.response.send_message(
                "You do not have permission to use this command.",
                ephemeral=True,
            )
        
        return has_permission
        
    @app_commands.command(name="promote", description="Promote a user to leader.")
    @app_commands.describe(
        user="The user to promote to leader",
        tier="The leader tier to assign to the user.",
    )
    @app_commands.choices(tier=LEADER_TIERS_CHOICE)
    async def promote(self, interaction: discord.Interaction, user: discord.Member, tier: str):
        """Promote a user to a specified leader tier."""
        await interaction.response.defer()
        
        # Check blacklist status
        try:
            if users.is_leader_blacklisted(user.id):
                embed = create_error_embed(
                    title="Promotion Failed",
                    description=f"{user.mention} is blacklisted from being promoted to leader.",
                )
                await interaction.followup.send(embed=embed)
                return
        except Exception as e:
            print(f"[ERROR] [{PRINT_PREFIX}] Error checking blacklist status for user {user.id}: {e}")
            embed = create_error_embed(
                title="Promotion Error",
                description=f"An unexpected error occurred while checking blacklist status: {e}",
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Assign role
        try:
            role_assigned = await _assign_proper_leader_role(user, tier)
            if not role_assigned:
                embed = create_error_embed(
                    title="Promotion Error",
                    description=f"Could not assign the leader role for tier '{tier}'. Please check the configuration.",
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Update database
            success = leaders.add_leader(user.id, tier)
            if not success:
                embed = create_error_embed(
                    title="Promotion Error",
                    description=(
                        f"Failed to add {user.mention} to the leaders database. "
                        "The role was assigned but database update failed."
                    ),
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Success
            embed = create_success_embed(
                title="User Promoted",
                description=f"Successfully promoted {user.mention} to leader tier '{tier}'.",
            )
            print(f"[INFO] [{PRINT_PREFIX}] Promoted user {user.id} to tier '{tier}' by {interaction.user.id}.")
            
        except Exception as e:
            print(f"[ERROR] [{PRINT_PREFIX}] Error promoting user {user.id} to tier '{tier}': {e}")
            embed = create_error_embed(
                title="Promotion Error",
                description=f"An unexpected error occurred while promoting the user: {e}",
            )
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="demote", description="Demote a leader.")
    @app_commands.describe(user="The leader to demote.")
    async def demote(self, interaction: discord.Interaction, user: discord.Member):
        """Remove leader roles from a user and update the database."""
        await interaction.response.defer()
        
        try:
            # Verify user is a leader
            leader_data = leaders.get_leader(user.id)
            if leader_data is None:
                embed = create_error_embed(
                    title="Demotion Failed",
                    description=f"{user.mention} is not a leader or does not exist in the database.",
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Remove roles
            roles_removed = await _remove_leader_roles(user)
            if not roles_removed:
                embed = create_error_embed(
                    title="Demotion Error",
                    description=f"Failed to remove leader roles from {user.mention}.",
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Update database
            success = leaders.remove_leader(user.id)
            if not success:
                embed = create_error_embed(
                    title="Demotion Error",
                    description=(
                        f"Failed to update {user.mention} in the leaders database. "
                        "The roles were removed but database update failed, please try again."
                    ),
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Success
            embed = create_success_embed(
                title="User Demoted",
                description=f"Successfully demoted {user.mention} from leader.",
            )
            print(f"[INFO] [{PRINT_PREFIX}] Demoted user {user.id} from leader by {interaction.user.id}.")
            
        except Exception as e:
            print(f"[ERROR] [{PRINT_PREFIX}] Error demoting user {user.id}: {e}")
            embed = create_error_embed(
                title="Demotion Error",
                description=f"An unexpected error occurred while demoting the user: {e}",
            )
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="blacklist", description="Blacklist a user from being promoted to leader.")
    @app_commands.describe(user="The user to blacklist from being promoted to leader.")
    async def blacklist(self, interaction: discord.Interaction, user: discord.User):
        """Blacklist a user from being promoted to leader."""
        await interaction.response.defer()
        
        try:
            # Check if user is currently a leader and remove roles if necessary
            leader_data = leaders.get_leader(user.id)
            if leader_data is not None:
                roles_removed = await _remove_leader_roles(user)
                if not roles_removed:
                    print(f"[WARN] [{PRINT_PREFIX}] Could not remove leader roles from user {user.id} during blacklist.")
                    embed = create_error_embed(
                        title="Blacklist Error",
                        description=f"Failed to remove leader roles from {user.mention} during blacklist.",
                    )
                    await interaction.followup.send(embed=embed)
                    return
                
            # Remove from leaders database if present
            if leader_data is not None:
                db_removed = leaders.remove_leader(user.id)
                if not db_removed:
                    print(f"[WARN] [{PRINT_PREFIX}] Could not remove user {user.id} from leaders database during blacklist.")
                    embed = create_error_embed(
                        title="Blacklist Error",
                        description=f"Failed to remove {user.mention} from the leaders database during blacklist.",
                    )
                    await interaction.followup.send(embed=embed)
                    return
            
            # Add to blacklist
            success = users.add_leader_blacklist(user.id)
            if not success:
                embed = create_error_embed(
                    title="Blacklist Error",
                    description=f"Failed to add {user.mention} to the blacklist database.",
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Success
            embed = create_success_embed(
                title="Leader Blacklisted",
                description=f"Successfully blacklisted {user.mention} from being promoted to leader.",
            )
            print(f"[INFO] [{PRINT_PREFIX}] Blacklisted user {user.id} from leader promotions by {interaction.user.id}.")
            
        except Exception as e:
            print(f"[ERROR] [{PRINT_PREFIX}] Error blacklisting user {user.id}: {e}")
            embed = create_error_embed(
                title="Leader Blacklist Error",
                description=f"An unexpected error occurred while blacklisting the user: {e}",
            )
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="unblacklist",description="Remove a user from the leader promotion blacklist.",)
    @app_commands.describe(user="The user to remove from the leader promotion blacklist.")
    async def unblacklist(self, interaction: discord.Interaction, user: discord.User):
        """Remove a user from the leader promotion blacklist."""
        await interaction.response.defer()
        
        try:
            success = users.remove_leader_blacklist(user.id)
            if not success:
                embed = create_error_embed(
                    title="Unblacklist Error",
                    description=f"Failed to remove {user.mention} from the blacklist database.",
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Success
            embed = create_success_embed(
                title="User Unblacklisted",
                description=f"Successfully removed {user.mention} from the leader promotion blacklist.",
            )
            print(f"[INFO] [{PRINT_PREFIX}] Unblacklisted user {user.id} from leader promotions by {interaction.user.id}.")
            
        except Exception as e:
            print(f"[ERROR] [{PRINT_PREFIX}] Error unblacklisting user {user.id}: {e}")
            embed = create_error_embed(
                title="Unblacklist Error",
                description=f"An unexpected error occurred while unblacklisting the user: {e}",
            )
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="on_break", description="Put a leader on break.")
    @app_commands.describe(user="The leader to put on break.")
    async def on_break(self, interaction: discord.Interaction, user: discord.Member):
        """Put a leader on break by assigning the on-break role."""
        await interaction.response.defer()
        
        try:
            # Verify user is a leader
            leader_data = leaders.get_leader(user.id)
            if leader_data is None:
                embed = create_error_embed(
                    title="On Break Failed",
                    description=f"{user.mention} is not a leader or does not exist in the database.",
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Verify not already on break
            if leaders.is_leader_on_break(user.id):
                embed = create_error_embed(
                    title="On Break Error",
                    description=f"{user.mention} is already on break since <t:{leader_data['on_break_since']}:R>.",
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Assign on-break role
            on_break_role_id = get_on_break_role_id()
            on_break_role = await get_role_or_fetch(user.guild, on_break_role_id)
            if on_break_role is None:
                embed = create_error_embed(
                    title="On Break Error",
                    description="Could not find the on-break role in the guild configuration.",
                )
                await interaction.followup.send(embed=embed)
                return
            
            success = await add_role_to_user(
                user.id, on_break_role, reason="Leader put on break"
            )
            if not success:
                embed = create_error_embed(
                    title="On Break Error",
                    description=f"Failed to assign the on-break role to {user.mention}.",
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Update database
            db_success = leaders.put_leader_on_break(user.id)
            if not db_success:
                embed = create_error_embed(
                    title="On Break Error",
                    description=(
                        f"Failed to update {user.mention} in the leaders database. "
                        "The role was assigned but database update failed."
                    ),
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Success
            embed = create_success_embed(
                title="Leader On Break",
                description=f"Successfully put {user.mention} on break.",
            )
            print(f"[INFO] [{PRINT_PREFIX}] Put user {user.id} on break by {interaction.user.id}.")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f"[ERROR] [{PRINT_PREFIX}] Error putting user {user.id} on break: {e}")
            embed = create_error_embed(
                title="On Break Error",
                description=f"An unexpected error occurred while putting the user on break: {e}",
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="off_break", description="Remove a leader from break.")
    @app_commands.describe(user="The leader to remove from break.")
    async def off_break(self, interaction: discord.Interaction, user: discord.Member):
        """Remove a leader from break by removing the on-break role."""
        await interaction.response.defer()
        
        try:
            # Verify user is a leader
            leader_data = leaders.get_leader(user.id)
            if leader_data is None:
                embed = create_error_embed(
                    title="Off Break Failed",
                    description=f"{user.mention} is not a leader or does not exist in the database.",
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Verify currently on break
            if not leaders.is_leader_on_break(user.id):
                embed = create_error_embed(
                    title="Off Break Error",
                    description=f"{user.mention} is not currently on break.",
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Remove on-break role
            on_break_role_id = get_on_break_role_id()
            on_break_role = await get_role_or_fetch(user.guild, on_break_role_id)
            if on_break_role is None:
                embed = create_error_embed(
                    title="Off Break Error",
                    description="Could not find the on-break role in the guild configuration.",
                )
                await interaction.followup.send(embed=embed)
                return
            
            success = await edit_user_roles(
                user.id,
                [role for role in user.roles if role.id != on_break_role.id],
                reason="Leader removed from break",
            )
            if not success:
                embed = create_error_embed(
                    title="Off Break Error",
                    description=f"Failed to remove the on-break role from {user.mention}.",
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Update database
            db_success = leaders.remove_leader_from_break(user.id)
            if not db_success:
                embed = create_error_embed(
                    title="Off Break Error",
                    description=(
                        f"Failed to update {user.mention} in the leaders database. "
                        "The role was removed but database update failed."
                    ),
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Success
            embed = create_success_embed(
                title="Leader Off Break",
                description=f"Successfully removed {user.mention} from break.",
            )
            print(f"[INFO] [{PRINT_PREFIX}] Removed user {user.id} from break by {interaction.user.id}.")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f"[ERROR] [{PRINT_PREFIX}] Error removing user {user.id} from break: {e}")
            embed = create_error_embed(
                title="Off Break Error",
                description=f"An unexpected error occurred while removing the user from break: {e}",
            )
            await interaction.followup.send(embed=embed)

bot.tree.add_command(LeaderCommands())


