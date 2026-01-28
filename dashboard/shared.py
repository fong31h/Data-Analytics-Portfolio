from pathlib import Path

import pandas as pd
import json

app_dir = Path(__file__).parent
with open('Data_Files/names.txt', 'r') as f:
    ex_list = [line.strip() for line in f]
with open('Data_Files/best_names.txt', 'r') as f:
    ex_list2 = [line.strip() for line in f]
dropdown_df = pd.read_csv('Data_Files/dropdown_df.csv')
with open('Data_Files/image_dict.json') as f:
    image_dict = json.load(f)
with open('Data_Files/expansions.txt', 'r') as f:
    expansions = [line.strip() for line in f]