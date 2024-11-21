from config import settings
from datetime import datetime
from fastapi import APIRouter, UploadFile, HTTPException
from pinecone import Pinecone
from AiServices.models import Delibera
from AiServices.embeddings import GetEmbedding, GetPineconeIndex
from AiServices.valutazione_classificazione import evaluate_classification_result
import json

router = APIRouter()

@router.post("/classificazione-aliquote")
async def classificazione_aliquote_ep(file: UploadFile):
    """
    Cerca record simili in Pinecone per ciascuna aliquota fornita in un file JSON.
    
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

        pc = Pinecone(api_key = settings.PINECONE_API_KEY)
        pinecone_index = GetPineconeIndex(pc)

        results = []
        for aliquota in delibera.aliquote:
            descrizione = aliquota.descrizione

            # Genera l'embedding per la descrizione
            query_vector = GetEmbedding(descrizione)

            # Esegui la ricerca in Pinecone
            search_results = pinecone_index.query(
                vector=query_vector,
                top_k=int(settings.PINECONE_NUM_RESULTS), 
                include_metadata=True  # Includi i metadati nel risultato
            )

            # Salva tutti i risultati trovati
            matches = []
            for match in search_results.get("matches", []):
                # Gestisci i metadati vuoti o nulli
                try:
                    imu_cod_alq_codice = int(match["metadata"].get("imuCodAlq_Codice", 0))  # Default a 0 se vuoto
                except ValueError:
                    imu_cod_alq_codice = 0

                try:
                    imu_cod_alq_sub = int(match["metadata"].get("imuCodAlq_Sub", 0))  # Default a 0 se vuoto
                except ValueError:
                    imu_cod_alq_sub = 0                

                matches.append({
                    "id": match["id"],
                    "score": match["score"],
                    "imuCodAlq_Codice": imu_cod_alq_codice,
                    "imuCodAlq_Sub": imu_cod_alq_sub,
                    "imuCodAlq_Descrizione": match["metadata"]["imuCodAlq_Descrizione"],
                })

            result_entry = {
                "aliquota": {
                    "valore": aliquota.valore,
                    "descrizione": aliquota.descrizione
                },
                "matches": matches  # Tutti i match trovati
            }

            # Valutazione dei risultati utilizzando un LLM
            evaluation_result = await evaluate_classification_result(aliquota.descrizione, matches)

            # Aggiungi la valutazione al risultato
            result_entry["classification_evaluation"] = evaluation_result.model_dump()

            results.append(result_entry)

        # Salva l'output in un file JSON
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            file_name = f"classificazione_aliquote_{delibera.comune}_{timestamp}.json"           
            file_path = f"{settings.FILE_OUT_DIR}/{file_name}"

            with open(file_path, "w", encoding="utf-8") as json_file:
                json.dump(results, json_file, ensure_ascii=False, indent=4)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Errore durante il salvataggio del file: {str(e)}")
        
        return {"results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
