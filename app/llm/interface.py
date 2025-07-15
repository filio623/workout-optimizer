from agents import Agent, Runner, function_tool
from app.hevy.client import HevyClient, HevyClientError
from app.config import config
import logging
from typing import List

OPENAI_MODEL = config.OPENAI_MODEL
OPENAI_API_KEY = config.OPENAI_API_KEY

logger = logging.getLogger(__name__)

class LLMInterfaceError(Exception):
    """Custom exception for LLM interface errors."""
    
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        super().__init__(f"LLM Interface Error: {message}")


class LLMInterface:
    def __init__(self):
        try:
            self.validate_config()
            self.hevy_client = HevyClient()
            self.model = OPENAI_MODEL
            self._setup_agent()
        except Exception as e:
            logger.error(f"Error initializing LLMInterface: {e}")
            raise LLMInterfaceError(f"Error initializing LLMInterface: {e}")

    def validate_config(self):
        if not OPENAI_API_KEY:
            raise LLMInterfaceError("OPENAI_API_KEY is required but not provided")

        logger.info("Config validated successfully")

    def _setup_agent(self):
        tools = self._create_tools()
        self.agent = Agent(
            name="Fitness Assistant",
            instructions="You are a helpful workout and fitness assistant that provides advice on workout routines, nutrition, and fitness tracking.",
            model=self.model,
            tools=tools,
        )
        logger.info("Agent setup successfully")

    def _create_tools(self) -> List:
        return []

    def run(self, prompt: str) -> str:
        pass