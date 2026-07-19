import os
from typing import Optional
import pymysql
import pymysql.cursors
from dotenv import load_dotenv
from dbutils.pooled_db import PooledDB

load_dotenv()

# ---------------------------------------------------------------------------
# Connection pool — keeps persistent connections to MySQL so each API call
# does NOT pay the TCP + auth handshake cost and avoids "session timeout"
# errors that happen when a fresh connection is left idle too long.
# ---------------------------------------------------------------------------
_pool: Optional[PooledDB] = None


def _get_pool() -> PooledDB:
    """Lazily create the shared connection pool (thread-safe singleton)."""
    global _pool
    if _pool is None:
        _pool = PooledDB(
            creator=pymysql,
            mincached=2,          # keep at least 2 connections alive
            maxcached=10,         # at most 10 idle connections cached
            maxconnections=20,    # hard cap on concurrent connections
            blocking=True,        # block instead of raising when pool is full
            ping=1,               # ping before handing out a connection
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "160747"),
            database=os.getenv("DB_NAME", "nakorndata"),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
    return _pool


def get_connection():
    """Borrow a connection from the pool (utf8mb4, dict rows)."""
    return _get_pool().connection()
