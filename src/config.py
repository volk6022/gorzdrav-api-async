import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    GORZDRAV_API = "https://gorzdrav.spb.ru/_api/api"
    GORZDRAV_API_V = "v2"
    API_URL = f"{GORZDRAV_API}/{GORZDRAV_API_V}"
    HEADERS = {
        "User-Agent": "gorzdrav-spb-bot"
    }
    BASE_APPOINTMENT_URL: str = "https://gorzdrav.spb.ru/service-free-schedule#"
    REQUEST_TIMEOUT: float = 30.0
    HTTP2_ENABLED: bool = True
    RETRY_INITIAL_DELAY: float = 1.0
    RETRY_ATTEMPTS: int = 3
