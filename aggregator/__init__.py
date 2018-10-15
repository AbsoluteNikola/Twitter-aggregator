"""Aggregator module of twitter news aggregator.

This module pulls timelines of users, combining them together, extracting keywords and finally storing them in a database.
"""

__all__ = ["Twit", "run"]
__author__ = "Danil Doroshin and Nikolay Rulev"
__credits__ = ["Danil Doroshin", "Nikolay Rulev", "ООО Форензика"]
__version__ = "0.1"

from .twitterHandler import keep_twits_updated
from .cachingHandler import keep_cache_updated
from .Twit import Twit
from .User import User
