import sys
from loguru import logger
from src.gui import main

logger.remove()
logger.add(sys.stderr, level="INFO")


if __name__ == "__main__":
	main()
