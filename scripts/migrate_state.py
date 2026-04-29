#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

from pymongo import MongoClient, ReplaceOne

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import Config


COLLECTIONS = (
    "posted_events",
    "mastobot_meta",
    "mastobot_subscriptions",
)


def _copy_collection(source_db, target_db, name: str, batch_size: int = 500) -> int:
    ops = []
    copied = 0
    for doc in source_db[name].find({}):
        ops.append(ReplaceOne({"_id": doc["_id"]}, doc, upsert=True))
        if len(ops) >= batch_size:
            target_db[name].bulk_write(ops, ordered=False)
            copied += len(ops)
            ops = []
    if ops:
        target_db[name].bulk_write(ops, ordered=False)
        copied += len(ops)
    return copied


def _counts(db, collections: Iterable[str]) -> dict[str, int]:
    return {name: db[name].count_documents({}) for name in collections}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy or verify Mastobot state so cutover from the main repo does not repost demos."
    )
    parser.add_argument("--source-uri", default=Config.STATE_SOURCE_MONGO_URI)
    parser.add_argument("--source-db", default=Config.STATE_SOURCE_DBNAME)
    parser.add_argument("--target-uri", default=Config.MONGO_URI)
    parser.add_argument("--target-db", default=Config.MONGO_DBNAME)
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Do not copy documents; only print whether source/target state is already aligned.",
    )
    args = parser.parse_args()

    if not args.source_uri or not args.target_uri:
        raise SystemExit(
            "Missing MongoDB connection details. Set MASTOBOT_CONFIG or pass --source-uri/--target-uri explicitly."
        )
    if not args.source_db or not args.target_db:
        raise SystemExit(
            "Missing MongoDB database names. Set MASTOBOT_CONFIG or pass --source-db/--target-db explicitly."
        )

    source = MongoClient(args.source_uri)[args.source_db]
    target = MongoClient(args.target_uri)[args.target_db]

    print(f"Source: {args.source_uri}/{args.source_db}")
    print(f"Target: {args.target_uri}/{args.target_db}")

    if args.source_uri == args.target_uri and args.source_db == args.target_db:
        print("Source and target are identical. Existing Mastobot state will be reused directly.")
        print(_counts(target, COLLECTIONS))
        return 0

    if args.verify_only:
        print("Source counts:", _counts(source, COLLECTIONS))
        print("Target counts:", _counts(target, COLLECTIONS))
        return 0

    for name in COLLECTIONS:
        copied = _copy_collection(source, target, name)
        print(f"{name}: upserted {copied} documents")

    print("Target counts:", _counts(target, COLLECTIONS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
