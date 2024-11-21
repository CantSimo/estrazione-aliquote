from AiServices.models import ClassificationEvaluation
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from AiServices.models import MatchFounded
from config import settings

async def evaluate_classification_result(descrizione_aliquota, matches):
    """
    Valuta quale dei matches trovati corrisponde semanticamente meglio alla descrizione dell'aliquota.
    
    Args:
        descrizione_aliquota (str): La descrizione dell'aliquota in delibera.
        matches (list): Lista di possibili corrispondenze trovate in Pinecone.
        
    Returns:
        ClassificationEvaluation: Risultato della valutazione.
    """
    
    # Definisci il contenuto del role system per guidare meglio il comportamento del modello
    systemcontent = (
        "Sei un assistente esperto nella classificazione di aliquote fiscali. "
        "Il tuo compito è identificare quale delle descrizioni fornite più si avvicina semanticamente alla descrizione fornita dall'aliquota. "
        "Se nessuna corrisponde adeguatamente, restituisci il valore 0. "
        "Considera accuratamente la descrizione delle categorie catastali."
    )

    # Costruisci il prompt per l'LLM
    promptUser = (
        f"La descrizione dell'aliquota è: '{descrizione_aliquota}'.\n"
        f"Valuta quale tra le seguenti descrizioni corrisponde meglio: \n"
    )
    for i, match in enumerate(matches):
        promptUser += f"{i + 1}. {match['imuCodAlq_Descrizione']}\n"

    promptUser += "Restituisci il numero della descrizione che corrisponde meglio, oppure 0 se nessuna è appropriata."
    
    # Chiamata al modello di linguaggio per la valutazione
    best_match_index = await call_llm(promptUser, systemcontent)
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
    
async def call_llm(promptUser, system_content):
    """
    Esegue una chiamata a un modello di linguaggio per elaborare una richiesta.
    
    Args:
        promptUser (str): La richiesta utente da passare al modello di linguaggio.
        system_content (str): Il contesto del ruolo del sistema per il modello.
        
    Returns:
        str: La risposta del modello di linguaggio.
    """
    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL, 
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2, 
        model_kwargs={"store": True})
    llm = llm.with_structured_output(MatchFounded)

    try:
        #---- Chaining ------
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_content),
                ("human", "{input}"),
            ]
        )

        chain = prompt | llm
        output = chain.invoke(
                    {
                        "input": promptUser,
                    }
                )
        
        return output.NumeroRiga

    except Exception as e:
        print(e)
        return e    