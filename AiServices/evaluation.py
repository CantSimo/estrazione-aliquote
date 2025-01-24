from AiServices.models import ClassificationEvaluation
from AiServices.models import MatchFounded
from LLMs.openai import openai_invoke

async def aliquota_evaluation(descrizione_aliquota, matches):
    """
    Valuta quale dei matches trovati corrisponde o riassume meglio la descrizione dell'aliquota.
    
    Args:
        descrizione_aliquota (str): La descrizione dell'aliquota in delibera.
        matches (list): Lista di possibili corrispondenze trovate in database vettoriale.
        
    Returns:
        ClassificationEvaluation: Risultato della valutazione.
    """
    
    # Definisci il contenuto del role system per guidare meglio il comportamento del modello
    systemcontent = (
        "Sei un assistente esperto nella classificazione di aliquote fiscali IMU. "
        "Il tuo compito è identificare quale delle descrizioni fornite si avvicina di più o riassume meglio la descrizione fornita dell'aliquota. "
        "Se nessuna corrisponde adeguatamente, restituisci il valore 0. "
    )

    # Costruisci il prompt per l'LLM
    promptUser = (
        f"La descrizione dell'aliquota è: '{descrizione_aliquota}'.\n"
        f"Valuta quale tra le seguenti descrizioni corrisponde meglio: \n"
    )
    for i, match in enumerate(matches):
        promptUser += f"{i + 1}. {match['imuCodAlq_Descrizione']}\n"

    promptUser += "Restituisci il numero della descrizione che corrisponde o riassume meglio, oppure 0 se nessuna è appropriata."
    
    # Chiamata al modello di linguaggio per la valutazione
    best_match = await openai_invoke(promptUser, systemcontent, MatchFounded)
    best_match_index = best_match.NumeroRiga
    best_match_index = best_match_index -1

    if best_match_index >= 0 and best_match_index < len(matches):
        best_match = matches[best_match_index]
        return ClassificationEvaluation(
            CategoriaTrovata=True,
            imuCodAlq_Codice=best_match["imuCodAlq_Codice"],
            imuCodAlq_Sub=best_match["imuCodAlq_Sub"],
            imuCodAlq_Descrizione=best_match["imuCodAlq_Descrizione"]
        )
    else:
        return ClassificationEvaluation(
            CategoriaTrovata=False,
            imuCodAlq_Codice=0,
            imuCodAlq_Sub=0,
            imuCodAlq_Descrizione=""
        )
