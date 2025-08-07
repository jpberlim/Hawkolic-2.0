import numpy as np
from simulacao import simular_rapido

def funcao_objetivo(vetor_stock, pecas, regime_voo, penalizacao):
    """
    Função de custo para o otimizador.
    Devolve o custo do stock gerado pelo otimizador com o custo da penalização por não cumprir as horas de voo
    """
    # Cria inventario positivo e inteiro
    inventario = [{"IC": p["IC"], "QTD": round(q)} for p, q in zip(pecas, vetor_stock)]

    # Calcula o preço do inventario
    custo_inventario = sum(q * p["Preço"] for p, q in zip(pecas, vetor_stock))
    resultado_temp=[]
    horas=[]

    # Corre Simulações para ver se o stock chega e calcula as horas restantes quando acaba o stock
    for i in range(2):
        resultado_temp = simular_rapido(pecas, inventario, regime_voo)
        horas.append(resultado_temp)    

    # Aqui Podiamos usar o np.percentile para dar o 95% das horas de voo...
    horas_restantes = np.mean(horas)
    
    return custo_inventario + penalizacao * horas_restantes



def fitness_func(solution, pecas, regime_voo, penalizacao):
    # solution é um vetor com quantidades de stock
    inventario = [{"IC": p["IC"], "QTD": int(max(0, q))} for p, q in zip(pecas, solution)]
    
    custo_inventario = sum(q * p["Preço"] for p, q in zip(pecas, solution))
    horas = []

    for _ in range(10):  # simulações rápidas
        resultado = simular_rapido(pecas, inventario, regime_voo)
        horas.append(resultado)

    horas_restantes = np.mean(horas)
    custo_total = custo_inventario + penalizacao * horas_restantes

    # GA maximiza → retornamos valor negativo para minimizar custo
    return -custo_total