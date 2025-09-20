import os
import configparser
import logging
import platform
#import json
import importlib.util
from pathlib import Path

system = platform.system()
home = Path.home()

# Platform-aware directory resolution
def get_platform_dir(app_name: str, kind: str = "config") -> Path:
    if system == "Windows":
        base = home / "AppData" / ("Roaming" if kind == "config" else "Local")
    elif system == "Darwin":
        base = home / "Library" / "Application Support"
    elif system == "Linux":
        env_var = "XDG_CONFIG_HOME" if kind == "config" else "XDG_DATA_HOME"
        fallback = home / (".config" if kind == "config" else ".local/share")
        base = Path(os.environ.get(env_var, fallback))
    else:
        base = home / f".{app_name}"
    return base / app_name

#   User config loader
def load_user_config(app_name="PySBK") -> dict:
    config_path = get_platform_dir(app_name, "config") / "config.ini"
    config = configparser.ConfigParser()
    config.read(config_path)
    return config["defaults"] if "defaults" in config else {}

#   Profile resolution
def resolve_profile(name: str) -> tuple[str, str]:
    base = home / ".config"
    if name == "firefox":
        return (str(home / ".mozilla/firefox/xyz.default"), str(home / ".mozilla"))
    elif name in ["chrome", "brave", "chromium"]:
        return (str(base / name.capitalize()), str(base))
    elif name == "edge":
        return (str(base / "microsoft-edge"), str(base))
    return ("", "")

#   Strategy loader
def load_strategies(app_name="PySBK") -> dict:
    paths = [
        Path.cwd() / "strategies",  # project-local
        get_platform_dir(app_name, "config") / "strategies",  # user config
        Path(__file__).parent / "default_strategies.py"  # fallback
    ]

    strategies = {}
    for path in paths:
        if path.is_dir():
            for file in path.glob("*.py"):
                mod_name = file.stem
                spec = importlib.util.spec_from_file_location(mod_name, file)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                strategies.update(getattr(mod, "default_strategies", {}))
        elif path.is_file() and path.suffix == ".py":
            spec = importlib.util.spec_from_file_location("default_strategies", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            strategies.update(getattr(mod, "default_strategies", {}))
    return strategies

#   Logger setup
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
