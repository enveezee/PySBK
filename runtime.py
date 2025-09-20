import configparser
import logging
from pathlib import Path
import platform

system = platform.system()
home = Path.home()

def get_user_data_dir(app_name: str) -> Path:
    if system == 'Windows':
        # Conventionally uses %LOCALAPPDATA%
        return home / 'AppData' / 'Local' / app_name
    elif system == 'Darwin':
        # Conventionally uses ~/Library/Application Support
        return home / 'Library' / 'Application Support' / app_name
    elif system == 'Linux':
        # Adheres to the XDG Base Directory Specification
        xdg_data_home = Path(os.environ.get('XDG_DATA_HOME', home / '.local' / 'share'))
        return xdg_data_home / app_name
    else:
        # Fallback for unsupported systems
        return home / f'.{app_name}'

def get_user_config_dir(app_name: str) -> Path:
    if system == 'Windows':
        # Conventionally uses %APPDATA% (Roaming) or %LOCALAPPDATA%
        return home / 'AppData' / 'Roaming' / app_name
    elif system == 'Darwin':
        # Same convention as user data, ~/Library/Application Support
        return home / 'Library' / 'Application Support' / app_name
    elif system == 'Linux':
        # Adheres to the XDG Base Directory Specification
        xdg_config_home = Path(os.environ.get('XDG_CONFIG_HOME', home / '.config'))
        return xdg_config_home / app_name
    else:
        # Fallback for unsupported systems
        return home / f'.{app_name}'
    
def load_config(app_name="PySBK"):
    config_path = Path.home() / ".config" / app_name.lower() / "config.ini"
    config = configparser.ConfigParser()
    config.read(config_path)
    return config["defaults"] if "defaults" in config else {}

def resolve_profile(self, name):
    home = os.path.expanduser("~")
    if name == "firefox":
        return (home + "/.mozilla/firefox/xyz.default", home + "/.mozilla")
    elif name in ["chrome", "brave", "chromium"]:
        return (home + "/.config/" + name.capitalize(), home + "/.config")
    elif name == "edge":
        return (home + "/.config/microsoft-edge", home + "/.config")
    return ("", "")

def setup_logger(name="PySBK", log_to_file=False, log_file="pysbk.log", level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_to_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
