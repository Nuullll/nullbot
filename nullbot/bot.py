import nonebot
import config
import os
import sys

PACKAGE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(PACKAGE_DIR, os.pardir))
sys.path.append(ROOT_DIR)


TEST = False
PLUGINS = True


if __name__ == "__main__":
    nonebot.init(config)
    nonebot.load_builtin_plugins()

    if PLUGINS:
        nonebot.load_plugins(
            os.path.join(PACKAGE_DIR, 'basic'),
            'basic'
        )
        nonebot.load_plugins(
            os.path.join(PACKAGE_DIR, 'manager'),
            'manager'
        )
    
    if TEST:
        nonebot.load_plugins(
            os.path.join(PACKAGE_DIR, 'tests'),
            'tests'
        )

    nonebot.run()
