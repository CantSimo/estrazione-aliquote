from config import settings
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(
    model=settings.OPENAI_MODEL, 
    temperature=0.1,
    max_tokens=None,
    timeout=None,
    max_retries=2, 
    model_kwargs={"store": False})
    
async def openai_invoke(user_content, system_content, structured_output):
    """
    Esegue una chiamata a un modello di linguaggio per elaborare una richiesta.
    
    Args:
        humanMessage (str): La richiesta utente da passare al modello di linguaggio.
        system_content (str): Il contesto del ruolo del sistema per il modello.
        structured_output (type): Tipo di output strutturato per il modello.
        
    Returns:
        str: La risposta del modello di linguaggio.
    """
    llm_with_output = llm.with_structured_output(structured_output)

    #---- Chaining ------
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_content),
            ("human", "{input}"),
        ]
    )

    chain = prompt | llm_with_output
    output = chain.invoke(
                {
                    "input": user_content,
                }
            )
    
    return output