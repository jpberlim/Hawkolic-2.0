from datetime import datetime
from collections import defaultdict

# Aircraft[NºCauda][Config, start_date, Model]
# Aircraft[NºCauda][Model][IC][ID][start_date]

Aircrafts = {
    29801: {
        'Config': 'UH-60A',
        'start_date': '2023-11-01',
        'Model': {
            '09': {
                '1': {
                    'start_date': '2024-10-12'
                },
                '2': {
                    'start_date': '2024-10-12'
                }
            }
        }
    },
    29802: {
        'Config': 'UH-60A',
        'start_date': '2023-11-01',
        'Model': {
            '09': {
                '1': {
                    'start_date': '2024-10-12'
                },
                '2': {
                    'start_date': '2024-10-11'
                }
            }
        }
    }
}

def search_IC(Aircrafts : dict, IC : list):
    """
    Function to search and collect the aircrafts based on IC value.
    """
    list_ids = []
    for n_cauda, aircraft in Aircrafts.items():
        for ic, ids in aircraft['Model'].items():
            if ic in IC:
                for id_key, id_value in ids.items():
                    # Append the tuple (n_cauda, IC, id_dict)
                    list_ids.append((n_cauda, ic, id_value))  # id_value contains 'start_date'
    return list_ids

def ordenar_lista(list_ids):
    """
    This function sorts the list_ids by start_date and intercalates the IDs
    by aircraft number (n_cauda) for entries with the same start_date.
    """
    
    # Step 1: Sort the list by start_date using x[2]['start_date']
    list_ids_sorted = sorted(list_ids, key=lambda x: datetime.strptime(x[2]['start_date'], "%Y-%m-%d"))
    
    # Step 2: Group by start_date and intercalate by aircraft number
    final_result = []
    
    # Dictionary to hold the entries grouped by their start date
    grouped = defaultdict(list)
    
    # Populate the dictionary grouping by start_date
    for entry in list_ids_sorted:
        start_date = entry[2]['start_date']
        grouped[start_date].append(entry)
    
    # For each group with the same start_date, intercalate by n_cauda
    for date, group in grouped.items():
        # Split into groups by n_cauda
        groups_by_cauda = defaultdict(list)
        for item in group:
            groups_by_cauda[item[0]].append(item)
        
        # Intercalate the aircrafts by n_cauda
        intercalated = []
        while any(groups_by_cauda.values()):
            for cauda in sorted(groups_by_cauda):  # sorted ensures we process by aircraft number
                if groups_by_cauda[cauda]:
                    intercalated.append(groups_by_cauda[cauda].pop(0))
        
        # Add intercalated result to final result
        final_result.extend(intercalated)
    
    return final_result

# Example usage
# teste = search_IC(Aircrafts, ['09'])
# teste = ordenar_lista(list_ids=teste)
