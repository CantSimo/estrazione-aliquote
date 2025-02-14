from config import settings
from fastapi import APIRouter, UploadFile, HTTPException
from AiServices.embeddings import EmbedText
import logging
import pandas as pd
import io
import chromadb

router = APIRouter()
@router.post("/ingestion-aliquote")
async def ingestion_aliquote_ep(file: UploadFile):
    """
    Endpoint per elaborare un file CSV e caricare vettori in Chroma.
    Args:
        file (UploadFile): File CSV ricevuto tramite l'endpoint.
    Returns:
        dict: Messaggio di successo o errore.
    """
    # Verifica il tipo di file
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Il file deve essere un CSV.")
       
    try:
        # Leggi il contenuto del file CSV
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode("utf-8")), sep=";")

        # Colonne obbligatorie
        colonne_obbligatorie = ['imuCodAlq_Codice', 'imuCodAlq_Sub', 'imuCodAlq_Descrizione']

        # Controlla che tutte le colonne obbligatorie siano presenti
        colonne_mancanti = [col for col in colonne_obbligatorie if col not in df.columns]
        if colonne_mancanti:
            raise HTTPException(
                status_code=400, 
                detail=f"Le seguenti colonne obbligatorie sono mancanti: {', '.join(colonne_mancanti)}"
            )
        
        # Sostituisci NaN nei metadati con stringa vuota
        df = df.fillna("")

        # Inizializza il client di Chroma e recupera/crea la collection
        chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)  
        collection_name = "aliquote_collection"
        try:
            collection = chroma_client.get_collection(name=collection_name)
        except Exception:
            collection = chroma_client.create_collection(name=collection_name)

        # Prepara le liste per accumulare gli ID, gli embeddings e i metadati
        ids = []
        embeddings_list = []
        metadatas_list = []
        
        # Itera su ogni riga del CSV
        for row_index, row in df.iterrows():
            # Estrai il valore della colonna 'imuCodAlq_Descrizione'
            descrizione = row['imuCodAlq_Descrizione']

            # Genera l'embedding (assicurati che EmbedText restituisca un vettore compatibile)
            embedding = EmbedText(descrizione)

            # Prepara i metadati (tutti i valori della riga con i loro nomi di colonna)
            metadata = row.to_dict()

            # Crea un ID univoco per il vettore
            vector_id = f"row-{row_index}"

            ids.append(vector_id)
            embeddings_list.append(embedding)
            metadatas_list.append(metadata)
        
        # Aggiungi tutti i vettori nella collection Chroma
        collection.add(
            ids=ids,
            embeddings=embeddings_list,
            metadatas=metadatas_list
        )

        return {"message": "Tutti i vettori sono stati caricati in Chroma."}

    except Exception as e:
        logging.exception(f"Errore durante l'invocazione dell'endpoint ingestion-aliquote: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
