import pandas as pd
import os
import time
import pygad

import consumos
from aeronave_config import configurar_aeronaves
from MTBFs_MTBRs import processar_consumos
from Stock import buy

from functools import partial
from scipy.optimize import differential_evolution
from gerar_falhas    import gerar_falhas_lognormal
from simulacao       import simular_operacao
from simulacao       import simula_preço
from Funcao_de_custo import funcao_objetivo
from Funcao_de_custo import fitness_func
from Validar_inv   import validar_pecas
from Import_files import Files_in
from teste_HR import Teste_horas_restantes


# Start time counter
tic= time.perf_counter()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#os.makedirs(folder_path, exist_ok=True)  # (Optional) recreate folder

# Aircrafts dictionary stays here
Aircrafts = {
    29801: {'Config': 'UH-60A', 'start_date': '2023-11-01'},
    29802: {'Config': 'UH-60A', 'start_date': '2023-11-01'},
    29803: {'Config': 'UH-60A', 'start_date': '2024-12-19'},
    29804: {'Config': 'UH-60A', 'start_date': '2025-04-28'}
}


Regime_de_esforço = 250


# Paths Note: no futuro tem que se vir ca adicionar caminhos para novos registos de HV
configuracao_file = os.path.join(BASE_DIR, 'Inputs', 'Configuração.xlsx')
consumos_file = os.path.join(BASE_DIR, 'Inputs', 'Consumos.xlsx')
HV_files = [
     os.path.join(BASE_DIR, 'Inputs', 'ResumoMensalHV_2023_exemplo.xlsx'),
     os.path.join(BASE_DIR, 'Inputs', 'ResumoMensalHV_2024_exemplo.xlsx'),
     os.path.join(BASE_DIR, 'Inputs', 'ResumoMensalHV_2025_exemplo.xlsx')
]

abastecimento_file = os.path.join(BASE_DIR, 'Inputs','abastecimento.xls')

# Read files
df_consumos = consumos.read(consumos_file=consumos_file)
df_config = pd.read_excel(configuracao_file, header=0, sheet_name=None)

# Format NNA as string
for sheet_name, df in df_config.items():
    if 'NNA' in df.columns:
        df_config[sheet_name]['NNA'] = df['NNA'].astype(int)
        df_config[sheet_name]['NNA'] = df['NNA'].astype(str)

# Configure aircrafts + IC_list
Aircrafts, IC_list = configurar_aeronaves(Aircrafts, df_config)

# Process MTBF/MTBR
##############################
#Falta adicionar o MTBF/MTBR de todos os ICs na data atual da execução
#Ou seja, em teoria existe dados para todos os ICs
##############################
df_MTB, ic_stats, nna_stats, df_missing_IC = processar_consumos(
    df_consumos, IC_list, Aircrafts, HV_files
)

# Export to Excel
estatisticas_file = os.path.join(BASE_DIR, 'Outputs', 'Output_Estatisticas.xlsx')
with pd.ExcelWriter(estatisticas_file) as writer:
    df_MTB.to_excel(writer, sheet_name='Consumos', index=False)
    ic_stats.to_excel(writer, sheet_name='ICs', index=False)
    nna_stats.to_excel(writer, sheet_name='NNA', index=False)
    df_missing_IC.to_excel(writer, sheet_name='ICs em falta', index=False)

list_to_buy = buy(abastecimento_file, estatisticas_file, configuracao_file, Regime_de_esforço)

pd_list_to_buy = pd.DataFrame(list_to_buy, columns=['IC', 'QTD'])

with pd.ExcelWriter(estatisticas_file, mode='a', engine='openpyxl', if_sheet_exists='new') as writer:
    pd_list_to_buy.to_excel(writer, sheet_name='Comprar', index=False)

print("Exportou Outputs")
"""
PARTE DO OTIMIZADOR ########################################################################################################################

"""

# Importa as pecas dos ficheiros
pecas= Files_in()

# Validar apenas peças com dados 
pecas_validas= validar_pecas(pecas)

Teste_horas_restantes(pecas_validas, Regime_de_esforço)

# GENETIC ALGORITHM ############################################################################
print("Entrou GA")
# Limites do stock
gene_space = [{'low': 0, 'high': 5000, 'step': 1} for _ in pecas_validas]

# Parametros
ga_instance = pygad.GA(
    fitness_func=fitness_func,
    num_genes=len(pecas_validas),
    num_generations=100,    # nº de gerações
    sol_per_pop=20,         # tamanho da população
    num_parents_mating=10,    # nº de indivíduos selecionados para cruzamento (regra geral: POP/2)
    gene_space=gene_space,
    mutation_probability=0.1,
    random_seed=42
)

ga_instance.run()

ga_instance.plot_fitness()


# fitness: valor que determina o quão boa é a solução // Solution: vetor que teve o melhor resultado // index: indice da solução na população 
Solution, fitness, index = ga_instance.best_solution()

# Passa do vetor para lista 
inventario_GA = [{"IC": p["IC"], "QTD": round(q)} 
                    for p, q in zip(pecas_validas, Solution)]

# Passa o resultado para data frame
df_stock_GA = pd.DataFrame(inventario_GA)

# Calcula o preço do inventario otimo
custo_GA= simula_preço(inventario_GA,pecas)

# Cria falhas para testar o Stock Otimo
for p in pecas_validas:
    p["falhas"] = gerar_falhas_lognormal(p["Média"], p["Desvio_Padrão"], Regime_de_esforço)

# Simula Operação para o Regime de esforço 
resultado_GA = simular_operacao(pecas_validas, inventario_GA, Regime_de_esforço)

print("SAIU GA")
# Differential evolution #######################################################################

# Definir limites para cada peça (min_stock, max_stock)
limites = [(0, 5000) for _ in pecas_validas]

# Usar partial para fixar parâmetros da função
objetivo = partial(funcao_objetivo, pecas=pecas_validas, regime_voo=Regime_de_esforço, penalizacao=10000000)

print("ENTROU DE")
# Rodar o otimizador
resultado_opt = differential_evolution(objetivo, bounds=limites, strategy='best1bin', maxiter=10, popsize=10)

# Passa do vetor para lista 
inventario_DE = [{"IC": p["IC"], "QTD": round(q)} 
                    for p, q in zip(pecas_validas, resultado_opt.x)]

# Passa o resultado para data frame
df_stock_DE = pd.DataFrame(inventario_DE)

# Calcula o preço do inventario otimo
custo_DE= simula_preço(inventario_DE,pecas)


# Cria falhas para testar o Stock Otimo
for p in pecas_validas:
    p["falhas"] = gerar_falhas_lognormal(p["Média"], p["Desvio_Padrão"], Regime_de_esforço)

# Simula Operação para o Regime de esforço 
resultado_DE = simular_operacao(pecas_validas, inventario_DE, Regime_de_esforço)

print("SAIU DE")
"""
# FIM DO PROGRAMA ############################################################################################################################
"""
# fim do tempo do programa
toc= time.perf_counter()
print(f"time spent:{toc-tic} seconds")
print(f"in minutes: {(toc-tic)/60}")

# Criar DataFrame para resumo
df_resultados_DE = pd.DataFrame([{
    "Tempo atingido (h)": resultado_DE["tempo_atingido"],
    "Tempo restante (h)": resultado_DE["tempo_restante"],
    "Custo total peças usadas": resultado_DE["custo_total"],
    "Custo inventário ótimo": custo_DE,
    "Tempo total simulação (s)": toc - tic,
    "Tempo total simulação (min)": (toc - tic) / 60
}])

df_resultados_GA = pd.DataFrame([{
    "Tempo atingido (h)": resultado_GA["tempo_atingido"],
    "Tempo restante (h)": resultado_GA["tempo_restante"],
    "Custo total peças usadas": resultado_GA["custo_total"],
    "Custo inventário ótimo": custo_GA,
    "Tempo total simulação (s)": toc - tic,
    "Tempo total simulação (min)": (toc - tic) / 60
}])

# DataFrame para consumo total
df_consumo_DE = pd.DataFrame(
    list(resultado_DE["consumo"].items()), 
    columns=["IC", "Consumo"]
)

df_consumo_GA = pd.DataFrame(
    list(resultado_GA["consumo"].items()), 
    columns=["IC", "Consumo"]
)

# Exportar tudo para Excel em folhas separadas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(BASE_DIR, 'Outputs', 'Resultados_Simulacao.xlsx')

with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    df_resultados_DE.to_excel(writer, sheet_name="Resumo DE", index=False)
    df_resultados_DE.to_excel(writer, sheet_name="Resumo DE", index=False)
    df_stock_DE.to_excel(writer, sheet_name="Stock_Ótimo DE", index=False)
    df_consumo_DE.to_excel(writer, sheet_name="Consumo_Total DE", index=False)
    df_resultados_GA.to_excel(writer, sheet_name="Resumo GA", index=False)
    df_resultados_GA.to_excel(writer, sheet_name="Resumo GA", index=False)
    df_stock_GA.to_excel(writer, sheet_name="Stock_Ótimo GA", index=False)
    df_consumo_GA.to_excel(writer, sheet_name="Consumo_Total GA", index=False)

print(f"\n✅ Resultados exportados para '{output_path}'")

