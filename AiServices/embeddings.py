from config import settings
from langchain_openai import OpenAIEmbeddings
from transformers import AutoModel, AutoTokenizer
from pinecone import Pinecone
import torch

if settings.EMBEDDING_MODEL == '0':
    # OpenAI Embedding model (caricato una sola volta)
    openai_embedding_model = OpenAIEmbeddings(model=settings.OPENAI_EMBEDDING_MODEL, openai_api_key=settings.OPENAI_API_KEY)
    
if settings.EMBEDDING_MODEL == '1':
    # Configurazione di BERT (caricata una sola volta)
    bert_tokenizer = AutoTokenizer.from_pretrained(settings.HUGGING_FACE_EMBEDDING_MODEL)
    bert_model = AutoModel.from_pretrained(settings.HUGGING_FACE_EMBEDDING_MODEL)

def generate_bert_embedding(text: str):
    """
    Genera embedding con BERT.
    Args:
        text (str): Il testo per il quale generare gli embedding.
    Returns:
        list: L'embedding generato.
    """
    inputs = bert_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = bert_model(**inputs)
    # Media dei token come embedding
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().tolist()
    return embedding

def EmbedText(text: str):
    """
    Genera embedding per il testo fornito utilizzando il modello specificato in settings.
    Args:
        text (str): Il testo per il quale generare gli embedding.
    Returns:
        list: L'embedding generato.
    Raises:
        ValueError: Se EMBEDDING_MODEL ha un valore non supportato.
    """

    # Embedding Model
    # 0 = OpenAI
    # 1 = Hugging Face 

    if settings.EMBEDDING_MODEL == '0':
        Embedding = openai_embedding_model.embed_query(text)
    elif settings.EMBEDDING_MODEL == '1':
        Embedding = generate_bert_embedding(text)
    else:
        raise ValueError("EMBEDDING_MODEL non supportato. Usa 0 (OpenAI) o 1 (Hugging Face).")        
    
    return Embedding

def GetPineconeIndex(pc: Pinecone):
    """
    Ritorna il nome del Database di Pinecone utilizzando il modello specificato in settings.
        Embedding Model: 0 = OpenAI; 1 = Hugging Face 
    Returns:
        list: Il nome del database.
    Raises:
        ValueError: Se EMBEDDING_MODEL ha un valore non supportato.
    """

    if settings.EMBEDDING_MODEL == '0':
        index = pc.Index(settings.PINECONE_OPENAI_INDEX)
    elif settings.EMBEDDING_MODEL == '1':
        index = pc.Index(settings.PINECONE_HUGGING_FACE_INDEX)
    else:
        raise ValueError("EMBEDDING_MODEL non supportato. Usa 0 (OpenAI) o 1 (Hugging Face).")        
    
    return index