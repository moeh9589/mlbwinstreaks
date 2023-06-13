import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import os
import re
import ast


def retrieve_info_from_mlb_dot_com():
    driver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=driver_service)

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    url = "https://www.mlb.com/standings"
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "lxml")

    team_names = []
    win_streaks = []

    for i in range(5):
        # TEAMS IN FIRST PLACE
        trs = soup.find_all('tr', attrs={'data-index': f"{i}"})

        for tr in trs:
            span = tr.find('span', class_='team--name')

            if span:
                # Find the <a> tag within the <span> tag
                a_tag = span.find('a')

                if a_tag:
                    team_name = a_tag['data-team-name']
                    # Get the value of the <a> tag
                    team_names.append(team_name)
                    # print(team_name)
                else:
                    continue

            winstreak = tr.find('td', class_=f'col-7 row-{i} colgroup--end')
            if winstreak:
                value = winstreak.text
                win_streaks.append(value)
                # print(value)
            else:
                continue

    team_names_set = []
    [team_names_set.append(x) for x in team_names if x not in team_names_set]

    win_streaks = [ws.replace('\n', '') for ws in win_streaks]

    teams_and_win_streaks_dict = dict(zip(team_names_set, win_streaks))
    print(teams_and_win_streaks_dict)
    return teams_and_win_streaks_dict


def get_previous_win_streaks(filename):
    previous_win_streaks = {}

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            team, win_streak = line.split(':')
            previous_win_streaks[team] = win_streak

    return previous_win_streaks


def get_current_win_streaks(teams_dict):
    current_win_streaks = {}
    for team, win_streak in teams_dict.items():
        if win_streak == 'W3':
            current_win_streaks[team] = win_streak

    return current_win_streaks


def get_current_two_win_streaks(teams_dict):
    current_two_win_streaks = {}
    for team, win_streak in teams_dict.items():
        if win_streak == 'W2':
            current_two_win_streaks[team] = win_streak

    return current_two_win_streaks


def write_to_file(teams_dict):
    with open('win_streaks.txt', 'w') as file:
        for team, win_streak in teams_dict.items():
            if win_streak == 'W3':
                file.write(f'{team}: {win_streak}\n')


def get_times_won_on_three_streak(dict1, dict2):
    times = 0
    for team_name in dict1:
        if team_name in dict2:
            win_streak = dict2[team_name]
            if win_streak == 'W4':
                times += 1

    return times


def check_if_teams_lost_on_win_streak(dict1, dict2):
    times = 0
    for team_name in dict1:
        if team_name in dict2:
            win_streak = dict2[team_name]
            if win_streak == 'L1':
                times += 1

    return times


def write_win_and_loss_times_to_file(times_won, times_lost):
    old_times_won = 0
    old_times_lost = 0

    with open('calcfile.txt', 'r') as file:
        for line in file:
            line = line.strip()
            old_times_won, old_times_lost = line.split(':')

    new_times_won = int(old_times_won) + times_won
    new_times_lost = int(old_times_lost) + times_lost

    with open('calcfile.txt', 'w') as file:
        file.write(f'{new_times_won}:{new_times_lost}')


def get_times_won_and_lost_from_file():
    with open('calcfile.txt', 'r') as file:
        for line in file:
            line = line.strip()
            old_times_won, old_times_lost = line.split(':')

    return [old_times_won, old_times_lost]


def get_historical_betting_data(year):
    driver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=driver_service)
    # driver.implicitly_wait(10)

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    team_names = [
        'arizona-diamondbacks',
        'atlanta-braves',
        'baltimore-orioles',
        'boston-red-sox',
        'chicago-cubs',
        'chicago-white-sox',
        'cincinnati-reds',
        'cleveland-guardians',
        'colorado-rockies',
        'detroit-tigers',
        'houston-astros',
        'kansas-city-royals',
        'los-angeles-angels',
        'los-angeles-dodgers',
        'miami-marlins',
        'milwaukee-brewers',
        'minnesota-twins',
        'new-york-yankees',
        'new-york-mets',
        'oakland-athletics',
        'philadelphia-phillies',
        'pittsburgh-pirates',
        'san-diego-padres',
        'san-francisco-giants',
        'seattle-mariners',
        'st.-louis-cardinals',
        'tampa-bay-rays',
        'texas-rangers',
        'toronto-blue-jays',
        'washington-nationals'
    ]

    for i in range(len(team_names)):
        team_name = team_names[i]
        moneyline_odds = []

        print(team_name)
        url = f'https://www.covers.com/sport/baseball/mlb/teams/main/{team_name}/{year}'
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "lxml")

        div_element = soup.find('div', class_="col-xs-12")
        if div_element:
            regular_season_h2 = div_element.find('h2', string='Regular Season')
            if regular_season_h2:
                td_elements = regular_season_h2.find_next('table').find_all('td')
                counter = 0
                for td_element in td_elements:
                    moneyline_value = re.search(r'[+-]\d{3}', td_element.get_text())
                    if moneyline_value:
                        counter += 1
                        print(str(counter))
                        print("Moneyline Value:", moneyline_value.group())
                        moneyline_odds.insert(0, moneyline_value.group())
                    else:
                        continue

        else:
            print("div element with class 'col-xs-12' not found.")

        folder_name = f'{year}-MoneylineOdds-data'
        if not os.path.exists(folder_name):
            # Create the new folder
            os.makedirs(folder_name)
            print(f"Folder '{folder_name}' created successfully.")
        else:
            print(f"Folder '{folder_name}' already exists.")

        with open(f'{folder_name}/{team_names[i]}-{year}-moneylines.txt', 'w') as file:
            file.write(str(moneyline_odds))


def get_historical_data(year, strk):
    total_profit = 0
    stake = 100
    team_tickers = [
        'ARI', 'ATL', 'BAL', 'BOS', 'CHC', 'CHW', 'CIN', 'CLE', 'COL', 'DET', 'HOU', 'KCR', 'LAA',
        'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK', 'PHI', 'PIT', 'SDP', 'SFG', 'SEA', 'STL',
        'TBR', 'TEX', 'TOR', 'WSN'
]

    team_names = [
        'arizona-diamondbacks',
        'atlanta-braves',
        'baltimore-orioles',
        'boston-red-sox',
        'chicago-cubs',
        'chicago-white-sox',
        'cincinnati-reds',
        'cleveland-guardians',
        'colorado-rockies',
        'detroit-tigers',
        'houston-astros',
        'kansas-city-royals',
        'los-angeles-angels',
        'los-angeles-dodgers',
        'miami-marlins',
        'milwaukee-brewers',
        'minnesota-twins',
        'new-york-mets',
        'new-york-yankees',
        'oakland-athletics',
        'philadelphia-phillies',
        'pittsburgh-pirates',
        'san-diego-padres',
        'san-francisco-giants',
        'seattle-mariners',
        'st.-louis-cardinals',
        'tampa-bay-rays',
        'texas-rangers',
        'toronto-blue-jays',
        'washington-nationals'
    ]

    driver_service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=driver_service)
    # driver.implicitly_wait(10)

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')

    year_total = 0
    year_pct = 0
    year_lost_on_streak_total = 0
    num = 0
    # goes to baseball reference.com to find all win streak values for each team
    for ticker in team_tickers:
        team_name = team_names[num]
        num += 1
        times_lost_on_win_streak = 0
        times_won_on_win_streak = 0
        total = 0
        pct = 0

        url = f'https://www.baseball-reference.com/teams/{ticker}/{year}-schedule-scores.shtml'
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "lxml")

        team_dict = {"Team Name and Year": team_name, "Win streaks": [], f"Odds on W{strk}": [],
                     "Possible winnings with $100 bet": 0}

        tds = soup.find_all('td', {'data-stat': 'win_loss_streak'})
        for td in tds:
            csk_value = td.get('csk')
            team_dict["Win streaks"].append(csk_value)
            # print(csk_value, end=', ')

        for i in range(len(team_dict["Win streaks"]) - 1):

            if team_dict["Win streaks"][i] == strk and team_dict["Win streaks"][i+1] == "-1":
                year_total += 1
                year_lost_on_streak_total += 1
                total += 1
                times_lost_on_win_streak += 1
                team_dict["Possible winnings with $100 bet"] -= 100
                total_profit -= 100

            elif team_dict["Win streaks"][i] == strk and team_dict["Win streaks"][i+1] == str(int(strk) + 1):
                year_total += 1
                total += 1
                times_won_on_win_streak += 1

                # from the moneylines file: use indexed value to calculate a profit based on $100 stake
                with open(f'2022-MoneylineOdds-data/{team_name}-{year}-moneylines.txt', 'r') as file:
                    content = file.read()
                data_list = ast.literal_eval(content)
                odds = data_list[i+1]
                team_dict[f"Odds on W{strk}"].append(odds)
                if odds.startswith('+'):
                    odds_int = float(odds[1:])
                    profit = (float(stake) / 100) * odds_int
                    # profit = profit * 0.9

                elif odds.startswith('-'):
                    odds_int = float(odds[1:])
                    profit = (float(stake) / odds_int) * 100
                    # profit *= 0.9

                else:
                    continue
                    
                team_dict["Possible winnings with $100 bet"] += profit
                total_profit += profit

        print(times_lost_on_win_streak, " : ", total)

        if total > 0:
            pct = times_lost_on_win_streak / total * 100

        if year_total > 0:
            year_pct = year_lost_on_streak_total / year_total * 100

        team_dict[f"Percentage of losses on a {strk} win streak:"] = pct
        team_dict_str = str(team_dict)

        folder_name = f'{year}-W{strk}-data'
        if not os.path.exists(folder_name):
            # Create the new folder
            os.makedirs(folder_name)
            print(f"Folder '{folder_name}' created successfully.")
        else:
            print(f"Folder '{folder_name}' already exists.")

        with open(f'{folder_name}/{ticker}-{year}-W{strk}.txt', 'w') as file:
            file.write(team_dict_str)

        with open(f'{folder_name}/{year}-W{strk}data.txt', 'w') as file:
            file.write(str(year_pct))
            file.write('\n')
            file.write(str(total_profit))


def get_historical_data_for_l1_after_l1_after_w3(year):
    team_tickers = ['ATL', 'MIA', 'NYM', 'PHI', 'WSN', 'MIL', 'PIT', 'CIN', 'CHC', 'STL', 'LAD', 'ARI', 'SFG', 'SDP',
                    'COL', 'TBR', 'BAL', 'NYY', 'TOR', 'BOS', 'MIN', 'DET', 'CLE', 'CHW', 'KCR', 'TEX', 'HOU', 'LAA',
                    'SEA', 'OAK']
    year_total = 0
    year_pct = 0
    year_lost_after_l1_after_w3_total = 0
    year_won_after_l1_after_w3_total = 0

    driver = webdriver.Chrome(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')

    for ticker in team_tickers:
        times_lost_after_l1_after_w3 = 0
        times_won_after_l1_after_w3 = 0
        total = 0
        pct = 0
        strk = "3"
        url = f'https://www.baseball-reference.com/teams/{ticker}/{year}-schedule-scores.shtml'
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "lxml")

        team_dict = {}

        team_name = ""
        team_info = soup.find('h1')
        span_tags = team_info.find_all('span')
        for span in span_tags:
            team_name += span.get_text()
            team_name += " "

        team_dict["Team Name and Year"] = team_name
        team_dict["Win streaks"] = []

        tds = soup.find_all('td', {'data-stat': 'win_loss_streak'})
        for td in tds:
            csk_value = td.get('csk')
            team_dict["Win streaks"].append(csk_value)
            print(csk_value)

        for i in range(len(team_dict["Win streaks"]) - 2):

            if team_dict["Win streaks"][i] == strk and team_dict["Win streaks"][i+1] == "-1" \
                    and team_dict["Win streaks"][i+2] == "1":
                year_total += 1
                total += 1
                times_won_after_l1_after_w3 += 1
                year_won_after_l1_after_w3_total += 1

            elif team_dict["Win streaks"][i] == strk and team_dict["Win streaks"][i+2] == "-2":
                year_total += 1
                total += 1
                times_lost_after_l1_after_w3 += 1
                year_lost_after_l1_after_w3_total += 1

        print(times_lost_after_l1_after_w3, " : ", total)
        print(times_won_after_l1_after_w3, " : ", total)

        if total > 0:
            pct = times_lost_after_l1_after_w3 / total * 100

        if year_total > 0:
            year_pct = year_lost_after_l1_after_w3_total / year_total * 100

        team_dict[f"Percentage of losses after losing 1 after a 3 win streak:"] = pct
        team_dict_str = str(team_dict)

        folder_name = f'{year}-L1-after-L1-after-W3-data'
        if not os.path.exists(folder_name):
            # Create the new folder
            os.makedirs(folder_name)
            print(f"Folder '{folder_name}' created successfully.")
        else:
            print(f"Folder '{folder_name}' already exists.")

        # with open(f'{folder_name}/{ticker}-{year}-W{strk}.txt', 'w') as file:
        #     file.write(team_dict_str)

        with open(f'{folder_name}/{year}-L1-after-L1-after-W3-data.txt', 'w') as file:
            file.write(str(year_pct))

        print(year_total)


def get_hd_for_mult_years(year1, year2):

    for i in range(year1, year2):
        get_historical_data_for_l1_after_l1_after_w3(i)


def main():

    test_dict = {'Tampa Bay Rays': 'W1',
                 'Minnesota Twins': 'W2',
                 'Texas Rangers': 'L1',
                 'Atlanta Braves': 'W1',
                 'Milwaukee Brewers': 'L1',
                 'Arizona Diamondbacks': 'W5',
                 'Baltimore Orioles': 'L1',
                 'Detroit Tigers': 'W1',
                 'Houston Astros': 'W1',
                 'New York Mets': 'L1',
                 'Pittsburgh Pirates': 'W2',
                 'Los Angeles Dodgers': 'L1',
                 'New York Yankees': 'L1',
                 'Cleveland Guardians': 'L1',
                 'Seattle Mariners': 'W1',
                 'Miami Marlins': 'L1',
                 'Cincinnati Reds': 'L1',
                 'San Francisco Giants': 'L2',
                 'Toronto Blue Jays': 'W1',
                 'Chicago White Sox': 'L1',
                 'Los Angeles Angels': 'L1',
                 'Philadelphia Phillies': 'L4',
                 'St. Louis Cardinals': 'W1',
                 'San Diego Padres': 'W1',
                 'Boston Red Sox': 'W2',
                 'Kansas City Royals': 'L1',
                 'Oakland Athletics': 'L1',
                 'Washington Nationals': 'L1',
                 'Chicago Cubs': 'W4',
                 'Colorado Rockies': 'W4'}

    # retrieves the win streaks saved to the text file
    previous_win_streaks = get_previous_win_streaks('win_streaks.txt')
    print("Previous teams on a win streak: ")
    print(previous_win_streaks)
    print()

    # accesses mlb.com/standings and gets all teams with their current win streaks
    # teams_dict = test_dict
    teams_dict = retrieve_info_from_mlb_dot_com()
    write_to_file(teams_dict)

    # gets all teams with a 3 win streak from all teams
    current_win_streaks = get_current_win_streaks(teams_dict)
    print("Current teams on a 3 win streak: ")
    print(current_win_streaks)
    print()
    print("Current teams on a 2 win streak: ")
    print(get_current_two_win_streaks(teams_dict))
    print()

    # counts how many teams won and lost on their three streak
    times_lost_on_three_streak = check_if_teams_lost_on_win_streak(previous_win_streaks, teams_dict)
    times_won_on_three_streak = get_times_won_on_three_streak(previous_win_streaks, teams_dict)

    print("Times won on a three streak: " + str(times_won_on_three_streak))
    print("Times lost on a three streak: " + str(times_lost_on_three_streak))
    print()

    write_win_and_loss_times_to_file(times_won_on_three_streak, times_lost_on_three_streak)

    total_times_won = get_times_won_and_lost_from_file()[0]
    total_times_lost = get_times_won_and_lost_from_file()[1]

    total = int(total_times_won) + int(total_times_lost)
    print(total)
    pct_won = int(total_times_won) / int(total) * 100
    pct_lost = int(total_times_lost) / int(total) * 100
    print("Total times won on a three streak: " + str(total_times_won))
    print("Total times lost on a three streak: " + str(total_times_lost))

    print(f'Percentage of teams to lose after a three win streak: {pct_lost}%'
          f' : {total_times_lost} / {total}')

    print()
    print()

    year = 2021

    # for i in range(year, 2023):
    #     get_historical_data(str(i), "2")
    # get_historical_data("2022", "3")
    # get_historical_data_for_l1_after_l1_after_w3(2022)
    # get_hd_for_mult_years(2013, 2023)
    # get_historical_betting_data("2022")


main()

