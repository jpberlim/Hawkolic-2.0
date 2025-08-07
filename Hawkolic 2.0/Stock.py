import pandas as pd


def buy(abastecimento_file, estatisticas_file, configuracao_file, Regime_de_esforço):

    # Define your own column names
    custom_headers = ['NNA', 'Nome', 'Tipo', 'UF', 'Qtd Disponivel', 'Qtd Cativa', 'Qtd Reparavel', 'Cod. Apl']

    # Read from row 2 (which is index 1), and ignore existing headers
    df = pd.read_excel(abastecimento_file, header=1, names=custom_headers)

    # Read all sheets into a dictionary of DataFrames
    df_stats = pd.read_excel(estatisticas_file, sheet_name=None)

    df_config =pd.read_excel(configuracao_file, sheet_name=None)

    ICs = df_stats['ICs']['IC'].to_list()
    list_to_buy = []

    #Método de cálculo de compra por base no regime de esforço e MTBF
    #Método linear
    #Não toma em consideração a árvore de configuração
    #Nivel de Identure = 0
    for ic in ICs:

        ic_nnas = df_config['UH-60A'][df_config['UH-60A']['IC'] == ic]['NNA'].to_list()
        ic_stock = df[df['NNA'].isin(ic_nnas)]['Qtd Disponivel'].sum()

        ic_buy = Regime_de_esforço / df_stats['ICs'][df_stats['ICs']['IC'] == ic]['Média'] - ic_stock

        list_to_buy.append([ic, float(ic_buy)])
        
    return list_to_buy



    





    


