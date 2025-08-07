import pandas as pd
import os



def Files_in():
     
    Preco_heli = 4855000

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    #MTBF_file= os.path.join(BASE_DIR, 'Outputs', 'Output_Estatisticas.xlsx')
    #configuracao_file = os.path.join(BASE_DIR, 'Inputs', 'Configuração.xlsx')

    
    #INPUTS PARA FICHEIROS DE TESTE

    #MTBF_file = os.path.join(BASE_DIR, 'Intputs', 'Book2.xlsx')
    MTBF_file= r"C:\Users\Joca\OneDrive - Academia da Força Aérea\Desktop\Hawkolic 2.0\Hawkolic 2.0\Inputs\Book2.xlsx"
    #configuracao_file= os.path.join(BASE_DIR, 'Inputs', 'Test_file.xlsx')
    configuracao_file= r"C:\Users\Joca\OneDrive - Academia da Força Aérea\Desktop\Hawkolic 2.0\Hawkolic 2.0\Inputs\Teste_file.xlsx"


    #df_medias = pd.read_excel(MTBF_file, sheet_name="ICs", header=0, index_col="IC")
    df_medias = pd.read_excel(MTBF_file, header=0, index_col="IC")

    #df_config = pd.read_excel(configuracao_file, sheet_name="UH-60A", header=0, dtype={"IC": str, "IC Superior": str})
    df_config = pd.read_excel(configuracao_file, header=0, dtype={"IC": str, "IC Superior": str})

    df_config_temp = df_config.drop_duplicates(subset=['IC'])

    # Junta o IC Superior à data frame das médias
    added = pd.concat([df_medias, df_config_temp.set_index('IC')[["IC Superior"]]], axis=1)
    added.index.name = "IC"

    # Vai buscar só o preço mais baixo de um IC ao excel 
    df_min_preco = df_config.groupby("IC")["Preço"].min().to_frame("Preço")

    # Junta o preço à data frame
    result = pd.concat([added, df_min_preco[["Preço"]]], axis=1)
    result["Preço"] = result["Preço"].fillna(Preco_heli)

    # Garante que o IC e IC Superior são strings
    result= result.reset_index()
    result["IC"]= result["IC"].astype(str)
    result["IC Superior"]= result["IC Superior"].astype(str)

    # Passa para dicionario
    dict_result = result.to_dict(orient='records')
    return dict_result

