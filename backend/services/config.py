from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "SignalFeed API"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite:///./signalfeed.db"
    COLLECTION_INTERVAL_MINUTES: int = 15
    DEFAULT_MIN_ENGAGEMENT: int = 10
    ENABLE_AI_FILTER: bool = False
    USE_TWITTER_API: bool = False
    ENABLE_SELENIUM_X: bool = False

    REDDIT_CLIENT_ID: str | None = None
    REDDIT_CLIENT_SECRET: str | None = None
    REDDIT_USER_AGENT: str = "signalfeed/0.1"

    TWITTER_BEARER_TOKEN: str | None = None

    LLM_API_KEY: str | None = None
    LLM_API_URL: str | None = None
    LLM_MODEL: str = "gpt-4o-mini"

    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_CHAT_ID: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)


settings = Settings()
