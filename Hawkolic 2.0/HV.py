import pandas as pd
import re
from datetime import datetime

mes = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']

def HV(HV_files : list, end_date, start_date):

    HV_df = []
    for path in HV_files:
        HV_df.append(pd.read_excel(path, header=0))

    if (type(start_date) == str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if (type(end_date) == str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    # Generate a date range with a frequency of 'MS' (Month Start)
    months = pd.date_range(start=start_date, end=end_date, freq='MS')
    months = months[:-1]
    if(months.empty):
        return 0
    if(start_date != months[0]):
        months = [pd.to_datetime(start_date)] + months.tolist() + [pd.to_datetime(end_date)]

    # Loop through the generated months
    
    sum_HV = 0
    for i, date in enumerate(months):
        if i == 0:  # First month
            n_aircrafts = HV_df[date.year - 2023][mes[10]].values.size - 1
            total_HV = int(re.match(r'(\d+)H(\d+)m', HV_df[date.year - 2023][mes[date.month - 1]].values[-1]).group(1)) * 60 + int(re.match(r'(\d+)H(\d+)m', HV_df[date.year - 2023][mes[date.month - 1]].values[-1]).group(2))
            HV_aircraft = total_HV / n_aircrafts

            # Get the number of days left in the first month
            days_in_month = (date + pd.offsets.MonthEnd(0)).day
            days_remaining = days_in_month - start_date.day + 1  # Include the start date

            # Calculate interpolated flight hours for the remaining days
            daily_HV = HV_aircraft / days_in_month
            interpolated_HV = daily_HV * days_remaining

            sum_HV += interpolated_HV

        elif date != months[-1]:  # Middle months
            n_aircrafts = HV_df[date.year - 2023][mes[10]].values.size - 1
            total_HV = int(re.match(r'(\d+)H(\d+)m', HV_df[date.year - 2023][mes[date.month - 1]].values[-1]).group(1)) * 60 + int(re.match(r'(\d+)H(\d+)m', HV_df[date.year - 2023][mes[date.month - 1]].values[-1]).group(2))
            HV_aircraft = total_HV / n_aircrafts

            sum_HV += HV_aircraft


        else:  # Last month
            n_aircrafts = HV_df[date.year - 2023][mes[10]].values.size - 1
            total_HV = int(re.match(r'(\d+)H(\d+)m', HV_df[date.year - 2023][mes[date.month - 1]].values[-1]).group(1)) * 60 + int(re.match(r'(\d+)H(\d+)m', HV_df[date.year - 2023][mes[date.month - 1]].values[-1]).group(2))
            HV_aircraft = total_HV / n_aircrafts

            # Get the number of days in the last month
            days_in_month = (date + pd.offsets.MonthEnd(0)).day
            days_difference = (end_date - pd.Timestamp(year=date.year, month=date.month, day=1)).days + 1  # Include the last day

            # Calculate interpolated flight hours for the remaining days
            daily_HV = HV_aircraft / days_in_month

            # Interpolate total flight hours for the remaining days
            interpolated_HV = daily_HV * days_difference

            sum_HV += interpolated_HV
    
    return sum_HV / 60
        
        

#HV(HV_files=['C:\\Users\\JPBranco\\Documents\\Hawkolic 2.0\\Inputs\\ResumoMensalHV_2023_exemplo.xlsx','C:\\Users\\JPBranco\\Documents\\Hawkolic 2.0\\Inputs\\ResumoMensalHV_2024_exemplo.xlsx'], end_date='2024-04-15', start_date='2023-11-05')


        

    