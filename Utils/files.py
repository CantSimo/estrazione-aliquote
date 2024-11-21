import fitz  # PyMuPDF
from fastapi import UploadFile
import json

def leggi_file_pdf(percorso_pdf):
    """
    Estrae il testo leggibile da un file PDF.

    Args:
        percorso_pdf (str): Il percorso del file PDF da processare.

    Returns:
        str: Il testo estratto dal PDF, con ogni pagina separata da un'intestazione.
    """
    # Apri il documento PDF
    documento = fitz.open(percorso_pdf)
    
    # Inizializza una variabile per raccogliere tutto il testo
    testo_completo = ""
    
    # Itera su ogni pagina del PDF
    for numero_pagina in range(documento.page_count):
        pagina = documento.load_page(numero_pagina)  # Carica la pagina
        testo = pagina.get_text()  # Estrai il testo
        testo_completo += f"\n--- Pagina {numero_pagina + 1} ---\n"  # Separa le pagine
        testo_completo += testo
    
    documento.close()  # Chiudi il documento
    return testo_completo

async def estrai_testo_pdf(file: UploadFile):
    """
    Estrae il testo leggibile da un file PDF caricato come UploadFile.

    Args:
        file (UploadFile): Il file PDF caricato come oggetto UploadFile.

    Returns:
        str: Il testo estratto dal PDF, con ogni pagina separata da un'intestazione.
    """
    # Leggi il contenuto del file PDF
    pdf_bytes = await file.read()
    
    # Apri il documento PDF dai byte
    documento = fitz.open("pdf", pdf_bytes)
    
    # Inizializza una variabile per raccogliere tutto il testo
    testo_completo = ""
    
    # Itera su ogni pagina del PDF
    for numero_pagina in range(documento.page_count):
        pagina = documento.load_page(numero_pagina)  # Carica la pagina
        testo = pagina.get_text()  # Estrai il testo
        #testo_completo += f"\n--- Pagina {numero_pagina + 1} ---\n"  # Separa le pagine
        testo_completo += testo
    
    documento.close()  # Chiudi il documento
    return testo_completo

def leggi_file_txt(percorso_file):
    """
    Legge il contenuto di un file .txt e lo restituisce come stringa.

    Args:
        percorso_file (str): Il percorso del file .txt da leggere.

    Returns:
        str: Il contenuto del file .txt.
    """
    with open(percorso_file, "r", encoding="utf-8") as file:  # Apri il file in modalità lettura
        contenuto = file.read()  # Leggi tutto il contenuto del file
    return contenuto

def leggi_file_json(percorso):
    with open(percorso, 'r', encoding='utf-8') as file:
        return json.load(file)