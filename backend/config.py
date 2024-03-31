# Loading config.ini
import configparser
import sys

config = configparser.ConfigParser()

try:
    config.read('./data/config.ini')
except Exception as e:
    print("Error reading the config.ini file. Error: " + str(e))  # since this won't have access to logger, use print
    sys.exit()

# Getting variables from config.ini
try:
    # Getting the variables from `[general]`
    log_level: str = config.get('general', 'log_level')
    presence: str = config.get('general', 'presence')
    version: str = config.get('general', 'version', fallback="unknown")

    # Getting the variables from `[secret]`
    discord_token: str = config.get('secret', 'discord_token')

    # Getting the variables from `[discord]`
    embed_footer: str = config.get('discord', 'embed_footer')
    sync_server: int = config.getint('discord', 'sync_server', fallback=0)
    should_sync: bool = config.getboolean('discord', 'should_sync', fallback=False)
    embed_color: int = int(config.get('discord', 'embed_color'), base=16)
    embed_url: str = config.get('discord', 'embed_url')


except Exception as err:
    print("Error getting variables from the config file. Error: " + str(err))  # no access to logger, use print
    sys.exit()
