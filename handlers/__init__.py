# ============================================================
# Group Manager Bot
# Author: LearningBotsOfficial (https://github.com/LearningBotsOfficial) 
# Support: https://t.me/LearningBotsCommunity
# Channel: https://t.me/learning_bots
# YouTube: https://youtube.com/@learning_bots
# License: Open-source (keep credits, no resale)
# ============================================================

from .start import register_handlers
from .group_commands import register_group_commands
from .clone import register_clone_handlers
from .admin_panel import register_admin_handlers
from .extra_commands import register_extra_commands

def register_all_handlers(app):
    register_handlers(app)
    register_group_commands(app)
    register_clone_handlers(app)
    register_admin_handlers(app)
    register_extra_commands(app)
    print("✅ All handlers registered!")

