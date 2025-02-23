import os               
import ast
import re
import pdfplumber

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from IPython.display import display
from pandasgui import show

sns.set_theme()

pdfs_short = 'pdfs/short'
pdf_free = 'pdfs/free'

all_paths = []
for folder in [pdfs_short, pdf_free]:
  paths = [os.path.join(folder, filename)
          for filename in os.listdir(folder)
          if filename.endswith('.pdf')]
  all_paths.extend(paths)

def extract_data(pdf_paths):
    all_entries = []
    short_entries_num = []
    free_entries_num = []
    pdf_table_map = {}  
    index_counter = 0 
    
    for pdf_path in pdf_paths:
        try:
            with pdfplumber.open(pdf_path) as f:
                all_page_tables = [page.extract_tables() for page in f.pages]
                tables = [x for entry in all_page_tables for x in entry]
                all_entries.extend(tables)

                if 'short' in pdf_path:
                    short_entries_num.append(len(tables))
                else:
                    free_entries_num.append(len(tables)) 
                for table in tables:
                  pdf_table_map[index_counter] = pdf_path  
                  index_counter += 1 
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
    
    return all_entries, short_entries_num, free_entries_num, pdf_table_map

single_entries, short_entries_num, free_entries_num, pdf_table_map = extract_data(all_paths)
print(sum(short_entries_num))
print(sum(free_entries_num))


for i in range(len(single_entries)):
    if len(single_entries[i]) <= 2:
        print(f"Problem with table {i} in a PDF {pdf_table_map[i]}. It has only {len(single_entries[i])} sublists.")


for i in range(len(single_entries)):
    single_entries[i][0][0] = single_entries[i][0][0].rsplit('\n', 1)[-1]
    single_entries[i][1][0] = '\n1' + single_entries[i][1][0].split('\n1', 1)[1]
    single_entries[i][1][0] = single_entries[i][1][0].split('\nProgram')[0]

single_entries_updated = []
extracted_elements = []
for entry in single_entries:
  element_data = entry[1][0].split('\n')[1:-1]
  single_entries_updated.append([entry[0], element_data])
  extracted_elements.append(element_data)

skaters_list = []
for element in single_entries_updated:

  skater_info = element[0][0].split(" ")

  skater_rank = int(skater_info[0])
  skater_name = " ".join(skater_info[1:-6])
  skater_nation = skater_info[-6]
  skater_startnr = int(skater_info[-5])
  segment_total = float(skater_info[-4])
  segment_tech = float(skater_info[-3])
  segment_pcs = float(skater_info[-2])
  segment_deduction = float(skater_info[-1])

  skater_data = {
      "rank": skater_rank,
      "name": skater_name,
      "nation": skater_nation,
      "startnr": skater_startnr,
      "total": segment_total,
      "tech": segment_tech,
      "pcs": segment_pcs,
      "deductions": segment_deduction
  }

  skaters_list.append(skater_data)

# if there is no Info about element the list has 14 elements, otherwise 15 or more

def process_element_data(elements):
    processed_elements = []
    calls = []
    scores = []
    for entry in elements:
      for element in entry:
        parts = re.split(r'\s+', element.strip())

        if len(parts) == 14:
          element = parts[1]
          call = 'None'
        else:
          if parts[3] == 'x':
            element = parts[1]
            call = parts[3]
          elif parts[4] == 'x':
            element = parts[1]
            call = parts[2], parts[4]
          else:
            if parts[3] in ('F', 'e', '!', 'q', '*', '<'):
              element = parts[1]
              call = parts[2], parts[3]
            else:
              element = parts[1]
              call = parts[2]

        final_value = float(parts[-1])
        goe = float(parts[-11])
        judges_scores = [float(score) if score != '-' else 'None' for score in parts[-10:-2]]
        base_value = round(final_value - abs(goe) if goe > 0 else final_value + abs(goe), 2)

        processed_elements.append(element)
        calls.append(call)
        scores.append((base_value, goe, judges_scores, final_value))

    return processed_elements, calls, scores

elements, calls, scores = process_element_data(extracted_elements)

skater_performance = list(zip(elements, calls, scores))


short_skater_count = sum(short_entries_num)

""" this part calculates how many elements in the skater_performance list should be assigned to particular skater 
 skaters lists is the same size as the number of tables extracted from short programs pdfs
 for short program there are 7 elements for one skater
 for free program there are 12 elements for one skater 
 the cumulative indices list holds the indices for start and finish of one performance """

skater_segment_sizes = []
for i in range(len(skaters_list)): 
    if i < short_skater_count:     
        skater_segment_sizes.append(7)  
    else:
        skater_segment_sizes.append(12) 

cumulative_indices = np.cumsum([0] + skater_segment_sizes)

data = []
for i, skater in enumerate(skaters_list):
    start_idx = cumulative_indices[i]
    end_idx = cumulative_indices[i + 1]
    
    performances_for_skater = skater_performance[start_idx:end_idx]

    for performance in performances_for_skater:
        row = skater.copy()
        row['element'] = performance[0]
        row['call'] = performance[1]
        row['base_value'] = performance[2][0]
        row['goe'] = performance[2][1]
        row['judges_scores'] = performance[2][2]
        row['final_element_score'] = performance[2][3]
        data.append(row)

df = pd.DataFrame(data)
show(df)


