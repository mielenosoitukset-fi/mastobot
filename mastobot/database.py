from __future__ import annotations

import logging
import re
from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database


logger = logging.getLogger(__name__)


def redact_mongo_uri(uri: str) -> str:
    """Hide the password in a MongoDB URI before it is logged."""
    return re.sub(r"(://[^:/@]+):[^@]*@", r"\1:***@", uri)


class DatabaseManager:
    """Small local database helper for Mastobot.

    The standalone bot should not rely on the main application package or a
    globally installed helper. This keeps the repo self-contained and makes the
    systemd deployment predictable.
    """

    def __init__(self, mongo_uri: str, db_name: str):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self._client: Optional[MongoClient] = None

    def get_db(self) -> Database:
        if self._client is None:
            logger.info("Connecting Mastobot to MongoDB at %s", redact_mongo_uri(self.mongo_uri))
            self._client = MongoClient(self.mongo_uri)
        return self._client[self.db_name]
