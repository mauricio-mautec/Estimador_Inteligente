from pydantic import BaseModel

class UserMock(BaseModel):
    id: int
    name: str

async def valida_sessao_alfa() -> UserMock:
    """
    Retorna um usuário fictício para permitir que a API e o bot do Telegram
    funcionem sem exigir validação real de tokens do frontend.
    """
    return UserMock(id=1, name="Usuario Teste Telegram")
