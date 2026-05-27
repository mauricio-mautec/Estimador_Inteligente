import logging
from contextlib import contextmanager

import pandas as pd
import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)


class DatabaseModel:
    """Camada de acesso PostgreSQL.

    Chaves de mapeamento de coluna (colunas dict):
        produto          - coluna de nome do produto
        data             - coluna período/data
        quantidade_manha - coluna de quantidade matinal
        quantidade_tarde - coluna de quantidade da tarde
        total            - coluna de quantidade total
    """

    def __init__(self, dsn: str):
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

    def fetch_product_history(
        self,
        tabela: str,
        colunas: dict[str, str],
        produtos: list[str],
    ) -> pd.DataFrame:
        """Buscar o histórico de séries temporais para os produtos fornecidos.

        Retorna um DataFrame com colunas normalizadas para:
        data, produto, quantidade_manha, quantidade_tarde, total
        """
        col_produto = colunas["produto"]
        col_data = colunas["data"]
        col_manha = colunas.get("quantidade_manha")
        col_tarde = colunas.get("quantidade_tarde")
        col_total = colunas.get("total")

        select_cols = [col_data, col_produto]
        if col_manha:
            select_cols.append(col_manha)
        if col_tarde:
            select_cols.append(col_tarde)
        if col_total:
            select_cols.append(col_total)

        cols_sql = ", ".join(f'"{c}"' for c in select_cols)
        placeholders = ", ".join(["%s"] * len(produtos))
        query = f"""
            SELECT {cols_sql}
            FROM "{tabela}"
            WHERE "{col_produto}" IN ({placeholders})
            ORDER BY "{col_data}" ASC
        """

        with self._cursor() as cur:
            cur.execute(query, produtos)
            rows = cur.fetchall()

        df = pd.DataFrame([dict(r) for r in rows])

        rename = {col_data: "data", col_produto: "produto"}
        if col_manha:
            rename[col_manha] = "quantidade_manha"
        if col_tarde:
            rename[col_tarde] = "quantidade_tarde"
        if col_total:
            rename[col_total] = "total"

        df.rename(columns=rename, inplace=True)
        df["data"] = pd.to_datetime(df["data"])
        return df

    def fetch_all_products(self, tabela: str, colunas: dict[str, str]) -> list[str]:
        """Return distinct product names from the table."""
        col_produto = colunas["produto"]
        query = f'SELECT DISTINCT "{col_produto}" FROM "{tabela}" ORDER BY 1'
        with self._cursor() as cur:
            cur.execute(query)
            return [row[col_produto] for row in cur.fetchall()]
