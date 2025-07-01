import logging.config, logging

class DarkyLogger:
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "%(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "console"
            }
        },
        "loggers": {
            "main": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False
            }
        }
    }

    def __init__(self, logger_name:str=None, configuration:dict=None, ansi:bool=True) -> None:

        r'''
        Класс DarkyLogger позволяет удобно и быстро инициализировать работу логгера logging

        :param logger_name: используется для присвоения уникального имени логгеру\
        (видно при использовании в форматировании %(name)s)
        :type logger_name: str 
        
        :param configuration: позволяет гибко настроить конфигурацию логгера
        (см. https://docs.python.org/3/library/logging.config.html#configuration-dictionary-schema)
        :type configuration: dict

        Не смотря на то что некоторые методы не отображаются, класс поддерживает следующие методы логгирования:
        - debug()
        - info()
        - warning()
        - error()
        - critical()

        Работающих по аналогии со стандартным logging

        Пример::

            >>> test_logger = DarkyLogger("test")
            >>> test_logger.info("Test message")
            INFO - Test message

        ``bool exc_info`` при вызове какого либо из уровня логгирования включит отображение последнего traceback:

            >>> try:
            ...     raise Exception
            >>> except Exception as ex:
            ...     test_logger.error("We got an error", exc_info=True)
            ERROR - We got an error
            Traceback (most recent call last):
              File "test.py", line 2, in main
                raise Exception
            Exception

        '''
        
        if logger_name is None:
            logger_name = "null"

        if configuration is None:
            configuration = DarkyLogger.config

        logging.config.dictConfig(configuration)
        self.__logger__ = logging.getLogger(logger_name)
        self.__logger__.debug(f"DarkyLogger initiated")
    
    def __getattr__(self, name):

        if name not in ["debug", "info", "warning", "error", "critical"]:
            self.__logger__.warning(f"'DarkyLogger' has no attribute '{name}'. \"INFO\" is used instead.")
            name = "info"
        attr = getattr(self.__logger__, name)
        return attr
    
    def get_logger(self) -> logging.Logger:

        '''
        Клонирует уже созданный ранее логгер для его использования в других модулях
        '''

        self.__logger__.debug(f"'DarkyLogger.get_logger()' has been called")
        return self.__logger__