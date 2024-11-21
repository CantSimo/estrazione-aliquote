from fastapi import APIRouter, UploadFile, HTTPException
from pinecone import Pinecone
from config import settings
from AiServices.embeddings import GetEmbedding, GetPineconeIndex
import pandas as pd
import io

router = APIRouter()

@router.post("/ingestion-aliquote")
async def ingestion_aliquote_ep(file: UploadFile):
    """
    Endpoint per elaborare un file CSV e caricare vettori in Pinecone.
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

        pc = Pinecone(api_key = settings.PINECONE_API_KEY)
        # pinecone_index = pc.Index(settings.PINECONE_OPENAI_INDEX)
        pinecone_index = GetPineconeIndex(pc)

        # embedding_model = OpenAIEmbeddings(model=settings.OPENAI_EMBEDDING_MODEL, openai_api_key=settings.OPENAI_API_KEY)

        # Itera su ogni riga del CSV
        for row_index, row in df.iterrows():
            # Estrai il valore della terza colonna 'imuCodAlq_Descrizione'
            descrizione = row['imuCodAlq_Descrizione']

            # Genera l'embedding
            #embedding = embedding_model.embed_query(descrizione)
            embedding = GetEmbedding(descrizione)

            # Prepara i metadati (tutti i valori della riga con i loro nomi di colonna)
            metadata = row.to_dict()

            # Inserisci il vettore nel database Pinecone
            pinecone_id = f"row-{row_index}"  # ID univoco
            pinecone_index.upsert([{
                "id": pinecone_id,
                "values": embedding,
                "metadata": metadata
            }])

        return {"message": "Tutti i vettori sono stati caricati in Pinecone."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

