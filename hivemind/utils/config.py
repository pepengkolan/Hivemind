import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    MIMO_API_KEY = os.getenv("MIMO_API_KEY", "")
    MIMO_BASE_URL = os.getenv("MIMO_BASE_URL", "https://token-plan-sgp.xiaomimimo.com/v1")
    MIMO_MODEL = os.getenv("MIMO_MODEL", "mimo-v2.5-pro")
    MAX_ROUNDS = int(os.getenv("MAX_ROUNDS", "5"))
    AGENT_COUNT = int(os.getenv("AGENT_COUNT", "3"))
