import os
import re
import csv

path = []
directory = r'data\raw_html'
for file_name in os.listdir(directory):
    full_path = os.path.join(directory, file_name)
    if os.path.isfile(full_path):
        path.append(full_path)
        
for p in path:
    with open(p, "r", encoding="utf-8") as f:
        text = f.read()
    
    matches = re.findall(r'<div id="g_1_(.*?)"', text)
    
    file_name = os.path.basename(p)
    season_match = re.search(r'\d{4}-\d{4}', file_name)
    
    if season_match:
        season = season_match.group(0).replace('-', '_')
        csv_file_path = f'data/match_ids/football_{season}_ids.csv'
        
        with open(csv_file_path, 'a', newline='', encoding="utf8") as csvfile:
            csv_writer = csv.writer(csvfile)
            for match_id in matches:
                csv_writer.writerow([match_id])

print("ID meczy zostały zapisane do plików sezonowych CSV.")
