class Config:
    # Server configuration
    HOST = "0.0.0.0"
    PORT = 8000
    SERVER_WORKERS = 1
    
    # Pool configuration
    POOL_SIZE = 5
    QUEUE_MAXSIZE = 100

    # API configuration
    GORZDRAV_API = "https://gorzdrav.spb.ru/_api/api"
    GORZDRAV_API_V = "v2"
    API_URL = f"{GORZDRAV_API}/{GORZDRAV_API_V}"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://gorzdrav.spb.ru/service-free-schedule"
    }
    BASE_APPOINTMENT_URL: str = "https://gorzdrav.spb.ru/service-free-schedule#"
    REQUEST_TIMEOUT: float = 30.0
    HTTP2_ENABLED: bool = True
    RETRY_INITIAL_DELAY: float = 1.0
    RETRY_ATTEMPTS: int = 3
