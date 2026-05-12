# pyrefly: ignore [missing-import]
from fastapi import FastAPI

app = FastAPI(title="Estimador Inteligente - Grupo Charlie")

@app.get("/")
async def root():
    return {"message": "API do Grupo Charlie rodando com sucesso! 🚀"}

@app.get("/status")
async def status():
    return {"status": "ok"}
