import os
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

class BotConfig:
    """
    Strict configuration class.
    Reads environment variables and validates their existence.
    """
    
    @staticmethod
    def get_env_var(var_name: str, default: str | None = None, required: bool = True) -> str:
        value = os.getenv(var_name, default)
        if required and not value:
            raise ValueError(f"Environment variable {var_name} is strictly required.")
        return str(value)

    @classmethod
    def load(cls) -> "BotConfig":
        cls.LOG_LEVEL = cls.get_env_var("LOG_LEVEL", default="INFO", required=False)
        cls.INPUT_EXCEL_PATH = cls.get_env_var("INPUT_EXCEL_PATH", default="data/input_cards.xlsx", required=True)
        cls.OUTPUT_EXCEL_PATH = cls.get_env_var("OUTPUT_EXCEL_PATH", default="data/output_prices.xlsx", required=True)
        cls.MAX_RETRIES = int(cls.get_env_var("MAX_RETRIES", default="3", required=False))
        cls.RETRY_DELAY = int(cls.get_env_var("RETRY_DELAY", default="2", required=False))
        return cls()

config = BotConfig.load()
