from pathlib import Path
import os

class LoggingConfig:
    ROOT_DIR = Path(__file__).parent.parent

    LOG_DIR = os.path.join(ROOT_DIR,"logs")

# LoggingConfig.LOG_DIR.mkdir(parents=True, exist_ok=True)
def main():
    a = LoggingConfig()
    print(type(a.ROOT_DIR),a.ROOT_DIR)
    print(a.LOG_DIR, type(a.LOG_DIR))
if __name__ == '__main__':
    main()
