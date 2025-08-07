import numpy as np
from simulacao import simular_rapido

def Teste_horas_restantes(pecas, regime_voo):
# --- Vetor de stock fixo para testar ---
    vetor_stock = [5 for _ in pecas]  # Exemplo: 200 unidades para cada peça
    n_iter = 10000  # Número de simulações para acompanhar a média

    # Armazenar resultados
    horas = []
    medias_iteracao = []

    # Loop para ir guardando a média cumulativa
    for i in range(1, n_iter + 1):
        resultado_temp = simular_rapido(pecas, 
                                        [{"IC": p["IC"], "QTD": int(max(0, q))} for p, q in zip(pecas, vetor_stock)],
                                        regime_voo)
        horas.append(resultado_temp)
        
        # Calcula a média acumulada até agora
        media_atual = np.mean(horas)
        medias_iteracao.append(media_atual)
        
        # Debug: mostra de 50 em 50 iterações
        if i % 50 == 0:
            print(f"Iteração {i} -> Média horas restantes = {media_atual:.2f}")

    # --- Resultado final ---
    print("\nMédia final após", n_iter, "iterações:", np.mean(horas))

    # Se quiseres ver a evolução da média ao longo do tempo:
    import matplotlib.pyplot as plt
    plt.plot(range(1, n_iter + 1), medias_iteracao)
    plt.xlabel("Iterações")
    plt.ylabel("Média acumulada de horas restantes")
    plt.title("Evolução da média com simulações repetidas")
    plt.grid(True)
    plt.show()