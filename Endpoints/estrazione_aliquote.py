from config import settings
from fastapi import APIRouter, UploadFile, HTTPException
from AiServices.models import Delibera
from LLMs.openai import openai_invoke
from Utils.files import leggi_file_txt, estrai_testo_pdf, sanitize_filename
from datetime import datetime
import langsmith as ls
import json
import os
import logging

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

    try:
        delibera_text = await estrai_testo_pdf(fileDelibera)
        system_content = leggi_file_txt(os.path.join(settings.BASE_DIR, "Files", "estrazione_aliquote_prompt_langchain.txt"))
        delibera = await openai_invoke(delibera_text, system_content, Delibera)
        
        # Salva l'output in un file JSON
        if settings.SAVE_OUTPUT:
            # Genera il nome del file in base al comune e alla data corrente
            comune = delibera.Comune if delibera.Comune else "sconosciuto"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            file_name = sanitize_filename(f"estrazione_aliquote_{comune}_{timestamp}.json")   
            file_path = os.path.join(settings.FILE_OUT_DIR, file_name) 
            
            with open(file_path, "w", encoding="utf-8") as json_file:
                json.dump(delibera.dict(by_alias=True), json_file, ensure_ascii=False, indent=4)
        
        return delibera.dict()
    except Exception as e:
        logging.exception(f"Errore durante l'invocazione dell'endpoint estrazione-aliquote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))