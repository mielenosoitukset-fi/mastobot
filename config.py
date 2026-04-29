import os
import yaml
import logging
from typing import Any, Dict


class Config:
    """Configuration class to load and manage application settings."""

    # Configure logging for configuration loading
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    CONFIG_PATH = os.environ.get("MASTOBOT_CONFIG", "config.yaml")

    def load_yaml(file_path: str) -> Dict[str, Any]:
        """Load configuration from a YAML file.

        Parameters
        ----------
        file_path :
            str:
        file_path : str :

        file_path : str :

        file_path: str :


        Returns
        -------


        """
        try:
            with open(file_path, "r") as file:
                config = yaml.safe_load(file) or {}
                logging.info(f"Loaded configuration from {file_path}")
                return config
        except Exception as e:
            logging.error(f"Failed to load configuration from {file_path}: {e}")
            return {}

    # Load the configuration
    config = load_yaml(CONFIG_PATH)

    # MongoDB Configuration
    MONGO_URI = config.get("MONGO_URI", "")
    MONGO_DBNAME = config.get("MONGO_DBNAME", "default_db")
    STATE_SOURCE_MONGO_URI = config.get("STATE_SOURCE_MONGO_URI", MONGO_URI)
    STATE_SOURCE_DBNAME = config.get("STATE_SOURCE_DBNAME", MONGO_DBNAME)

    # Mastodon configuration
    mastodon_config = config.get("MASTODON", {})
    MASTODON_ACCESS_TOKEN = mastodon_config.get("ACCESS_TOKEN")
    MASTODON_BASE_URL = mastodon_config.get("BASE_URL")
    
    # Mosofi instance configuration
    mo_config = config.get("MOSOFI", {}) # TODO: Rename this to something more neutral, that doesn't directly point to mielenosoitukset.fi, for international use
    MO_BASE_URL = mo_config.get("BASE_URL", "https://mielenosoitukset.fi")
    MO_ACCESS_TOKEN = mo_config.get("ACCESS_TOKEN", "")
    MO_CHECK_INTERVAL = int(mo_config.get("CHECK_INTERVAL", 60))
    MO_POST_MAX_DAYS = int(mo_config.get("POST_MAX_DAYS", "60"))
    
    LOG_LEVEL = config.get("LOG_LEVEL", "INFO").upper()
    
    @classmethod
    def init_config(cls) -> None:
        """Initialize configuration and log validation messages."""
        if not cls.MONGO_URI:
            cls.logger.warning("MONGO_URI is not set.")
        if not cls.MASTODON_ACCESS_TOKEN or not cls.MASTODON_BASE_URL:
            cls.logger.warning("Mastodon credentials are not set.")
        if not cls.MONGO_DBNAME:
            cls.logger.warning("MONGO_DBNAME is not set.")

        

# Initialize the configuration
Config.init_config()
