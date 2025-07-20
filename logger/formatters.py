import re
import logging
from typing import Literal
from copy import copy

from uvicorn.logging import AccessFormatter

from .darky_visual import STYLE, FG, BG


class DarkyConsoleFormatter(logging.Formatter):

    levelname_colors = {
        "DEBUG": f"{FG.BLUE}DEBUG{STYLE.RESET}",
        "INFO": f"{FG.GREEN}INFO{STYLE.RESET}",
        "WARNING": f"{FG.YELLOW}WARNING{STYLE.RESET}",
        "ERROR": f"{FG.BOLD}{FG.RED}ERROR{STYLE.RESET}",
        "CRITICAL": f"{FG.BOLD}{BG.RED}{FG.WHITE}CRITICAL{STYLE.RESET}"
    }

    asctime_color = f"{FG.CUSTOM_COLOR("#DDD")}%s{STYLE.RESET}"
    name_color = f"{FG.CUSTOM_COLOR("#888")}%s{STYLE.RESET}"

    def __init__(
            self,
            fmt: str | None = None,
            datefmt: str | None = None,
            style: Literal["%", "{", "$"] = "%",
            colored: Literal[True, False] = False,
            color_core_name: Literal[True, False] = False
    ):
        '''
        Initializes the console formatter for logging module

        :param fmt: Log message format
        :type fmt: str | None

        :param datefmt: Time format
        :type datefmt: str | None

        :param style: Format style
        
        :param colored: Sets the colors for log message
        :type colored: bool
        '''
        self.colored = colored
        self.color_core_name = color_core_name
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
    
    def color_levename(self, levelname: str) -> str:
        '''
        Applies colors to the levelname
        '''
        if self.colored:
            return self.levelname_colors[levelname]
        return levelname
    
    def formatTime(self, record, datefmt = None):
        '''
        Applies color to the asctime
        '''
        time_str = super().formatTime(record, datefmt)
        if self.colored:
            return self.asctime_color % time_str
        return time_str

    def formatException(self, ei):
        '''
        Applies colors to the exception's traceback
        '''
        if self.colored:
            return f"{FG.RED}{super().formatException(ei)}{STYLE.RESET}"
        return super().formatException(ei)

    def format(self, record):
        '''
        Formatting the log message
        '''
        record_copy = copy(record)
        if self.colored:
            if self.color_core_name and "twilight" in record_copy.name:
                record_copy.name = f"{STYLE.GRADIENT(f"{record_copy.name}", ["#44F", "#A6F"])}{STYLE.RESET}"
            else:
                record_copy.name = self.name_color % record_copy.name
            if record_copy.levelname == "CRITICAL":
                record_copy.msg = f"{FG.RED}{record_copy.msg}{STYLE.RESET}"
            record_copy.levelname = self.color_levename(record_copy.levelname)
        record_copy.name = record_copy.name + " " * (15 - len(record.name))
        record_copy.levelname = record_copy.levelname + " " * (8 - len(record.levelname))
        return super().format(record_copy)
        

class DarkyFileFormatter(logging.Formatter):

    def __init__(
            self,
            fmt: str | None = None,
            datefmt: str | None = None,
            style: Literal["%", "{", "$"] = "%",
    ):
        '''
        Initializes the console formatter for logging module

        :param fmt: Log message format
        :type fmt: str | None

        :param datefmt: Time format
        :type datefmt: str | None

        :param style: Format style
        '''
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
    
    def formatTime(self, record, datefmt = None):
        return super().formatTime(record, datefmt)
    
    def formatException(self, ei):
        return super().formatException(ei)

    def format(self, record):
        '''
        Removes the colors for file logging
        '''
        record_copy = copy(record)
        record_copy.levelname =      re.sub(r'\033\[.*?m', '', record_copy.levelname)
        record_copy.msg =            re.sub(r'\033\[.*?m', '', record_copy.msg)
        record_copy.name =           re.sub(r'\033\[.*?m', '', record_copy.name)

        record_copy.name = record_copy.name + " " * (15 - len(record.name))
        record_copy.levelname = record_copy.levelname + " " * (8 - len(record.levelname))

        return super().format(record_copy)

class UvicornAccessFormatter(DarkyConsoleFormatter, AccessFormatter):
    pass