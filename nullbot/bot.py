import nonebot
import config
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(ROOT_DIR)

if __name__ == "__main__":
    nonebot.init(config)
    nonebot.load_builtin_plugins()
    nonebot.load_plugins(
        os.path.join(os.path.dirname(__file__), 'basic'),
        'basic'
    )
    nonebot.load_plugins(
        os.path.join(os.path.dirname(__file__), 'tests'),
        'tests'
    )
    nonebot.run()
