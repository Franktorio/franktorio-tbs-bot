# src\commands\slashed\context.py
# Slashed commands to interact with the context json of the bot.

PRINT_PREFIX = "COMMANDS - SLASHED - CONTEXT"

# Standard library imports
import json
import io
from typing import Callable

# Third-party imports
import discord
from discord import app_commands

# Local imports
from src.bot import bot
from src.core.embeds import create_success_embed, create_error_embed
from src.db.context_json import (
    add_category_entry,
    add_channel_entry,
    add_role_entry,
    add_dev_entry
)
from src.db.context_json import (
    get_category_entry,
    get_channel_entry,
    get_role_entry,
    get_dev_entry
)
from src.db.context_json import (
    delete_category_entry,
    delete_channel_entry,
    delete_role_entry,
    delete_dev_entry
)
from src.db.context_json import export_context_json
from src.commands.permissions import is_developer

def _decide_entry_type(entry_type: str, caller_id: int) -> tuple[Callable, Callable, Callable]:
    """Returns the appropriate functions for the given entry type."""
    entry_type = entry_type.lower()
    if entry_type == "category":
        return get_category_entry, add_category_entry, delete_category_entry
    elif entry_type == "channel":
        return get_channel_entry, add_channel_entry, delete_channel_entry
    elif entry_type == "role":
        return get_role_entry, add_role_entry, delete_role_entry
    elif entry_type == "dev":
        if not is_developer(caller_id): # Prevent non-developers from accessing dev entries
            return None, None, None
        return get_dev_entry, add_dev_entry, delete_dev_entry
    else:
        return None, None, None

class ContextCommands(app_commands.Group):
    """Group of slashed commands to manage the bot's context JSON."""

    def __init__(self):
        super().__init__(name="context", description="Manage the bot's context JSON data. (Administrator only)")

    async def interaction_check(self, interaction):
        try:
            interaction.user.guild_permissions.administrator
            return True
        except Exception:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
            return False
    
    @app_commands.command(name="export", description="Export the entire context JSON data.")
    async def export(self, interaction: discord.Interaction):
        await interaction.response.defer()
        print(f"[INFO] [{PRINT_PREFIX}] Exporting context.json data")

        try:
            context_data = export_context_json()
            context_json_str = json.dumps(context_data, indent=2)
            context_file = discord.File(io.StringIO(context_json_str), filename="context.json")

            embed = create_success_embed("Context JSON Exported", "The context.json data has been exported successfully.")
            await interaction.followup.send(embed=embed, file=context_file)

        except Exception as e:
            print(f"[WARNING] {PRINT_PREFIX} Error exporting context.json: {e}")
            embed = create_error_embed("Error Exporting Context JSON", f"An error occurred while exporting the context.json data: {e}")
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="delete", description="Delete an entry from the context JSON.")
    @app_commands.describe(entry_type="Type of entry to delete (category, channel, role, dev)", entry_name="Name of the entry")
    async def delete(self, interaction: discord.Interaction, entry_type: str, entry_name: str):
        await interaction.response.defer()
        print(f"[INFO] [{PRINT_PREFIX}] Deleting {entry_type} entry '{entry_name}'")

        _, _, delete_entry_func = _decide_entry_type(entry_type, interaction.user.id)

        if not delete_entry_func:
            embed = create_error_embed("Invalid Entry Type", f"The entry type '{entry_type}' is not valid. Please use 'category', 'channel', 'role', or 'dev'.")
            await interaction.followup.send(embed=embed)
            return
        
        try:
            delete_entry_func(entry_name)
            embed = create_success_embed("Entry Deleted", f"The {entry_type} entry '{entry_name}' has been deleted.")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f"[WARNING] [{PRINT_PREFIX}] Error deleting entry: {e}")
            embed = create_error_embed("Error Deleting Entry", f"An error occurred while deleting the entry: {e}")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="set_id", description="Set an entry as an integer in the context JSON.")
    @app_commands.describe(entry_type="Type of entry to set (category, channel, role, dev)", entry_name="Name of the entry", entry_id="ID of the entry")
    async def set_id(self, interaction: discord.Interaction, entry_type: str, entry_name: str, entry_id: str):
        await interaction.response.defer()
        print(f"[INFO] [{PRINT_PREFIX}] Setting {entry_type} entry '{entry_name}' with ID {entry_id}")

        _, add_entry_func, _ = _decide_entry_type(entry_type, interaction.user.id)

        if not add_entry_func:
            embed = create_error_embed("Invalid Entry Type", f"The entry type '{entry_type}' is not valid. Please use 'category', 'channel', 'role', or 'dev'.")
            await interaction.followup.send(embed=embed)
            return
        
        try:
            add_entry_func(entry_name, int(entry_id))
            embed = create_success_embed("Entry Set", f"The {entry_type} entry '{entry_name}' has been set with ID {entry_id}.")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f"[WARNING] [{PRINT_PREFIX}] Error setting entry: {e}")
            embed = create_error_embed("Error Setting Entry", f"An error occurred while setting the entry: {e}")
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="set_list", description="Set an entry as a list of in the context JSON.")
    @app_commands.describe(entry_type="Type of entry to set (category, channel, role, dev)", entry_name="Name of the entry")
    async def set_list(self, interaction: discord.Interaction, entry_type: str, entry_name: str):
        await interaction.response.defer()
        print(f"[INFO] [{PRINT_PREFIX}] Setting {entry_type} entry '{entry_name}' as a list")

        _, add_entry_func, _ = _decide_entry_type(entry_type, interaction.user.id)

        if not add_entry_func:
            embed = create_error_embed("Invalid Entry Type", f"The entry type '{entry_type}' is not valid. Please use 'category', 'channel', 'role', or 'dev'.")
            await interaction.followup.send(embed=embed)
            return
        
        try:
            add_entry_func(entry_name, [])
            embed = create_success_embed("Entry Set as List", f"The {entry_type} entry '{entry_name}' has been set as an empty list.")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f"[WARNING] [{PRINT_PREFIX}] Error setting entry as list: {e}")
            embed = create_error_embed("Error Setting Entry as List", f"An error occurred while setting the entry as a list: {e}")
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="set_bool", description="Set an entry as a boolean in the context JSON.")
    @app_commands.describe(entry_type="Type of entry to set (category, channel, role, dev)", entry_name="Name of the entry", entry_value="Boolean value to set (true/false)")
    async def set_bool(self, interaction: discord.Interaction, entry_type: str, entry_name: str, entry_value: bool):
        await interaction.response.defer()
        print(f"[INFO] [{PRINT_PREFIX}] Setting {entry_type} entry '{entry_name}' with boolean value {entry_value}")

        _, add_entry_func, _ = _decide_entry_type(entry_type, interaction.user.id)

        if not add_entry_func:
            embed = create_error_embed("Invalid Entry Type", f"The entry type '{entry_type}' is not valid. Please use 'category', 'channel', 'role', or 'dev'.")
            await interaction.followup.send(embed=embed)
            return
        
        try:
            add_entry_func(entry_name, bool(entry_value))
            embed = create_success_embed("Entry Set", f"The {entry_type} entry '{entry_name}' has been set with boolean value {entry_value}.")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f"[WARNING] {PRINT_PREFIX} Error setting entry: {e}")
            embed = create_error_embed("Error Setting Entry", f"An error occurred while setting the entry: {e}")
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="set_str", description="Set an entry as a string in the context JSON.")
    @app_commands.describe(entry_type="Type of entry to set (category, channel, role, dev)", entry_name="Name of the entry", entry_value="String value to set")
    async def set_str(self, interaction: discord.Interaction, entry_type: str, entry_name: str, entry_value: str):
        await interaction.response.defer()
        print(f"[INFO] [{PRINT_PREFIX}] Setting {entry_type} entry '{entry_name}' with string value '{entry_value}'")

        _, add_entry_func, _ = _decide_entry_type(entry_type, interaction.user.id)

        if not add_entry_func:
            embed = create_error_embed("Invalid Entry Type", f"The entry type '{entry_type}' is not valid. Please use 'category', 'channel', 'role', or 'dev'.")
            await interaction.followup.send(embed=embed)
            return
        
        try:
            add_entry_func(entry_name, str(entry_value))
            embed = create_success_embed("Entry Set", f"The {entry_type} entry '{entry_name}' has been set with string value '{entry_value}'.")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f"[WARNING] [{PRINT_PREFIX}] Error setting entry: {e}")
            embed = create_error_embed("Error Setting Entry", f"An error occurred while setting the entry: {e}")
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="append_id", description="Append an ID to a list entry in the context JSON.")
    @app_commands.describe(entry_type="Type of entry to append to (category, channel, role, dev)", entry_name="Name of the entry", entry_id="ID to append")
    async def append_id(self, interaction: discord.Interaction, entry_type: str, entry_name: str, entry_id: str):
        await interaction.response.defer()
        print(f"[INFO] [{PRINT_PREFIX}] Appending ID {entry_id} to {entry_type} entry '{entry_name}'")
        get_entry_func, add_entry_func, _ = _decide_entry_type(entry_type, interaction.user.id)

        if not get_entry_func or not add_entry_func:
            embed = create_error_embed("Invalid Entry Type", f"The entry type '{entry_type}' is not valid. Please use 'category', 'channel', 'role', or 'dev'.")
            await interaction.followup.send(embed=embed)
            return  
        
        try:
            current_entry = get_entry_func(entry_name)
            if current_entry is None:
                embed = create_error_embed("Entry Not Found", f"The {entry_type} entry '{entry_name}' does not exist.")
                await interaction.followup.send(embed=embed)
                return
            
            if not isinstance(current_entry, list):
                embed = create_error_embed("Invalid Entry Format", f"The {entry_type} entry '{entry_name}' is not a list and cannot have IDs appended.")
                await interaction.followup.send(embed=embed)
                return
            
            if int(entry_id) in current_entry:
                embed = create_error_embed("ID Already Exists", f"The ID {entry_id} already exists in the {entry_type} entry '{entry_name}'.")
                await interaction.followup.send(embed=embed)
                return
            
            current_entry.append(int(entry_id))
            add_entry_func(entry_name, current_entry)
            embed = create_success_embed("ID Appended", f"The ID {entry_id} has been appended to the {entry_type} entry '{entry_name}'.")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(f"[WARNING] [{PRINT_PREFIX}] Error appending ID: {e}")
            embed = create_error_embed("Error Appending ID", f"An error occurred while appending the ID: {e}")
            await interaction.followup.send(embed=embed)


bot.tree.add_command(ContextCommands())


