from pydantic import BaseSettings

class Config(BaseSettings):
  
  repeat_threhold: int = 2
  cache_capacity: int = 4

  class Config:
    extra = "ignore"
