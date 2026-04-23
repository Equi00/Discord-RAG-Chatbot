import json
import logging.config
import pathlib

logger = logging.getLogger("discord_rag_chatbot")


def setup_logging():
    pathlib.Path("logs").mkdir(parents=True, exist_ok=True)
    config_file = pathlib.Path("logging_configs/logger_config.json")
    with open(config_file) as f_in:
        config = json.load(f_in)
    logging.config.dictConfig(config)