class MockConnection:
    """
    Uma conexão simulada para o PostgreSQL.
    Permite que os métodos fetchval, execute, etc., sejam chamados
    sem levantar exceções de rede ou banco de dados indisponível.
    """
    async def fetchval(self, query: str, *args):
        # Retorna None para indicar que nenhum modelo real foi encontrado,
        # permitindo que o predictor utilize a predição mockada em vez de falhar.
        return None

    async def execute(self, query: str, *args):
        return "SELECT 0"

    async def fetch(self, query: str, *args):
        return []

    async def fetchrow(self, query: str, *args):
        return None

async def get_connection():
    """
    Retorna a conexão simulada.
    """
    return MockConnection()
