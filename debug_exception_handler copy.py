import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd

# Konfiguracja Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

# Ścieżki plików
debug_filepath = 'debug_idse0_2023_24.csv.log'
csv_filepath = r"data\extracted_data\23_24_v2.csv"

# Wczytaj zawartość pliku logów
with open(debug_filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Regex do podziału logów (uwzględnia linię z błędem)
pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - Exception_\d+ occured .*?)\n(?=Traceback \(most recent call last\):)'
tracebacks = re.split(pattern, content)

# Połączenie nagłówka z tracebackiem
traceback_list = []
for i in range(1, len(tracebacks), 2):
    traceback_list.append(tracebacks[i] + '\n' + tracebacks[i + 1])

# Usuń puste elementy
traceback_list = [tb.strip() for tb in traceback_list if tb.strip()]
print("Razem błędów: ", len(traceback_list))

idx = 0
while idx < len(traceback_list):  # Przechodzimy przez wszystkie błędy
    sublines = traceback_list[idx].split("\n")
    match_id = sublines[0].split("id: ")[1].split(";")[0]
    match_id = match_id.strip()
    match_url = sublines[0].split(";")[1]

    print(f"\n=== Bug {idx+1} ==={idx}\n" + match_id)

    try:
        driver.get(match_url)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        span_country = soup.find('span', class_='tournamentHeader__country')
        league_text = span_country.text.strip()
        print(league_text)

    except:
        print("Błąd pobierania strony!")
        idx += 1
        continue

    x = input("Czy usunąć? (t = tak / inny klawisz = nie): ")
    if x != 't':
        idx += 1
        continue

    # 1. Usuń z traceback_list
    removed_traceback = traceback_list.pop(idx)  # Usuń i idź dalej

    # # 2. Usuń z pliku `filtered_20_21.log`
    with open(debug_filepath, 'w') as f:
        f.write('\n'.join(traceback_list))

    # 3. Usuń wiersz z CSV
    if os.path.exists(csv_filepath):
        df = pd.read_csv(csv_filepath, dtype=str)
        df = df[df['match_id'].str.strip() != match_id]
        df.to_csv(csv_filepath, index=False)


        
    print("Usunięto błąd i zaktualizowano pliki.\n" + "=" * 50)

# Zamknięcie Selenium
driver.quit()
