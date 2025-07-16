import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-4o-mini"

    HEVY_API_KEY = os.getenv("HEVY_API_KEY")
    HEVY_BASE_URL = "https://api.hevyapp.com"



    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"




    def __init__(self):
        self.validate_api_keys()

    def validate_api_keys(self) -> None:
        missing_keys = []

        if not self.OPENAI_API_KEY:
            missing_keys.append("OPENAI_API_KEY")
        if not self.HEVY_API_KEY:
            missing_keys.append("HEVY_API_KEY")

        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")

    def is_valid(self) -> bool:
        try:
            self.validate_api_keys()
            return True
        except ValueError as e:
            print(f"Error: {e}")
            return False


    
config = Config()