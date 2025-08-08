from pydantic_settings import BaseSettings
from pydantic import AnyUrl
from typing import List

class Settings(BaseSettings):
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DATABASE_URL: str
    CORS_ORIGINS: str = "http://localhost:3000"
    BASE_LIST_URL: str = "https://www.prevost-stuff.com/forsale/public_list_ads.php"
    ENABLE_SCRAPER_STARTUP: bool = False

    def cors_list(self) -> List[str]:
        return [c.strip() for c in self.CORS_ORIGINS.split(",") if c.strip()]

settings = Settings()  # will read from environment/.env
