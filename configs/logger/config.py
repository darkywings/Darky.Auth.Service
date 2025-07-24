from logger.formatters import DarkyConsoleFormatter, DarkyFileFormatter

LOGGER = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "file": {
            "()": DarkyFileFormatter,
            "fmt": "%(name)s | %(asctime)s | %(levelname)s | %(message)s"
        },
        "console": {
            "()": DarkyConsoleFormatter,
            "fmt": "%(name)s | %(asctime)s | %(levelname)s | %(message)s",
            "colored": True
        }
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "file",
            "filename": "data/darky.log",
            "backupCount": 1,
            "encoding": "utf-8"
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "console"
        }
    },
    "loggers": {
        "darky.users": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False
        },
        "darky.news": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False
        },
        "darky.admins": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}