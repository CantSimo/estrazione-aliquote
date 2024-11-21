from fastapi import APIRouter, UploadFile, HTTPException
from AiServices.estrazione_aliquote import estrazione_aliquote_OpenAi, estrazione_aliquote_LangChain_ChatOpenAi
from datetime import datetime
from config import settings
import json
import langsmith as ls

router = APIRouter()

@router.post("/estrazione-aliquote")
@ls.traceable(tags=["estrazione-aliquote"])
async def estrazione_aliquote_ep(fileDelibera: UploadFile):
    """
    Endpoint per estrarre aliquote da delibere comunali
    Args:
        file (UploadFile): Delibera in formato PDF.
    Returns:
        dict: oggetto Delibera
    """

    if fileDelibera.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # delibera = await estrazione_aliquote_OpenAi(fileDelibera)
    delibera = await estrazione_aliquote_LangChain_ChatOpenAi(fileDelibera)
    
    # Genera il nome del file in base al comune e alla data corrente
    comune = delibera.comune if delibera.comune else "sconosciuto"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    file_name = f"estrazione_aliquote_{comune}_{timestamp}.json"
    
    file_path = f"{settings.FILE_OUT_DIR}/{file_name}"

    # Salva l'output in un file JSON
    try:
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(delibera.dict(by_alias=True), json_file, ensure_ascii=False, indent=4)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante il salvataggio del file: {str(e)}")
    
    return delibera.dict()