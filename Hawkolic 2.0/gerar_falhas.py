import numpy as np
import pandas as pd



def gerar_falhas_lognormal(mtbf, variabilidade, regime):
    """
    Gera uma lista de tempos entre falhas até atingir o regime de voo.
    Usa distribuição lognormal com média ~MTBF.
    """
    falhas = []
    total = 0

    sigma = np.sqrt(np.log(1 + (variabilidade / mtbf)**2))
    mu = np.log(mtbf) - (sigma**2) / 2

    while total < regime:
        tempo = np.random.lognormal(mean=mu, sigma=sigma)
        falhas.append(tempo)
        total += tempo

    return falhas
