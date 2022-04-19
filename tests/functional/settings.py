from pydantic import BaseSettings, Field


class Setting(BaseSettings):
    ELASTICSEARCH_HOST: str = Field(..., env='ELASTICSEARCH_HOST')
    ELASTICSEARCH_PORT: int = Field(..., env='ELASTICSEARCH_PORT')
    ELASTICSEARCH_URL: str = Field(..., env='ELASTICSEARCH_URL')

    REDIS_HOST: str = Field(..., env='REDIS_HOST')
    REDIS_PORT: int = Field(..., env='REDIS_PORT')

    FASTAPI_HOST: str = Field(..., env='FASTAPI_HOST')
    FASTAPI_PORT: int = Field(..., env='FASTAPI_PORT')
    FASTAPI_URL: str = Field(..., env='FASTAPI_URL')

    class Config:
        case_sentive = False
        env_file = '../.env'
