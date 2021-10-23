from pydantic import BaseSettings

class Config(BaseSettings):
  
  turingbot_api_url: str = "http://openapi.tuling123.com/openapi/api/v2"
  turingbot_api_key: str
  daily_api_quota: int = 500

  strategy: str = "uniform"

  # UniformProb
  uniform_prob: float = 1/10

  class Config:
    extra = "ignore"
