from pydantic import BaseModel, Field
from typing import List

class Aliquota(BaseModel):
    valore: float = Field(
        ..., 
        alias="Valore", 
        description="Il valore dell'aliquota espresso in percentuale",
        example=1.06
    )
    descrizione: str = Field(
        ..., 
        alias="Descrizione", 
        description="Una descrizione che specifica a quale tipo di immobile o condizione si applica l'aliquota (ad esempio, 'abitazione principale', 'fabbricati rurali')."
    )

class Delibera(BaseModel):
    comune: str = Field(
        ..., 
        alias="Comune", 
        description="Il nome del comune che ha emesso la delibera fiscale."
    )
    data: str = Field(
        ..., 
        alias="Data", 
        description="La data in cui è stata emessa la delibera, nel formato giorno-mese-anno."
    )
    aliquote: List[Aliquota] = Field(
        ..., 
        alias="Aliquote", 
        description="L'elenco delle aliquote applicabili contenute nella delibera, ciascuna associata a specifici gruppi e categorie catastali."
    )

class ClassificationEvaluation(BaseModel):
    CategoriaTrovata: bool = Field(
        ..., 
        description="vale True se e' stato recuperato un match la cui 'imuCodAlq_Descrizione' corrisponde semanticamente alla descrizione dell'aliquota in delibera, altrimenti False"
    )
        
    imuCodAlq_Codice: int = Field(
        ..., 
    )

    imuCodAlq_Sub: int = Field(
        ..., 
    )

    imuCodAlq_Descrizione: str = Field(
        ..., 
        description="Una descrizione che specifica a quale tipo di immobile o condizione si applica l'aliquota (ad esempio, 'abitazione principale', 'fabbricati rurali')."
    )

class MatchFounded(BaseModel):
    NumeroRiga: int = Field(
        ..., 
        description="Numero della descrizione che corrisponde meglio, oppure 0 se nessuna è appropriata."
    )


