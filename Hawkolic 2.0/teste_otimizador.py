import time
from functools import partial
from scipy.optimize import differential_evolution
import pandas as pd
import os
from gerar_falhas    import gerar_falhas_lognormal
from simulacao       import simular_operacao
from simulacao       import simula_preço
from Funcao_de_custo import funcao_objetivo
from Validar_inv   import validar_pecas
from Import_files import Files_in
import winsound

import matplotlib.pyplot as plt


from teste_HR import Teste_horas_restantes

tic= time.perf_counter()

regime_voo = 250  # horas de voo para simular

# Dados das peças (IC, IC_Superior, MTBF, variância, preço) - Hardcoded (exemple)
pecas = [
    {"IC": "0-1", "IC Superior": "nan"  , "Média": 50  , "Desvio_Padrão": 1 , "Preço": 10000},
    {"IC": "0-2", "IC Superior": "0-1" , "Média": 15, "Desvio_Padrão": 2, "Preço": 50},
    {"IC": "0-3", "IC Superior": "0-1" , "Média": 10  , "Desvio_Padrão": 1, "Preço": 10},
    {"IC": "0-4", "IC Superior": "0-1" , "Média": 25, "Desvio_Padrão": 1, "Preço": 200},
    {"IC": "0-5", "IC Superior": "0-2" , "Média": 10, "Desvio_Padrão": 1.5, "Preço": 7},
    {"IC": "0-6", "IC Superior": "0-3" , "Média": 7, "Desvio_Padrão": 1,   "Preço": 4},
    {"IC": "0-7", "IC Superior": "0-4" , "Média": 8, "Desvio_Padrão": 0, "Preço": 5},
    {"IC": "0-8", "IC Superior": "0-5" , "Média": 1, "Desvio_Padrão": 0.1, "Preço": 1},

]

# Importa as pecas dos ficheiros
pecas= Files_in()

# Validar apenas peças com dados 
pecas_validas= validar_pecas(pecas)

# Definir limites para cada peça (min_stock, max_stock)
limites = [(0, 500) for _ in pecas_validas]

# Usar partial para fixar parâmetros da função
objetivo = partial(funcao_objetivo, pecas=pecas_validas, regime_voo=regime_voo, penalizacao=1000000)

# Solução linear
for p in pecas_validas:
    p["Stock_linear"]= int(regime_voo/p["Média"])


# TESTE HORAS RESTANTES
Teste_horas_restantes(pecas_validas, 250)

# Rodar o otimizador
# INVESTIGAR MUTATION
historico=[]

def callback(xk, convergence):
    historico.append(objetivo(xk))

resultado_opt = differential_evolution(objetivo, bounds=limites, strategy='best1bin', maxiter=2000, popsize=10, callback=callback)

# Plot da evolução da função objetivo
plt.plot(historico)
plt.xlabel("Geração")
plt.ylabel("Valor da função objetivo")
plt.title("Evolução do Differential Evolution")
plt.grid(True)
plt.show()


print("\n=== RESULTADO DA OTIMIZAÇÃO ===")
print("Níveis ótimos de stock:", [int(x) for x in resultado_opt.x])

inventario_otimo = [{"IC": p["IC"], "QTD": int(max(0, q))} 
                    for p, q in zip(pecas_validas, resultado_opt.x)]

custo= simula_preço(inventario_otimo,pecas)
print("\nCusto inverntario otimo = ", custo)

for p in pecas_validas:
    p["falhas"] = gerar_falhas_lognormal(p["Média"], p["Desvio_Padrão"], regime_voo)

resultado_final = simular_operacao(pecas_validas, inventario_otimo, regime_voo)

print("\n=== RESULTADOS COM STOCK ÓTIMO ===")
print("Stock ótimo por peça:", {inv['IC']: inv['QTD'] for inv in inventario_otimo})
print("Tempo atingido:", resultado_final["tempo_atingido"])
print("Tempo restante:", resultado_final["tempo_restante"])
print("Consumo total:", resultado_final["consumo"])
print("Custo total peças usadas:", resultado_final["custo_total"])



toc= time.perf_counter()
print(f"time spent:{toc-tic} seconds")
print(f"in minutes: {(toc-tic)/60}")

winsound.Beep(2500, 500)

# Criar DataFrame para resumo
df_resultados = pd.DataFrame([{
    "Tempo atingido (h)": resultado_final["tempo_atingido"],
    "Tempo restante (h)": resultado_final["tempo_restante"],
    "Custo total peças usadas": resultado_final["custo_total"],
    "Custo inventário ótimo": custo,
    "Tempo total simulação (s)": toc - tic,
    "Tempo total simulação (min)": (toc - tic) / 60
}])

# DataFrame para stock ótimo
df_stock = pd.DataFrame(inventario_otimo)

# DataFrame para consumo total
df_consumo = pd.DataFrame(
    list(resultado_final["consumo"].items()), 
    columns=["IC", "Consumo"]
)

# Exportar tudo para Excel em folhas separadas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(BASE_DIR, "Outputs\\Resultados_Simulacao.xlsx")

with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    df_resultados.to_excel(writer, sheet_name="Resumo", index=False)
    df_stock.to_excel(writer, sheet_name="Stock_Ótimo", index=False)
    df_consumo.to_excel(writer, sheet_name="Consumo_Total", index=False)

print(f"\n✅ Resultados exportados para '{output_path}'")



