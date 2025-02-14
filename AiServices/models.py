from pydantic import BaseModel, Field
from typing import List

class Aliquota(BaseModel):
    valore: float = Field(
        ..., 
        description="Il valore dell'aliquota espresso in percentuale",
        example=1.06
    )
    fattispeciePrincipale: str = Field(
        ..., 
        description="Una descrizione che specifica a quale fattispecie principale appartiene l'aliquota, obbligatoria"
    )
    fattispeciePersonalizzata: str = Field(
        ..., 
        description="Una descrizione che specifica a quale fattispecie secodaria appartiene l'aliquota, facoltativa"
    )
    esente: bool = Field(
        ..., 
        description="impostare a true se nella colonna valore e' indicata la descrizione 'esente' al posto del valore percentuale, altrimenti impostare a false.",
    )
    assimilazioneAbitazionePrincipale: str = Field(
        ..., 
        description="puo' valere 'SI', 'NO' o ''",
        example="SI"
        )
    def Filtra(self):
        if self.fattispeciePrincipale == "Abitazione principale di categoria catastale A/1, A/8 e A/9 e relative pertinenze":
            return 1
        elif self.fattispeciePrincipale == "Assimilazione all’abitazione principale dell’unità immobiliare posseduta da anziani o disabili di cui all'art. 1, comma 741, lett. c), n. 6), della legge n. 160 del 2019":
            return 2
        elif self.fattispeciePrincipale == "Fabbricati rurali ad uso strumentale (inclusa la categoria catastale D/10)":
            return 3
        elif self.fattispeciePrincipale == "Fabbricati appartenenti al gruppo catastale D (esclusa la categoria catastale D/10)":
            return 4
        elif self.fattispeciePrincipale == "Terreni agricoli":
            return 5
        elif self.fattispeciePrincipale == "Aree fabbricabili":
            return 6
        elif self.fattispeciePrincipale == "Altri fabbricati (fabbricati diversi dall'abitazione principale e dai fabbricati appartenenti al gruppo catastale D)":
            return 7

class NewAliquota(BaseModel):
    Codice: int = Field(
        ..., 
        description="Codice Aliquota",
        example=1
    )        
    SubCodice: str = Field(
        ..., 
        description="Subcodice, progressivo all'interno del Codice",
        example='0098'
    )        

    FattispeciePersonalizzata: str = Field(
        ..., 
        description="Una descrizione che specifica a quale fattispecie principale appartiene l'aliquota, obbligatoria"
    )

class Delibera(BaseModel):
    Comune: str = Field(
        ..., 
        description="Il nome del comune che ha emesso la delibera fiscale."
    )
    Data: str = Field(
        ..., 
        description="La data in cui è stata emessa la delibera, nel formato giorno-mese-anno."
    )
    Aliquote: List[Aliquota] = Field(
        ..., 
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

