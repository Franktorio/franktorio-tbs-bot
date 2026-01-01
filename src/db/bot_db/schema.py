# Franktorio TBS Bot
# Author: Franktorio
# December 16, 2025
# Bot Database Handler - stores bot configuration and user data

PRINT_PREFIX = "BOT DB"

DB_FILE_NAME = "bot.db"

SCHEMA = {
    "users": """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            roblox_user_id INTEGER,
            is_banned BOOLEAN NOT NULL DEFAULT 0,
            is_leader_blacklisted BOOLEAN NOT NULL DEFAULT 0,
            warnings TEXT DEFAULT '{}',
            notes TEXT DEFAULT '{}',
            personal_blacklists TEXT DEFAULT '[]',
            personal_whitelists TEXT DEFAULT '[]'
        );
    """,
    
    "leaders": """
        CREATE TABLE IF NOT EXISTS leaders (
            user_id INTEGER PRIMARY KEY,
            leader_tier TEXT,
            on_break_since INTEGER DEFAULT 0,
            promoted_at INTEGER DEFAULT (strftime('%s', 'now')),
            last_win_at INTEGER DEFAULT NULL,
            last_host_at INTEGER DEFAULT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
    """, # Put 0 on the demotion_in fields to indicate no demotion is scheduled
    
    "wins": """
        CREATE TABLE IF NOT EXISTS wins (
            win_message_id INTEGER PRIMARY KEY,
            win_message_link TEXT,
            user_id INTEGER,
            won_at INTEGER DEFAULT (strftime('%s', 'now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
    """,
    
    "minor_wins": """
        CREATE TABLE IF NOT EXISTS minor_wins (
            win_message_id INTEGER PRIMARY KEY,
            win_message_link TEXT,
            user_id INTEGER,
            won_at INTEGER DEFAULT (strftime('%s', 'now')),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
    """,

    "global_blacklists": """
        CREATE TABLE IF NOT EXISTS global_blacklists (
            blacklist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            enforced_by INTEGER NOT NULL,
            reason TEXT NOT NULL,
            duration INTEGER,
            applied_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
            modifications TEXT DEFAULT '[]',
            is_expired BOOLEAN NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (enforced_by) REFERENCES users(user_id)
        );
    """,
    
    "under_review": """
        CREATE TABLE IF NOT EXISTS under_review (
            case_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            reason TEXT NOT NULL,
            given_at INTEGER DEFAULT (strftime('%s', 'now')),
            removed_at INTEGER DEFAULT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
    """,
    
    "create_vc_templates": """
        CREATE TABLE IF NOT EXISTS create_vc_templates (
            master_vc_id INTEGER PRIMARY KEY,
            name_prefix TEXT,
            permission_overrides TEXT DEFAULT '{}',
            manager_roles TEXT DEFAULT '[]',
            apply_global_blacklists BOOLEAN NOT NULL DEFAULT 0,
            apply_owner_permissions BOOLEAN NOT NULL DEFAULT 1,
            apply_whitelisted_users BOOLEAN NOT NULL DEFAULT 1
        );
    """,
    
    "active_vcs": """
        CREATE TABLE IF NOT EXISTS active_vcs (
            vc_id INTEGER PRIMARY KEY,
            owner_id INTEGER NOT NULL,
            master_vc_id INTEGER NOT NULL,
            created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
            muted_users TEXT DEFAULT '[]',
            deafened_users TEXT DEFAULT '[]',
            FOREIGN KEY (owner_id) REFERENCES users(user_id),
            FOREIGN KEY (master_vc_id) REFERENCES create_vc_templates(master_vc_id)
        );
    """
}
