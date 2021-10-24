from pydantic import BaseSettings

class Config(BaseSettings):
  
  nullfs_api_url: str = "http://127.0.0.1:5000"
  nullfs_mount_point: str = "/home/flask/image/nullfs"

  class Config:
    extra = "ignore"
