import os
from dotenv import load_dotenv

load_dotenv()

class Settings:

    # Distribuzione
    PORT = int(os.getenv("PORT", 9091))  # Porta di default: 9091
    
    # OpenAI parameters
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")

    # Huggin Face parameters
    HUGGING_FACE_EMBEDDING_MODEL = os.getenv("HUGGING_FACE_EMBEDDING_MODEL")

    # Vector database
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_OPENAI_INDEX = os.getenv("PINECONE_OPENAI_INDEX")
    PINECONE_HUGGING_FACE_INDEX = os.getenv("PINECONE_HUGGING_FACE_INDEX")
    PINECONE_NUM_RESULTS = os.getenv("PINECONE_NUM_RESULTS")

    # output folder
    FILE_OUT_DIR = os.getenv("FILE_OUT_DIR")

    # Embedding Model
    # 0 = OpenAI
    # 1 = Hugging Face 
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

settings = Settings()
