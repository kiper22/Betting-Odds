import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from unidecode import unidecode
import time
import os
import pandas as pd
import logging


def setup_logger(discipline, season):
    global time_start
    time_start = time.time()
    
    logger = logging.getLogger('debugger')
    logger.setLevel(logging.DEBUG)
    logging.root.handlers = []
    file_handler = logging.FileHandler(f'debug_{discipline}_{season}.log')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def get_soup(driver, url):
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    except:
        pass

    return BeautifulSoup(driver.page_source, 'html.parser')

def merge_into_df(df, idx, *dicts):
    for d in dicts:
        if d:
            for k, v in d.items():
                df.loc[idx, k] = v

# Exception 1 - header
def fill_headline(soup) -> dict: # change creating/filling ids col and row
    dictionary = dict()    
    date_div = soup.find('div', class_='duelParticipant__startTime')
    date = date_div.get_text(strip=True) if date_div else None
    
    dictionary['date'] = date # date
    
    span_country = soup.find('span', class_='tournamentHeader__country')
    if not span_country:
        return {}

    league_text = span_country.text.strip()      # league
    league_name = league_text.split(':')[-1].strip()
    league = league_name.split('-')[0]
    league = league.strip()   
    parts = league_name.split('-')[-1]
    _parts = parts.split()

    for part in _parts:
        if part.isdigit():
            turn = int(part)
            break

    dictionary['league'] = league                  
    dictionary['turn'] = turn     
             
    home_team_name = soup.find('div', class_='duelParticipant__home').find('a', class_='participant__participantName').text.strip()
    away_team_name = soup.find('div', class_='duelParticipant__away').find('a', class_='participant__participantName').text.strip()

    dictionary['team_1'] = home_team_name        # team 1 (home)
    dictionary['team_2'] = away_team_name        # team 2 (away)
    
    result_element = soup.find('div', class_='detailScore__wrapper')
    goals_1 = result_element.find_all('span')[0].text.strip()
    goals_2 = result_element.find_all('span')[2].text.strip()
    
    dictionary['goals_1'] = goals_1              # goals team 1
    dictionary['goals_2'] = goals_2              # goals team 2
    
    if int(goals_1)>int(goals_2):
        winner = 1
    elif int(goals_1)==int(goals_2):
        winner = 0
    else:
        winner = 2
    dictionary['winner'] = winner                # winner
    
    return dictionary

# Exception 2 - match data
def extract_stats(soup) -> dict:
    dictionary = dict()
    triple_list = []
    stat_divs = soup.find_all('div', class_='wcl-row_OFViZ')

    for stat_div in stat_divs:
        try:
            values = stat_div.find_all('strong', {'data-testid': ['wcl-scores-simpleText1', 'wcl-scores-simpleText-01']})  
            category_div = stat_div.find('div', {'data-testid': 'wcl-statistics-category'})

            if category_div:
                category = category_div.text.strip()
            else:
                raise ValueError("Nie znaleziono kategorii statystyki")

            if len(values) == 2:
                triple_values = [values[0].text.strip(), category, values[1].text.strip()]
            elif len(values) == 3: 
                triple_values = [values[0].text.strip(), category, values[2].text.strip()]
            else:
                raise ValueError("Nieoczekiwany format danych w statystykach")

            triple_list.append(triple_values)

        except Exception as e:
            print(f"Error extracting values: {e}")

    column_mappings = {
        'Oczekiwane_bramki_(xG)': 'expected_goals',
        'Posiadanie_pilki': 'possession',
        'Sytuacje_bramkowe': 'goal_chances',
        'Strzaly_na_bramke': 'shots_on_target',
        'Strzaly_niecelne': 'shots_off_target',
        'Strzaly_zablokowane': 'blocked_shots',
        'Rzuty_wolne': 'free_kicks',
        'Rzuty_rożne': 'corner_kicks',
        'Spalone': 'offsides',
        'Wrzuty_z_autu': 'throw_ins',
        'Interwencje_bramkarzy': 'goalkeeper_saves',
        'Faule': 'fouls',
        'Żółte_kartki': 'yellow_cards',
        'Czerwone_kartki': 'red_cards',
        'Ataki': 'attacks',
        'Niebezpieczne_ataki': 'dangerous_attacks'
    }

    for i, triple_values in enumerate(triple_list):
        column_name = unidecode(triple_values[1].replace(' ', '_'))
        
        if column_name in column_mappings:
            english_column_name = column_mappings[column_name]
            dictionary[f"{english_column_name}_1"] = triple_values[0]  
            dictionary[f"{english_column_name}_2"] = triple_values[2]  
    
    return dictionary

# Exception 3 - team squats
def team_squats(soup) -> dict:
    dictionary = dict()

    formations = soup.find_all('span', class_='wcl-overline_rOFfd wcl-scores-overline-02_n9EXm wcl-cell_LDXJM')
    dictionary['team_1_formation'] = formations[0].text.strip()
    dictionary['team_2_formation'] = formations[2].text.strip()
    
    return dictionary

# Exception 4 - team ratings     
def fill_team_ratings(team_section, team_number) -> dict:
    dictionary = dict()
    
    if not team_section:
        print(f"Brak danych dla team_{team_number}")
        return {}
    
    team_lines = team_section.find_all('div', class_='lf__line')

    for i, line in enumerate(team_lines):
        players_ratings = []

        for player in line.find_all('div', class_='lf__player'):
            rating_element = player.find('span', {'data-testid': ['wcl-scores-caption-03', 'wcl-scores-caption1']})

            if rating_element:
                players_ratings.append(rating_element.text.strip())
            else:
                players_ratings.append(None)
        
        dictionary[f'team_{team_number}_line_{i}'] = "-".join(str(x) for x in players_ratings)
    
    return dictionary

# Exceptions 5 and 6
def bets_1(soup, col_names) -> dict:
    '''Extract standard and double chance bet rates. For standard and double chance needs to be called'''

    dictionary = dict()
    bookmaker_rows = soup.find_all('div', class_='ui-table__row')
    for row in bookmaker_rows:
        link = row.find('a', class_='prematchLink')
        if not link:
            continue

        bookmaker_name = link.get('title', '')

        if 'eFortuna.pl' in bookmaker_name:
            odds = row.find_all('a', class_=['oddsCell__odd', 'oddsCell__noOddsCell'])
            
            if odds and len(odds) == 3: # >= było
                dictionary[col_names[0]] = odds[0].text.strip()
                dictionary[col_names[1]] = odds[1].text.strip()
                dictionary[col_names[2]] = odds[2].text.strip()
    
    return dictionary    

# Exception 7
def bets_below_above(soup) -> dict:
    dictionary = dict()
    
    over_under_rows = soup.select('div.ui-table__row')

    for row in over_under_rows:
        bookmaker_name = row.find('a', class_='prematchLink')
        if bookmaker_name and 'eFortuna.pl' in bookmaker_name.get('title', ''):

            bet_value_span = row.find('span', class_='wcl-oddsValue_Fc9sZ')
            if bet_value_span:
                bet_value = bet_value_span.text.strip()

                odds = row.find_all('a', class_='oddsCell__odd')

                odd_above = odds[0].text.strip() if len(odds) > 0 else '-1'
                odd_below = odds[1].text.strip() if len(odds) > 1 else '-1'

                column_above = f'bet_above_{bet_value}'
                column_below = f'bet_below_{bet_value}'

                dictionary[column_above] = odd_above
                dictionary[column_below] = odd_below
    
    return dictionary

# Exception 8
def handicap(soup)->dict:
    dictionary = dict()
    handicap_rows = soup.select('div.ui-table__row, div.oddsTab__tableWrapper div.ui-table__row')

    for row in handicap_rows:
        bookmaker_name = row.find('a', class_='prematchLink')
        handicap_span = row.find('span', class_=['wcl-oddsValue_Fc9sZ', 'oddsCell__noOddsCell', 'oddsCell__odd'])
        
        if bookmaker_name and 'eFortuna.pl' in bookmaker_name.get('title', '') and handicap_span:

            handicap_value = handicap_span.text.strip()

            odds = row.find_all('a', class_='oddsCell__odd')
            odd_1 = odds[0].text.strip() if len(odds) > 0 else '-1'
            odd_2 = odds[1].text.strip() if len(odds) > 1 else '-1'

            dictionary[f'bet_handicap{handicap_value}_1'] = odd_1
            dictionary[f'bet_handicap{handicap_value}_2'] = odd_2
    
    return dictionary


directory = r'data\match_ids'
for file_name in os.listdir(directory):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(5)
    
    discipline, season = file_name.split('_')[0], file_name.split('_')[1] + "_" + file_name.split('_')[2]
    output_file_path = f"data/extracted_data/{discipline}_{season}_data.csv"
    
    ids = []
    with open(f"{directory}\{file_name}", 'r') as f:
        for line in f.readlines():
            ids.append(line.strip())
    
    if os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0:
        try:
            df = pd.read_csv(output_file_path)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame() 
        
    if 'id' not in df.columns:
        df['id'] = pd.Series(dtype=str)
        df['match_id'] = pd.Series(dtype=str)


    logger = setup_logger(discipline, season)
    
    for match_id in ids:
        if len(df[df['match_id'] == id]) == 1:
            logger.warning(f"WARNING: match id had repeat: {match_id}")
            continue
        print(id)
        # else:
        # new_df = pd.DataFrame([{'id': id}]) 
        # df = pd.concat([df, new_df], ignore_index=True)
        # _idx = df.shape[0] - 1
        
        # df.loc[_idx, 'match_id'] = id
        
        _idx = len(df)
        df.loc[_idx] = {'id': _idx, 'match_id': match_id}
        

        
        url = f'https://www.flashscore.pl/mecz/{match_id}/#/szczegoly-meczu/statystyki-meczu/0'
        try:
            soup = get_soup(driver, url)
            dict1 = fill_headline(soup)
            dict2 = extract_stats(soup)
            merge_into_df(df, _idx, dict1, dict2)
        except:
            logger.exception(f"Exception_0 occured when filling match stats for id: {match_id};{url}")
            continue        # if cant extract most important data skip this match
            
            
        # Approach 3
        url = f'https://www.flashscore.pl/mecz/{match_id}/#/szczegoly-meczu/sklady'
        
        try:
            soup = get_soup(driver, url)

            dict_form = team_squats(soup)
            merge_into_df(df, _idx, dict_form)

            home_team_section = soup.find('div', class_='lf__formation')
            away_team_section = soup.find('div', class_='lf__formation lf__formationAway')

            dict_h = fill_team_ratings(home_team_section, 1)
            dict_a = fill_team_ratings(away_team_section, 2)
            merge_into_df(df, _idx, dict_h, dict_a)

        except:
            logger.exception(f"Exception_1 occured when filling match teams for id: {match_id};{url}")

        
        url = f'https://www.flashscore.pl/mecz/{match_id}/#/zestawienie-kursow/kursy-1x2/koniec-meczu'
        try:
            soup = get_soup(driver, url)
            dict_bets = bets_1(soup, ['bet_1', 'bet_x', 'bet_2'])
            merge_into_df(df, _idx, dict_bets)
        except:
            logger.exception(f"Exception_2 occured when filling match bets 1x2 for id: {match_id};{url}")


        url = f'https://www.flashscore.pl/mecz/{match_id}/#/zestawienie-kursow/podwojna-szansa/koniec-meczu'
        try:
            soup = get_soup(driver, url)
            dict_bets = bets_1(soup, ['bet_1x', 'bet_12', 'bet_x2'])
            merge_into_df(df, _idx, dict_bets)
        except:
            logger.exception(f"Exception_3 occurred when filling match bets double chance for id: {match_id};{url}")



        url = f'https://www.flashscore.pl/mecz/{match_id}/#/zestawienie-kursow/handicap-azjat/koniec-meczu'
        try:
            soup = get_soup(driver, url)
            new_dict = handicap(soup)
            merge_into_df(df, _idx, new_dict)
        except Exception as e:
            logger.exception(f"Exception_4 occurred when filling match bets handicap for id: {match_id}; {url}. Error: {e}")
        
        
        url = f'https://www.flashscore.pl/mecz/{match_id}/#/zestawienie-kursow/powyzej-ponizej/koniec-meczu'
        try:
            soup = get_soup(driver, url)
            dict_ou = bets_below_above(soup)
            merge_into_df(df, _idx, dict_ou)


        except Exception as e:
            logger.exception(f"Exception_5 occurred when filling match bets above and below for id: {match_id}; {url}. Error: {e}")

        if ids.index(match_id) % 50 == 0:
            driver.quit()
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(2)
            
        df.to_csv(output_file_path, index=False)
        # defragmentation_iter += 1
        # if defragmentation_iter >= DEFRAGMENTATION_BATCH_SIZE:
        #     df = df.copy()
    
    
    time_end = time.time()
    logger.debug(f"Ended after: {time_end-time_start}")
    
    driver.quit()


