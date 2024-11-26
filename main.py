from config import settings
from fastapi import FastAPI
from Endpoints import estrazione_aliquote, ingestion_aliquote, classificazione_aliquote
from Utils.Logger import configura_logger
import uvicorn

configura_logger()

app = FastAPI(title="BNX AI Estrazione Aliquote API")

# Includi il router definito nel file estrazione_aliquote_ep.py
app.include_router(ingestion_aliquote.router)
app.include_router(estrazione_aliquote.router)
app.include_router(classificazione_aliquote.router)

PORT = settings.PORT

if __name__ == "__main__":
    uvicorn.run("main:app", port=PORT, reload=True)
    