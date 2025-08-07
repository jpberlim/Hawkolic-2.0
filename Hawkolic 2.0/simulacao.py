import numpy as np
from gerar_falhas import gerar_falhas_lognormal

def simular_operacao(pecas, inventario_list, regime_voo):
    """
    Simula a operação até faltar stock para reparar uma falha.
    """

    # Gerar falhas para cada peça
    for p in pecas:
        p["falhas"] = gerar_falhas_lognormal(p["Média"], p["Desvio_Padrão"], regime_voo)
     
    # 🔹 Conversão da lista para dicionário
    inventario = {item["IC"]: item["QTD"] for item in inventario_list}

    tempo_passado = 0
    ultimo_tempo_falha = 0  
    consumo = {ic['IC']: 0 for ic in pecas}
    custo_total = 0

    # Ordenar eventos de falha
    eventos = []
    for p in pecas:
        t = 0
        for f in p["falhas"]:
            t += f
            eventos.append((t, p["IC"]))
    eventos.sort(key=lambda x: x[0])

    # Simulação
    for tempo_falha, ic in eventos:
        ultimo_tempo_falha = tempo_falha  # Guardar a última falha processada

        if tempo_falha > regime_voo:
            break

        ic_atual = ic
        substituido = False

        while ic_atual:
            if inventario.get(ic_atual, 0) > 0:
                inventario[ic_atual] -= 1
                consumo[ic_atual] += 1
                custo_total += next(p["Preço"] for p in pecas if p["IC"] == ic_atual)
                substituido = True
                """
                # Se foi peça superior, apenas regista que repôs inferiores (não consome mais stock)--- Não podemos mudar a lista dentro do for, seria interessante "reiniciar o consumo da peça filho" sem tirar do inventario
                if ic_atual != ic:
                    for filho in [p for p in pecas if p["IC_Superior"] == ic_atual]:
                        consumo[filho["IC"]] += 0
                """
                break
                
            else:
                # Subir nível hierárquico
                parent = next((p["IC Superior"] for p in pecas if p["IC"] == ic_atual), None)
                ic_atual = parent

        if not substituido:
            # Falha total -> sem stock
            tempo_passado = tempo_falha
            break
    else:
        # Se completou sem falha total
        tempo_passado = regime_voo

    # Garantir que o tempo atingido é no mínimo o último evento ou o regime final
    tempo_passado = max(tempo_passado, ultimo_tempo_falha)

    return {
        "tempo_atingido": tempo_passado,
        "tempo_restante": max(0, regime_voo - tempo_passado),
        "consumo": consumo,
        "custo_total": custo_total
    }




def simular_rapido(pecas, inventario_list, regime_voo):
    """
    Simula a operação sem calcular consumos e custos.
    """

    # Gerar falhas para cada peça
    for p in pecas:
        p["falhas"] = gerar_falhas_lognormal(p["Média"], p["Desvio_Padrão"], regime_voo)

    # 🔹 Conversão da lista para dicionário
    inventario = {item["IC"]: item["QTD"] for item in inventario_list}

    tempo_passado = 0
    ultimo_tempo_falha = 0  # (ALTERADO) para guardar o tempo da última falha processada

    # Ordenar eventos de falha
    eventos = []
    for p in pecas:
        t = 0
        for f in p["falhas"]:
            t += f
            eventos.append((t, p["IC"]))
    eventos.sort(key=lambda x: x[0])

    # Simulação
    for tempo_falha, ic in eventos:
        ultimo_tempo_falha = tempo_falha  # Guardar a última falha processada

        if tempo_falha > regime_voo:
            break

        ic_atual = ic
        substituido = False

        while ic_atual:
            if inventario.get(ic_atual, 0) > 0:
                inventario[ic_atual] -= 1
                substituido = True
                break
                
            else:
                # Subir nível hierárquico
                parent = next((p["IC Superior"] for p in pecas if p["IC"] == ic_atual), None)
                ic_atual = parent

        if not substituido:
            # Falha total -> sem stock
            tempo_passado = tempo_falha
            break
    else:
        # Se completou sem falha total
        tempo_passado = regime_voo

    # (ALTERADO) Caso não tenha faltado stock e a última falha ocorreu antes do fim da missão
    # Garantir que o tempo atingido é no mínimo o último evento ou o regime final
    tempo_passado = max(tempo_passado, ultimo_tempo_falha)

    return  max(0, regime_voo - tempo_passado),
    


def simula_preço(inventario_otimo, pecas):
    """
    Calcula o custo total do inventário ótimo.
    Retorna custo total do inventário
    """
    custo_total = 0

    for item in inventario_otimo:
        ic = item["IC"]
        qtd = item["QTD"]

        # encontrar preço da peça
        preco = next((p["Preço"] for p in pecas if p["IC"] == ic), 0)

        custo_total += qtd * preco

    return custo_total
