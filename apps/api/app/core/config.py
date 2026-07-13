from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "OrientaIA API"
    environment: str = "development"
    database_url: str = Field(
        default="sqlite+aiosqlite:///./orientaia.db", alias="DATABASE_URL"
    )
    sync_database_url: str = Field(default="sqlite:///./orientaia.db", alias="SYNC_DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field(default="password", alias="NEO4J_PASSWORD")
    jwt_secret_key: str = Field(default="change_me", alias="JWT_SECRET_KEY")
    jwt_refresh_secret_key: str = Field(default="change_me_refresh", alias="JWT_REFRESH_SECRET_KEY")
    access_token_expire_minutes: int = Field(default=20, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=14, alias="REFRESH_TOKEN_EXPIRE_DAYS")
    web_origin: str = Field(default="http://localhost:3000", alias="WEB_ORIGIN")
    llm_provider: str = Field(default="none", alias="LLM_PROVIDER")
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_model: str = Field(default="", alias="LLM_MODEL")
    llm_base_url: str = Field(default="", alias="LLM_BASE_URL")
    experimental_expert_weight: float = Field(default=0.30, alias="EXPERIMENTAL_EXPERT_WEIGHT")
    experimental_ml_weight: float = Field(default=0.55, alias="EXPERIMENTAL_ML_WEIGHT")
    experimental_graph_weight: float = Field(default=0.15, alias="EXPERIMENTAL_GRAPH_WEIGHT")
    single_user_mode: bool = Field(default=True, alias="SINGLE_USER_MODE")
    demo_user_email: str = Field(default="demo@orientaia.local", alias="DEMO_USER_EMAIL")
    demo_user_name: str = Field(default="Estudiante Demo", alias="DEMO_USER_NAME")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
