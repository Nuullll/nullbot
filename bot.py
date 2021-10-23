import nonebot
from nonebot.adapters.cqhttp import Bot as NullBot

nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter("cqhttp", NullBot)
nonebot.load_builtin_plugins()
nonebot.load_plugins("nullbot/plugins")

if __name__ == "__main__":
  nonebot.run()
