from config import settings
from datetime import datetime
from fastapi import APIRouter, UploadFile, HTTPException
import chromadb
from AiServices.models import Delibera
from AiServices.embeddings import EmbedText
from AiServices.evaluation import aliquota_evaluation
from Utils.files import sanitize_filename
import os
import json
import langsmith as ls
import logging

router = APIRouter()

def safe_int(value, default=0):
    """
    Converte value in intero, restituendo default se value è una stringa vuota, None o non convertibile.
    """
    try:
        if value is None or (isinstance(value, str) and value.strip() == ""):
            return default
        return int(value)
    except (ValueError, TypeError):
        return default
        
@router.post("/classificazione-aliquote")
@ls.traceable(tags=["classificazione-aliquote"])
async def classificazione_aliquote_ep(file: UploadFile):
    """
    Cerca record simili in database vettoriale per ciascuna aliquota fornita in un file JSON.
    
    Args:
        file (UploadFile): File JSON contenente un oggetto Delibera.
        
    Returns:
        dict: Una lista di risultati con i record più simili.
    """
    # Verifica il tipo di file
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Il file deve essere in formato JSON.")

    try:
        # Leggi il contenuto del file
        content = await file.read()
        delibera_data = json.loads(content)

        # Convalida il contenuto
        try:
            delibera = Delibera(**delibera_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Formato JSON non valido: {str(e)}")

        # Inizializza il client di ChromaDB e ottieni la collection
        chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        collection = chroma_client.get_or_create_collection(name="aliquote_collection")

        results = []
        for aliquota in delibera.Aliquote:
            descrizione = aliquota.fattispeciePrincipale + " " + aliquota.fattispeciePersonalizzata

            # Genera l'embedding per la descrizione
            query_vector = EmbedText(descrizione)

            # Definisci i filtri per i metadati
#            metadata_filters = {
#                "imuCodAlq_Codice": {"$eq": aliquota.Filtra()},  # Esempio di filtro per imuCodAlq_Codice
#            }

#            # Esegui la ricerca in Chroma
#            search_results = collection.query(
#                query_embeddings=[query_vector],
#                n_results=settings.CHROMA_NUM_RESULTS,
#                where=metadata_filters
#            )

            # Esegui la ricerca in Chroma
            search_results = collection.query(
                query_embeddings=[query_vector],
                n_results=settings.CHROMA_NUM_RESULTS
            )

            # Processa i risultati
            matches = []
            for idx, doc_id in enumerate(search_results["ids"][0]):
                metadata = search_results["metadatas"][0][idx]

                # Gestione dei metadati mancanti
                imu_cod_alq_codice = safe_int(metadata.get("imuCodAlq_Codice", 0))
                imu_cod_alq_sub = safe_int(metadata.get("imuCodAlq_Sub", 0))

                matches.append({
                    "id": doc_id,
                    "score": search_results["distances"][0][idx],
                    "imuCodAlq_Codice": imu_cod_alq_codice,
                    "imuCodAlq_Sub": imu_cod_alq_sub,
                    "imuCodAlq_Descrizione": metadata.get("imuCodAlq_Descrizione", "")
                })

            result_entry = {
                "aliquota": {
                    "valore": aliquota.valore,
                    "fattispeciePrincipale": aliquota.fattispeciePrincipale,
                    "fattispeciePersonalizzata": aliquota.fattispeciePersonalizzata
                },
                "matches": matches  # Tutti i match trovati
            }

            # Valutazione dei risultati utilizzando un LLM
            evaluation_result = await aliquota_evaluation(descrizione, matches)

            # Aggiungi la valutazione al risultato
            result_entry["classification_evaluation"] = evaluation_result.model_dump()

            results.append(result_entry)

        # Salva l'output in un file JSON
        if settings.SAVE_OUTPUT:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            file_name = sanitize_filename(f"classificazione_aliquote_{delibera.Comune}_{timestamp}.json")
            file_path = os.path.join(settings.FILE_OUT_DIR, file_name)

            with open(file_path, "w", encoding="utf-8") as json_file:
                json.dump(results, json_file, ensure_ascii=False, indent=4)

        return {"results": results}

    except Exception as e:
        logging.exception(f"Errore durante l'invocazione dell'endpoint classificazione-aliquote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
