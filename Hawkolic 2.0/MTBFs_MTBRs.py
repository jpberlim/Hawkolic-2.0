import pandas as pd
from HV import HV
import Database

def processar_consumos(df_consumos, IC_list, Aircrafts, HV_files):
    from collections import defaultdict

    to_drop = set()
    df_consumos = df_consumos[df_consumos['CC'] != 'P']

    # Process type 1 vs type 2
    for index, row in df_consumos.iterrows():
        if row['Mov.'] == 1:
            quantity_to_subtract = row['Qtd Mov.']
            prior_movements = df_consumos[
                (df_consumos['NNA'] == row['NNA']) &
                (df_consumos['Mov.'] == 2) &
                (df_consumos.index < index)
            ]
            for type2_index in reversed(prior_movements.index):
                type2_quantity = df_consumos.at[type2_index, 'Qtd Mov.']
                if quantity_to_subtract <= 0:
                    break
                new_quantity = type2_quantity - quantity_to_subtract
                if new_quantity < 0:
                    to_drop.add(type2_index)
                    quantity_to_subtract = -new_quantity
                else:
                    df_consumos.at[type2_index, 'Qtd Mov.'] = new_quantity
                    quantity_to_subtract = 0
            if quantity_to_subtract > 0:
                to_drop.add(index)

    to_drop.update(df_consumos[(df_consumos['Mov.'] == 2) & (df_consumos['Qtd Mov.'] == 0)].index)
    to_drop.update(df_consumos[df_consumos['Mov.'] == 1].index)
    df_consumos = df_consumos.drop(index=to_drop).reset_index(drop=True)
    df_consumos = df_consumos.sort_values(by='Data Mov.').reset_index(drop=True)

    MTB_list = defaultdict(list)
    ic_missing = []
    ids_99 = []
    ic_99 = []

    consumiveis_list = df_consumos[df_consumos['CC'] == 'C']

    for _, row in consumiveis_list.iterrows():
        ic = IC_list['UH-60A'][IC_list['UH-60A']['NNA'] == row['NNA']]['IC'].tolist()
        #ic += IC_list['UH-60L'][IC_list['UH-60L']['NNA'] == row['NNA']]['IC'].tolist()
        ids = Database.search_IC(Aircrafts=Aircrafts, IC=ic)

        if not ids:
            ic_missing.append(row['NNA'])
        elif (ids[0][1].startswith('99-01') or ids[0][1].startswith('99-02')) and \
             len(Aircrafts[29801]['Model'][ids[0][1]]) == 1:
            if ids[0][1] not in ic_99:
                ids_99.extend(IC_list['UH-60A'][IC_list['UH-60A']['IC'] == ids[0][1]]['NNA'])
                ic_99.append(ids[0][1])
            ids = []

        ids = Database.ordenar_lista(ids)
        iter = min(row['Qtd Mov.'], len(ids))

        for i in range(iter):
            MTBF = HV(HV_files=HV_files, end_date=row['Data Mov.'], start_date=ids[i][2]['start_date'])
            MTB_list['IC'].append(ids[i][1])
            MTB_list['NNA'].append(row['NNA'])
            MTB_list['MTB'].append('MTBF')
            MTB_list['Horas'].append(MTBF)
            MTB_list['Data'].append(row['Data Mov.'].strftime('%Y-%m-%d'))
            ids[i][2]['start_date'] = row['Data Mov.'].strftime('%Y-%m-%d')

    # Handle 99 ICs
    for i_99 in ids_99:
        filter_99 = consumiveis_list[consumiveis_list['NNA'] == i_99]
        sum_99 = filter_99['Qtd Mov.'].sum()
        begin_date = '2023-11-01'
        last_date = filter_99['Data Mov.'].max()
        ii_99 = IC_list['UH-60A'][IC_list['UH-60A']['NNA'] == i_99]['IC'].values[0]
        MTBF = HV(HV_files=HV_files, end_date=last_date, start_date=begin_date)

        for _ in range(sum_99):
            MTB_list['IC'].append(ii_99)
            MTB_list['NNA'].append(i_99)
            MTB_list['MTB'].append('MTBF')
            MTB_list['Horas'].append(float(MTBF / sum_99))
            MTB_list['Data'].append(last_date.strftime('%Y-%m-%d'))

    # MTBR
    reparaveis_list = df_consumos[df_consumos['Mov.'] == 5]
    for _, row in reparaveis_list.iterrows():
        ic = IC_list['UH-60A'][IC_list['UH-60A']['NNA'] == row['NNA']]['IC'].tolist()
        ic += IC_list['UH-60L'][IC_list['UH-60L']['NNA'] == row['NNA']]['IC'].tolist()
        ids = Database.search_IC(Aircrafts=Aircrafts, IC=ic)

        if not ids:
            ic_missing.append(row['NNA'])
        ids = Database.ordenar_lista(ids)
        iter = min(row['Qtd Mov.'], len(ids))

        for i in range(iter):
            MTBF = HV(HV_files=HV_files, end_date=row['Data Mov.'], start_date=ids[i][2]['start_date'])
            MTB_list['IC'].append(ids[i][1])
            MTB_list['NNA'].append(row['NNA'])
            MTB_list['MTB'].append('MTBR')
            MTB_list['Horas'].append(MTBF)
            MTB_list['Data'].append(row['Data Mov.'].strftime('%Y-%m-%d'))
            ids[i][2]['start_date'] = row['Data Mov.'].strftime('%Y-%m-%d')

    df_MTB = pd.DataFrame(data=MTB_list)

    ic_stats = df_MTB.groupby('IC').agg(
        Média=('Horas', lambda x: x[x > 0].mean()),
        Desvio_Padrão=('Horas', 'std'),
        Consumos=('Horas', 'size')
    ).reset_index()

    nna_stats = df_MTB.groupby('NNA').agg(
        Média=('Horas', lambda x: x[x > 0].mean()),
        Desvio_Padrão=('Horas', 'std'),
        Consumos=('Horas', 'size')
    ).reset_index()

    df_missing_IC = pd.DataFrame(data=list(set(ic_missing)), columns=['NNA'])

    return df_MTB, ic_stats, nna_stats, df_missing_IC
