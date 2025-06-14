import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from unidecode import unidecode
import time
import os
import pandas as pd
import logging

DEFRAGMENTATION_BATCH_SIZE = 100
defragmentation_iter = 0

    


url = 'https://www.flashscore.pl/mecz/0E9VSinE/#/szczegoly-meczu/statystyki-meczu/0'

def get_soup(driver, url):
    driver.get(url)
    time.sleep(0.7)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    return soup

# Exception 0
def fill_headline(soup, df, id): # change creating/filling ids col and row
    df.at[id, 'id'] = id 
    date = soup.find('div', class_='duelParticipant__startTime').find('div', class_='').text.strip()
    df.at[id, 'date'] = date                    # date
    span_country = soup.find('span', class_='tournamentHeader__country')
    league_text = span_country.text.strip()      # league
    league_name = league_text.split(':')[-1].strip()
    league = league_name.split('-')[0]
    parts = league_name.split('-')[-1]
    league = league.strip()   
    _parts = parts.split()

    for part in _parts:
        if part.isdigit():
            turn = int(part)
            break

    df.at[id, 'league'] = league                  # league
    df.at[id, 'turn'] = turn              # turn
    home_team_element = soup.find('div', class_='duelParticipant__home').find('a', class_='participant__participantName')
    away_team_element = soup.find('div', class_='duelParticipant__away').find('a', class_='participant__participantName')
    home_team_name = home_team_element.text.strip()
    away_team_name = away_team_element.text.strip()
    df.at[id, 'team_1'] = home_team_name        # team 1 (home)
    df.at[id, 'team_2'] = away_team_name        # team 2 (away)
    result_element = soup.find('div', class_='detailScore__wrapper')
    goals_1 = result_element.find_all('span')[0].text.strip()
    goals_2 = result_element.find_all('span')[2].text.strip()
    df.at[id, 'goals_1'] = goals_1              # goals team 1
    df.at[id, 'goals_2'] = goals_2              # goals team 2
    if int(goals_1)>int(goals_2):
        winner = 1
    elif int(goals_1)==int(goals_2):
        winner = 0
    else:
        winner = 2
    df.at[id, 'winner'] = winner                # winner

# Exception 0
def extract_stats(soup):
    triple_list = []
    stat_divs = soup.find_all('div', class_='wcl-row_OFViZ')

    for stat_div in stat_divs:
        try:
            values = stat_div.find_all('strong', {'data-testid': 'wcl-scores-simpleText1'})
            category = stat_div.find('div', {'data-testid': 'wcl-statistics-category'}).text.strip()
            triple_values = [values[0].text.strip(), category, values[2].text.strip()]
            triple_list.append(triple_values)
        except Exception as e:
            print("An error occurred while extracting values:", e)
    
    return triple_list

def extract_stats_v2(soup):
    triple_list = []
    stat_divs = soup.find_all('div', class_='wcl-row_OFViZ')

    for stat_div in stat_divs:
        try:
            # Pobieramy wartości dla obu drużyn
            values = stat_div.find_all('strong', {'data-testid': 'wcl-scores-simpleText-01'})  
            category_div = stat_div.find('div', {'data-testid': 'wcl-statistics-category'})

            if category_div:
                category = category_div.text.strip()
            else:
                raise ValueError("Nie znaleziono kategorii statystyki")

            # Obsługa różnych układów strony
            if len(values) == 2:
                triple_values = [values[0].text.strip(), category, values[1].text.strip()]
            elif len(values) == 3:  # Jeśli są 3 wartości, pobieramy 1 i 3 (środkowy może być błędny)
                triple_values = [values[0].text.strip(), category, values[2].text.strip()]
            else:
                raise ValueError("Nieoczekiwany format danych w statystykach")

            triple_list.append(triple_values)

        except Exception as e:
            print(f"Error extracting values: {e}")

    return triple_list


# Exception 0
def fill_stats(df, triple_list, id):
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
            df.loc[id, f"{english_column_name}_1"] = triple_values[0]  
            df.loc[id, f"{english_column_name}_2"] = triple_values[2]  

# Exception 1          
def fill_team_ratings(team_section, team_number, df, id):
        team_lines = team_section.find_all('div', class_='lf__line')
        i = 0
        for line in team_lines:
            players_ratings = []

            for player in line.find_all('div', class_='lf__player'):
                rating_element = player.find('div', class_='wcl-badgeRating_1MU6s')
                if rating_element:
                    rating = rating_element.find('span', {'data-testid': 'wcl-scores-caption1'}).text
                    players_ratings.append(rating)
            
            df.loc[id, f'team_{team_number}_line_{i}'] =  "-".join(str(x) for x in players_ratings)
            i += 1

# Exception 1          
def fill_team_ratings_v2(team_section, team_number, df, id):
        team_lines = team_section.find_all('div', class_='lf__line')
        i = 0
        for line in team_lines:
            players_ratings = []

            for player in line.find_all('div', class_='lf__player'):
                rating_element = player.find('div', class_='wcl-badgeRating_1MU6s')
                if rating_element:
                    # rating = rating_element.find('span', {'data-testid': 'wcl-scores-caption1'}).text # ta linia
                    rating = rating_element.find('span', {'data-testid': 'wcl-scores-caption-03'}).text
                    players_ratings.append(rating)
            
            df.loc[id, f'team_{team_number}_line_{i}'] = "-".join(str(x) for x in players_ratings)
            i += 1

# Exception 1
def get_team_formations(soup, df, _idx):
    formations = soup.find_all('span', class_='wcl-overline_rOFfd wcl-scores-overline-02_n9EXm wcl-cell_LDXJM')
    df.loc[_idx, 'team_1_formation'] = formations[0].text.strip()
    df.loc[_idx, 'team_2_formation'] = formations[2].text.strip()

def fill_team_ratings_v3(team_section, team_number, df, _idx):
    if not team_section:
        print(f"Brak danych dla team_{team_number}")
        return
    
    team_lines = team_section.find_all('div', class_='lf__line')
    
    for i, line in enumerate(team_lines):
        players_ratings = []
        
        for player in line.find_all('div', class_='lf__player'):
            rating_element = player.find('span', {'data-testid': 'wcl-scores-caption-03'})
            if rating_element:
                players_ratings.append(rating_element.text.strip())

        df.loc[_idx, f'team_{team_number}_line_{i}'] = "-".join(players_ratings)


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


    time_start = time.time()
    logger = logging.getLogger('debugger')
    logger.setLevel(logging.DEBUG)
    logging.root.handlers = []
    file_handler = logging.FileHandler(f'debug_{discipline}_{season}.log')
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    for id in ids:
        if len(df[df['match_id'] == id]) == 1:
            logger.warning(f"WARNING: match id had repeat: {id}")
            continue
        print(id)
        # else:
        # new_df = pd.DataFrame([{'id': id}]) 
        # df = pd.concat([df, new_df], ignore_index=True)
        # _idx = df.shape[0] - 1
        
        # df.loc[_idx, 'match_id'] = id
        
        _idx = len(df)
        df.loc[_idx] = {'id': _idx, 'match_id': id}
        

        
        # url = f'https://www.flashscore.pl/mecz/{id}/#/szczegoly-meczu/statystyki-meczu/0'
        # try:
        #     soup = get_soup(driver, url)
        #     fill_headline(soup, df, _idx)
        #     triple_list = extract_stats_v2(soup)
        #     fill_stats(df, triple_list, _idx)
        # except:
        #     logger.exception(f"Exception_0 occured when filling match stats for id: {id};{url}")
        #     continue        # if cant extract most important data skip this match


        # approach 1
        # url = f'https://www.flashscore.pl/mecz/{id}/#/szczegoly-meczu/sklady'
        # try:
        #     soup = get_soup(driver, url)
            
        #     formation_section = soup.find('div', class_='lf__header section__title')
        #     formations = formation_section.find_all('span', 'lf__headerPart')
        #     df.loc[_idx, 'team_1_formation'] = formations[0].text.strip()
        #     df.loc[_idx, 'team_2_formation'] = formations[1].text.strip()
            
        #     home_team_section = soup.find('div', class_='lf__formation')
        #     away_team_section = soup.find('div', class_='lf__formation lf__formationAway')
            
        #     fill_team_ratings(home_team_section, 1, df, _idx)
        #     fill_team_ratings(away_team_section, 2, df, _idx)
        # except:
        #     logger.exception(f"Exception_1 occured when filling match teams for id: {id};{url}")
        
        # approach 2
        # url = f'https://www.flashscore.pl/mecz/{id}/#/szczegoly-meczu/sklady'
        # try:
        #     soup = get_soup(driver, url)
            
        #     formations = soup.find_all('span', class_='wcl-overline_rOFfd wcl-scores-overline-02_n9EXm')
        #     df.loc[_idx, 'team_1_formation'] = formations[0].text.strip()
        #     df.loc[_idx, 'team_2_formation'] = formations[2].text.strip()
            
        #     home_team_section = soup.find('div', class_='lf__formation')
        #     away_team_section = soup.find('div', class_='lf__formation lf__formationAway')
            
        #     fill_team_ratings_v2(home_team_section, 1, df, _idx)
        #     fill_team_ratings_v2(away_team_section, 2, df, _idx)
        # except:
        #     logger.exception(f"Exception_1 occured when filling match teams for id: {id};{url}")
            
            
        # Approach 3
        # url = f'https://www.flashscore.pl/mecz/{id}/#/szczegoly-meczu/sklady'
        
        # try:
        #     soup = get_soup(driver, url)

        #     get_team_formations(soup, df, _idx)

        #     home_team_section = soup.find('div', class_='lf__formation')
        #     away_team_section = soup.find('div', class_='lf__formation lf__formationAway')

        #     fill_team_ratings_v3(home_team_section, 1, df, _idx)
        #     fill_team_ratings_v3(away_team_section, 2, df, _idx)

        # except:
        #     logger.exception(f"Exception_1 occured when filling match teams for id: {id};{url}")

        
        url = f'https://www.flashscore.pl/mecz/{id}/#/zestawienie-kursow/kursy-1x2/koniec-meczu'
        try:
            soup = get_soup(driver, url)
            
            bookmaker_rows = soup.find_all('div', class_='ui-table__row')
            for row in bookmaker_rows:
                bookmaker_name = row.find('a', class_='prematchLink').get('title')

                if 'eFortuna.pl' in bookmaker_name:
                    odds = row.find_all('a', class_=['oddsCell__odd', 'oddsCell__noOddsCell'])
                    
                    if odds and len(odds) >= 3:
                        df.loc[_idx, 'bet_1'] = odds[0].text.strip()
                        df.loc[_idx, 'bet_x'] = odds[1].text.strip()
                        df.loc[_idx, 'bet_2'] = odds[2].text.strip()
        except:
            logger.exception(f"Exception_2 occured when filling match bets 1x2 for id: {id};{url}")


        url = f'https://www.flashscore.pl/mecz/{id}/#/zestawienie-kursow/podwojna-szansa/koniec-meczu'
        try:
            soup = get_soup(driver, url)
            
            bookmaker_rows = soup.find_all('div', class_='ui-table__row')

            for row in bookmaker_rows:
                bookmaker_name = row.find('a', class_='prematchLink').get('title')

                if 'eFortuna.pl' in bookmaker_name:
                    odds_cells = row.find_all(['a', 'span'], class_=['oddsCell__odd', 'oddsCell__noOddsCell'])

                    df.loc[_idx, 'bet_1x'] = odds_cells[0].text.strip() if len(odds_cells) > 0 and odds_cells[0].name == 'a' else '0'
                    df.loc[_idx, 'bet_12'] = odds_cells[1].text.strip() if len(odds_cells) > 1 and odds_cells[1].name == 'a' else '0'
                    df.loc[_idx, 'bet_x2'] = odds_cells[2].text.strip() if len(odds_cells) > 2 and odds_cells[2].name == 'a' else '0'
        except:
            logger.exception(f"Exception_3 occurred when filling match bets double chance for id: {id};{url}")

        
        # Older website version
        # url = f'https://www.flashscore.pl/mecz/{id}/#/zestawienie-kursow/handicap-azjat/koniec-meczu'
        # try:
        #     soup = get_soup(driver, url)
            
        #     handicap_rows = soup.select('div.oddsTab__tableWrapper div.ui-table__row')

        #     for row in handicap_rows:
        #         bookmaker_name = row.find('a', class_='prematchLink')
        #         if bookmaker_name and 'eFortuna.pl' in bookmaker_name.get('title'):
                    
        #             handicap_span = row.find('span', class_=['oddsCell__noOddsCell', 'oddsCell__odd', 'oddsCell__noOddsCell'])
        #             if handicap_span:
        #                 handicap_value = handicap_span.text.strip()
                        
        #                 odds = row.find_all('a', class_='oddsCell__odd')
                        
        #                 odd_1 = odds[0].text.strip() if len(odds) > 0 else '-1'
        #                 odd_2 = odds[1].text.strip() if len(odds) > 1 else '-1'
                        
        #                 column_1 = f'bet_handicap{handicap_value}_1'
        #                 column_2 = f'bet_handicap{handicap_value}_2'
                        
        #                 df.loc[_idx, column_1] = odd_1
        #                 df.loc[_idx, column_2] = odd_2
        # except:
        #     logger.exception(f"Exception_4 occured when filling match bets handicap for id: {id};{url}")

        # url = f'https://www.flashscore.pl/mecz/{id}/#/zestawienie-kursow/handicap-azjat/koniec-meczu'
        # try:
        #     soup = get_soup(driver, url)
            
        #     handicap_rows = soup.select('div.ui-table__row')

        #     for row in handicap_rows:
        #         bookmaker_name = row.find('a', class_='prematchLink')
        #         if bookmaker_name and 'eFortuna.pl' in bookmaker_name.get('title', ''):

        #             handicap_span = row.find('span', class_='wcl-oddsValue_Fc9sZ')
        #             if handicap_span:
        #                 handicap_value = handicap_span.text.strip()

        #                 odds = row.find_all('a', class_='oddsCell__odd')

        #                 odd_1 = odds[0].text.strip() if len(odds) > 0 else '-1'
        #                 odd_2 = odds[1].text.strip() if len(odds) > 1 else '-1'

        #                 # Jeśli kursy mają "Kursy usunięte przez bukmachera" - zignoruj
        #                 if 'Kursy usunięte przez bukmachera' in odd_1:
        #                     odd_1 = '-1'
        #                 if 'Kursy usunięte przez bukmachera' in odd_2:
        #                     odd_2 = '-1'

        #                 column_1 = f'bet_handicap{handicap_value}_1'
        #                 column_2 = f'bet_handicap{handicap_value}_2'

        #                 # Zapisanie danych do DataFrame
        #                 df.loc[_idx, column_1] = odd_1
        #                 df.loc[_idx, column_2] = odd_2

        # except Exception as e:
        #     logger.exception(f"Exception_4 occurred when filling match bets handicap for id: {id}; {url}. Error: {e}")



        # url = f'https://www.flashscore.pl/mecz/{id}/#/zestawienie-kursow/powyzej-ponizej/koniec-meczu'
        # try:
        #     soup = get_soup(driver, url)
            
        #     over_under_rows = soup.select('div.ui-table.oddsCell__odds div.ui-table__row')

        #     for row in over_under_rows:
        #         bookmaker_name = row.find('a', class_='prematchLink')
        #         if bookmaker_name and 'eFortuna.pl' in bookmaker_name.get('title'):
                    
        #             bet_value_span = row.find('span', class_=['oddsCell__noOddsCell', 'oddsCell__odd', 'oddsCell__noOddsCell'])
        #             if bet_value_span:
        #                 bet_value = bet_value_span.text.strip()
                        
        #                 odds = row.find_all('a', class_='oddsCell__odd')
                        
        #                 odd_above = odds[0].text.strip() if len(odds) > 0 else '-1'
        #                 odd_below = odds[1].text.strip() if len(odds) > 1 else '-1'
                        
        #                 column_above = f'bet_above_{bet_value}'
        #                 column_below = f'bet_below_{bet_value}'
                        
        #                 df.loc[_idx, column_above] = odd_above
        #                 df.loc[_idx, column_below] = odd_below
        # except:
        #     logger.exception(f"Exception_5 occured when filling match bets above and below for id: {id};{url}")
        
        
        # url = f'https://www.flashscore.pl/mecz/{id}/#/zestawienie-kursow/powyzej-ponizej/koniec-meczu'
        # try:
        #     soup = get_soup(driver, url)
            
        #     over_under_rows = soup.select('div.ui-table__row')

        #     for row in over_under_rows:
        #         bookmaker_name = row.find('a', class_='prematchLink')
        #         if bookmaker_name and 'eFortuna.pl' in bookmaker_name.get('title', ''):

        #             bet_value_span = row.find('span', class_='wcl-oddsValue_Fc9sZ')
        #             if bet_value_span:
        #                 bet_value = bet_value_span.text.strip()

        #                 odds = row.find_all('a', class_='oddsCell__odd')

        #                 odd_above = odds[0].text.strip() if len(odds) > 0 else '-1'
        #                 odd_below = odds[1].text.strip() if len(odds) > 1 else '-1'

        #                 if 'Kursy usunięte przez bukmachera' in odd_above:
        #                     odd_above = '-1'
        #                 if 'Kursy usunięte przez bukmachera' in odd_below:
        #                     odd_below = '-1'

        #                 column_above = f'bet_above_{bet_value}_1'
        #                 column_below = f'bet_below_{bet_value}_2'

        #                 df.loc[_idx, column_above] = odd_above
        #                 df.loc[_idx, column_below] = odd_below

        # except Exception as e:
        #     logger.exception(f"Exception_5 occurred when filling match bets above and below for id: {id}; {url}. Error: {e}")

        if _idx % 50 == 0:  # Restartuj co 20 iteracji
            driver.quit()
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(2)
            
        df.to_csv(output_file_path)
        # defragmentation_iter += 1
        # if defragmentation_iter >= DEFRAGMENTATION_BATCH_SIZE:
        #     df = df.copy()
    
    
    time_end = time.time()
    logger.debug(f"Ended after: {time_end-time_start}")
    
    driver.quit()


