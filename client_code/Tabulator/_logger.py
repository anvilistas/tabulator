# SPDX-License-Identifier: MIT
# Copyright (c) 2022 Stu Cork

import sys
from datetime import datetime as _datetime

__version__ = "0.3.5"

NOTSET = 0
DEBUG = 1
INFO = 2
WARNING = 3
ERROR = 4
CRITICAL = 5

_level_to_name = {
    NOTSET: "NOTSET",
    DEBUG: "DEBUG",
    INFO: "INFO",
    WARNING: "WARNING",
    ERROR: "ERROR",
    CRITICAL: "CRITICAL",
}


def _get_level_name(level):
    return _level_to_name.get(level) or f"Level {level}"


class Logger:
    def __init__(
        self,
        name="root",
        level=NOTSET,
        format="{name}: {level}: {msg}",
        stream=None,
    ):
        self._validate(level, format, stream)
        self.name = name
        self.stream = stream or sys.stdout
        self.level = level
        self.format = format
        self.disabled = False

    def _validate(self, level, format, stream):
        if level not in _level_to_name:
            raise TypeError("level should be a valid logging level e.g. logging.DEBUG")
        if not isinstance(format, str):
            raise TypeError("format must be a string")
        if stream is not None and not (
            hasattr(stream, "write") and hasattr(stream, "flush")
        ):
            raise TypeError("a valid stream must have a .write() and .flush() method")

    def _write(self, msg):
        self.stream.write(msg + "\n")
        self.stream.flush()

    def get_format_params(self, *, level, msg, **params):
        now = _datetime.now()
        return {
            "name": self.name,
            "time": now.time(),
            "datetime": now,
            "date": now.date(),
            "level": _get_level_name(level),
            "msg": msg,
            **params,
        }

    def log(self, level, msg):
        """log a message at a given level"""
        if level < self.level or self.disabled:
            return
        params = self.get_format_params(level=level, msg=msg)
        out = self.format.format(**params)
        self._write(out)

    def debug(self, msg):
        self.log(DEBUG, msg)

    def info(self, msg):
        self.log(INFO, msg)

    def warning(self, msg):
        self.log(WARNING, msg)

    def error(self, msg):
        self.log(ERROR, msg)

    def critical(self, msg):
        self.log(CRITICAL, msg)

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} {self.name!r} ({_get_level_name(self.level)})>"
        )


logger = Logger("$Tabulator", format="{name}: {msg}", level=INFO)


def debug_logging(enable=True):
    logger.level = DEBUG if enable else INFO
