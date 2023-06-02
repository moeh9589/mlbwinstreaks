import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def retrieve_info_from_mlb_dot_com():
    driver = webdriver.Chrome(ChromeDriverManager().install())

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
    print("Total times won on a three streak: " + str(total_times_won))
    print("Total times lost on a three streak: " + str(total_times_lost))

    print(f'Percentage of teams to win after a three win streak: {pct_won}')


main()

