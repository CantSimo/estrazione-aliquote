from config import settings
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI
from Utils.files import leggi_file_txt, estrai_testo_pdf
from AiServices.models import Delibera
import langsmith as ls
import os

async def estrazione_aliquote_OpenAi(file):
    """
    Utilizza le API di OpenAI per estrarre aliquote da una delibera comunale in formato PDF.
    
    Args:
        file : Delibera in formato PDF.
        
    Returns:
        dict: un oggetto json la cui struttura è data dalla classe 'Delibera'.
    """
    client = OpenAI()

    delibera_text = await estrai_testo_pdf(file)
    prompt_text = leggi_file_txt(os.path.join(settings.BASE_DIR, "Files", "estrazione_aliquote_prompt.txt"))

    try:
        completion  = client.beta.chat.completions.parse(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": prompt_text},
                {"role": "user", "content": delibera_text}
            ],
            response_format=Delibera,
            temperature=0.1,
            store=True,
        )
        output = completion.choices[0].message

        if output.parsed:
            return output.parsed
        elif output.refusal:
            return output.refusal

    except Exception as e:
        print(e)
        return e

async def estrazione_aliquote_LangChain_ChatOpenAi(file):
    """
    Utilizza le API di Langchain ed OpenAI per estrarre aliquote da una delibera comunale in formato PDF.
    
    Args:
        file : Delibera in formato PDF.
        
    Returns:
        dict: un oggetto json la cui struttura è data dalla classe 'Delibera'.
    """

    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL, 
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2, 
        model_kwargs={"store": True})
    llm = llm.with_structured_output(Delibera)

    delibera_text = await estrai_testo_pdf(file)
    prompt_text = leggi_file_txt(os.path.join(settings.BASE_DIR, "Files", "estrazione_aliquote_prompt_langchain.txt"))

    try:
        #---- Chaining ------
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    prompt_text,
                ),
                ("human", "{input}"),
            ]
        )

        chain = prompt | llm
        output = chain.invoke(
                    {
                        "input": delibera_text,
                    }
                )
        
        return output

    except Exception as e:
        print(e)
        return e    
