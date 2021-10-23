from pydantic import BaseSettings

class Config(BaseSettings):
  
  turingbot_api_url: str = "http://openapi.tuling123.com/openapi/api/v2"
  turingbot_api_key: str
  daily_api_quota: int = 500

  strategy: str = "uniform_and_boost"

  # UniformProb
  uniform_prob: float = 1/20

  # UniformAndBoost
  boosted_prob: float = 4/5

  class Config:
    extra = "ignore"
