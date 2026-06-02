import logging
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

from .tabela_dinamica import TabelaDinamica

logger = logging.getLogger(__name__)


class DatabaseConnection:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn
        self._conn: psycopg2.extensions.connection | None = None

    def connect(self) -> None:
        self._conn = psycopg2.connect(self._dsn)
        logger.info("Connected to PostgreSQL")

    def close(self) -> None:
        if self._conn and not self._conn.closed:
            self._conn.close()

    @contextmanager
    def _cursor(self):
        with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            yield cur

    @property
    def tabela_dinamica(self) -> TabelaDinamica:
        return TabelaDinamica(self._conn)
