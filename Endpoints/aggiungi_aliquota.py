from config import settings
from fastapi import APIRouter, UploadFile, HTTPException
from AiServices.models import Delibera, Aliquota
from LLMs.openai import openai_invoke
from Utils.files import leggi_file_txt, estrai_testo_pdf, sanitize_filename
from datetime import datetime
from AiServices.models import NewAliquota
from AiServices.embeddings import EmbedText
import langsmith as ls
import json
import os
import logging
import csv
import chromadb


router = APIRouter()

@router.post("/aggiungi-aliquota")
@ls.traceable(tags=["aggiungi-aliquota"])
async def aggiungi_aliquota_ep(newAliquota: NewAliquota):
    #codice + fattispecie principale + fattispecie personalizzata
    # Path to the CSV file
    current_dir = os.path.dirname(__file__)
    csv_path = os.path.join(current_dir, '../Files/codici_aliquote.csv')

    # Check if the file exists
    file_exists = os.path.isfile(csv_path)

    # Open the CSV file in append mode
    with open(csv_path, mode='a', newline='\n', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        
        # Write the new aliquota data
        writer.writerow([
            newAliquota.Codice, newAliquota.SubCodice, newAliquota.FattispeciePersonalizzata, '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''   
        ])

    # Inserimento del nuovo record anche nel database vettoriale esistente
    try:
        chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)  
        collection_name = "aliquote_collection"
        collection = chroma_client.get_collection(name=collection_name)

        # Generazione embedding e metadati
        descrizione = newAliquota.FattispeciePersonalizzata
        embedding = EmbedText(descrizione)
        metadata = {
            "Codice": newAliquota.Codice,
            "SubCodice": newAliquota.SubCodice,
            "FattispeciePersonalizzata": newAliquota.FattispeciePersonalizzata
        }
        vector_id = f"aliquota-{newAliquota.Codice}-{newAliquota.SubCodice}"

        collection.add(
            ids=[vector_id],
            embeddings=[embedding],
            metadatas=[metadata]
        )
    except Exception as e:
        logging.exception(f"Errore durante l'inserimento nel database vettoriale: {str(e)}")
        raise HTTPException(status_code=500, detail="Errore durante il salvataggio nel database vettoriale.")
    
    return {"message": "Aliquota aggiunta con successo e salvata nel database vettoriale."}
