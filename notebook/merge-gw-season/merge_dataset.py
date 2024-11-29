import pandas as pd
pd.set_option('display.max_columns', None)

"""2016-17"""
url = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2016-17/gws/merged_gw.csv"
df_1617 = pd.read_csv(url, encoding='ISO-8859-1')

"""2017-18"""
url = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2017-18/gws/merged_gw.csv"
df_1718 = pd.read_csv(url, encoding='ISO-8859-1')

"""2018-19"""
url = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2018-19/gws/merged_gw.csv"
df_1819 = pd.read_csv(url, encoding='ISO-8859-1')

"""2019-20"""
url = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2019-20/gws/merged_gw.csv"
df_1920 = pd.read_csv(url)

"""2020-21"""
url = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2020-21/gws/merged_gw.csv"
df_2021 = pd.read_csv(url)

"""2021-22"""
url = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2021-22/gws/merged_gw.csv"
df_2122 = pd.read_csv(url)

"""2022-23"""
url = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2022-23/gws/merged_gw.csv"
df_2223 = pd.read_csv(url)

"""2023-24"""
url = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2023-24/gws/merged_gw.csv"
df_2324 = pd.read_csv(url)

"""2024-25"""
url = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2024-25/gws/merged_gw.csv"
df_2425 = pd.read_csv(url)


"""Combine & Formatting Features"""
new_features_list = ['xP', 'expected_assists', 'expected_goal_involvements', 'expected_goals', 'expected_goals_conceded']
df_list = [df_1617, df_1718, df_1819, df_1920]

for df in df_list:
    for feature in new_features_list:
        df[feature] = 0

df_list = [df_2021, df_2122]
new_features_list = ['expected_assists', 'expected_goal_involvements', 'expected_goals', 'expected_goals_conceded']

for df in df_list:
    for feature in new_features_list:
        df[feature] = 0

df_list = [df_1617, df_1718, df_1819, df_1920, df_2021, df_2122, df_2223, df_2324, df_2425]
season_list = ['16-17', '17-18', '18-19', '19-20', '20-21', '21-22', '22-23', '23-24', '24-25']

for df, season in zip(df_list, season_list):
    df['season'] = f'20{season}'

cols = ['season', 'element', 'assists', 'bonus', 'bps',
        'clean_sheets', 'creativity', 'fixture', 'goals_conceded',
        'goals_scored', 'ict_index', 'influence', 'xP', 'expected_assists',
        'expected_goal_involvements', 'expected_goals', 'expected_goals_conceded',
        'kickoff_time', 'minutes', 'opponent_team', 'own_goals', 'penalties_missed',
        'penalties_saved', 'red_cards', 'saves', 'selected', 'team_a_score',
        'team_h_score', 'threat', 'total_points', 'transfers_balance', 'transfers_in',
        'transfers_out', 'value', 'was_home', 'yellow_cards', 'GW']

df_1617 = df_1617[cols]
df_1718 = df_1718[cols]
df_1819 = df_1819[cols]
df_1920 = df_1920[cols]
df_2021 = df_2021[cols]
df_2122 = df_2122[cols]
df_2223 = df_2223[cols]
df_2324 = df_2324[cols]
df_2425 = df_2425[cols]

df = pd.concat([df_1617, df_1718, df_1819, df_1920, df_2021, df_2122, df_2223, df_2324, df_2425]).reset_index(drop=True)


"""Change Features Name"""
players_info = pd.read_csv(r'data/processed/players_raw_1617_2425.csv')

players_info = players_info[['season', 'id', 'web_name', 'first_name', 'second_name', 'element_type', 'team']]
players_info = players_info.rename(columns={'id': 'element', 'element_type':'position'})

"""Merge Dataset to add 'web_name' feature"""

df = pd.merge(df, players_info, on=['season', 'element'], how='left')
df['name'] = df['first_name'] + " " + df['second_name']
df = df.drop(['first_name', 'second_name'], axis=1)

cols = ['season', 'name', 'web_name', 'position', 'team', 'assists', 'bonus', 'bps',
        'clean_sheets', 'creativity', 'element', 'fixture', 'goals_conceded',
        'goals_scored', 'ict_index', 'influence', 'xP', 'expected_assists', 
        'expected_goal_involvements', 'expected_goals', 'expected_goals_conceded', 
        'kickoff_time', 'minutes', 'opponent_team', 'own_goals', 'penalties_missed', 
        'penalties_saved', 'red_cards', 'saves', 'selected', 'team_a_score',
        'team_h_score', 'threat', 'total_points', 'transfers_balance', 'transfers_in', 
        'transfers_out', 'value', 'was_home', 'yellow_cards', 'GW']

df = df[cols]

"""Mapping Team"""
url_teams = 'https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2024-25/teams.csv'
# FILE_PATH = os.path.join(MAIN_FOLDER, 'data/season/2024-25/teams.csv')
team_2425 = pd.read_csv(url_teams)
team_2425['season'] = '2024-25'
team_2425 = team_2425[['season', 'id', 'name']]
team_2425.rename(columns={
    'id':'team',
    'name':'team_name',
}, inplace=True)

# Membaca dataset dari URL
url_master_team = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/master_team_list.csv"
team_id = pd.read_csv(url_master_team)
team_id = pd.concat([team_id, team_2425]).reset_index(drop=True)

# Inisialisasi dictionary kosong untuk menyimpan peta tim per musim
team_maps = {}

# Daftar musim yang akan diproses
seasons = ['2016-17', '2017-18', '2018-19', '2019-20', '2020-21', '2021-22', '2022-23', '2023-24', '2024-25']

# Membuat mapping untuk setiap musim secara otomatis
for season in seasons:
    team_maps[season] = dict(zip(team_id[team_id['season'] == season]['team'], 
                                 team_id[team_id['season'] == season]['team_name']))

# Mengganti nilai 'opponent_team' berdasarkan musim
for season in seasons:
    df.loc[df['season'] == season, 'opponent_team'] = df.loc[df['season'] == season, 'opponent_team'].replace(team_maps[season])
    df.loc[df['season'] == season, 'team'] = df.loc[df['season'] == season, 'team'].replace(team_maps[season])
    
"""Formatting Team Name"""

team_map = {
    'Arsenal': 'Arsenal', 'Aston Villa': 'Aston Villa', 'Brentford': 'Brentford', 'Bournemouth': 'Bournemouth', 
    'Brighton': 'Brighton & Hove Albion', 'Burnley': 'Burnley', 'Chelsea': 'Chelsea', 'Crystal Palace': 'Crystal Palace', 
    'Everton': 'Everton', 'Leicester': 'Leicester City', 'Liverpool': 'Liverpool', 'Man City': 'Manchester City', 
    'Man Utd': 'Manchester United', 'Newcastle': 'Newcastle United', 'Tottenham': 'Tottenham Hotspur', 'Wolves': 'Wolverhampton Wanderers'
}

df['team'] = df['team'].replace(team_map)
df['opponent_team'] = df['opponent_team'].replace(team_map)

df = df.rename({
    'expected_assists':'xA',
    'expected_goal_involvements':'xGI',
    'expected_goals':'xG',
    'expected_goals_conceded':'xGC',
}, axis=1)

"""Handling Missing Values"""
df = df[~df['position'].isna()]

condition = (df['season'] == '2019-20') & (df['GW'] == 29) & (df['team'] == 'Manchester City')
df.loc[condition, ['team_h_score', 'team_a_score']] = [3, 0]

condition = (df['season'] == '2019-20') & (df['GW'] == 29) & (df['team'] == 'Arsenal')
df.loc[condition, ['team_h_score', 'team_a_score']] = [3, 0]

# df.loc

for wrong_gw, fixed_gw in zip(range(39, 48), range(30, 39)):
    df.loc[(df['season'] == '2019-20') & (df['GW'] == wrong_gw), 'GW'] = fixed_gw

df = df[df['team'] != df['opponent_team']]
df = df.reset_index(drop=True)

"""Cleaned Dataset"""
print("Dataset has been merged")
df.to_csv(r'data/processed/final-dataset.csv', index=False)