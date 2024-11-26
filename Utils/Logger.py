from config import settings
import logging
import os

# Metodo per configurare il logger
def configura_logger():
    log_file_path = os.path.join(settings.FILE_OUT_DIR, "api_errors.log")
    logging.basicConfig(filename=log_file_path, level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")