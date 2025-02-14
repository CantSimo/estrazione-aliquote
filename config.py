import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    CHROMA_NUM_RESULTS = int(os.getenv("CHROMA_NUM_RESULTS"))
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./Files/Database")

    # Distribuzione
    PORT = int(os.getenv("PORT", 9091))  # Porta di default: 9091
    BASE_DIR = os.path.dirname(__file__)

    # OpenAI parameters
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL")

    # Huggin Face parameters
    HUGGING_FACE_EMBEDDING_MODEL = os.getenv("HUGGING_FACE_EMBEDDING_MODEL")

    # output folder
    SAVE_OUTPUT = os.getenv("SAVE_OUTPUT", "false").lower() in ("true", "1", "yes")
    FILE_OUT_DIR = os.getenv("FILE_OUT_DIR")
    if not os.path.exists(FILE_OUT_DIR):
        os.makedirs(FILE_OUT_DIR)

    # Embedding Model
    # 0 = OpenAI
    # 1 = Hugging Face 
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

settings = Settings()
