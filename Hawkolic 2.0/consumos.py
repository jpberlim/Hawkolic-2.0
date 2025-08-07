import pandas as pd

def read(consumos_file : str):
    df = pd.read_excel(consumos_file, header=0)

    df['Data Mov.'] = pd.to_datetime(df['Data Mov.'].astype(str) + df['Hora Mov.'].astype(str), format='%Y%m%d%H%M%S')
    df['Data Act.'] = pd.to_datetime(df['Data Act.'].astype(str) + df['Hora Mov.'].astype(str), format='%Y%m%d%H%M%S')
    
    df = df.sort_values(by='Data Mov.', ascending=True)
    
    return df