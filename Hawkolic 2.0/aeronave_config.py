import pandas as pd

def configurar_aeronaves(Aircrafts, df_config):
    # Create IC list
    IC_list = {
        'UH-60A': df_config['UH-60A'].drop_duplicates(subset=['IC']),
        'UH-60L': df_config['UH-60L'].drop_duplicates(subset=['IC'])
    }

    # Assign models to each aircraft
    for N, aircraft in Aircrafts.items():
        aircraft['Model'] = {}
        for _, row in IC_list[aircraft['Config']].iterrows():
            aircraft['Model'][row['IC']] = {}
            for ID in range(1, row['QTD'] + 1):
                aircraft['Model'][row['IC']][ID] = {
                    'start_date': aircraft['start_date']
                }

    # Return full IC list (not drop_duplicates)
    IC_list = {
        'UH-60A': df_config['UH-60A'],
        'UH-60L': df_config['UH-60L']
    }

    return Aircrafts, IC_list



#df_config = pd.read_excel('C:\\Users\\JPBranco\\Documents\\Hawkolic 2.0\\Inputs\\Configuração.xlsx', header=0, sheet_name=None)

"""
Aircrafts = {
    29801: {'Config': 'UH-60A', 'start_date': '2023-11-01'},
    29802: {'Config': 'UH-60A', 'start_date': '2023-11-01'},
    29803: {'Config': 'UH-60A', 'start_date': '2024-12-19'},
    29804: {'Config': 'UH-60A', 'start_date': '2025-04-28'}
}
configurar_aeronaves(Aircrafts, df_config)
"""