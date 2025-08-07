import math
import pandas as pd


def validar_pecas(pecas):

    pecas_validas = pecas
    
    # Vai peça a peça verificar se tem valor do MTBF, se não tiver passa o IC Superior dessa peça para os "filhos"
    for p in pecas_validas:

        if math.isnan(p["Média"]):
                
                parent= p.get("IC Superior")
                ic_atual= p["IC"]

                for children in pecas_validas:
                     
                     if children.get("IC Superior") == ic_atual:
                          children["IC Superior"] = parent

    # Remove todas as peças que não têm MTBF                
    pecas_validas_final = [p for p in pecas_validas if not pd.isna(p["Média"])] 

    # Passa o desvio padrão das que não têm de NaN para 0
    for p in pecas_validas_final:
         if pd.isna(p["Desvio_Padrão"]):
              p["Desvio_Padrão"] = 0
  
    return pecas_validas_final
