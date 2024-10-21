import os
import pandas as pd

def combine_dataset(folder_path, position):
    all_data = []
    
    for file in os.listdir(folder_path):
        if file.endswith('.xlsx'):
            file_path = os.path.join(folder_path, file)
            df = pd.read_excel(file_path, header=None)
            df.columns = ['name', 'team', 'price', 'condition']
            
            def update_condition(value):
                if '25% chance of playing' in value: return 0.25
                elif '50% chance of playing' in value: return 0.5
                elif '75% chance of playing' in value: return 0.75
                elif 'Unlikely to play' in value: return 0
                else: return 1
            
            df['condition'] = df['condition'].apply(update_condition)
            all_data.append(df)

    df_combined = pd.concat(all_data, ignore_index=True)
    df_combined['position'] = position
    return df_combined

def process_fpl_data(gw_no):
    MAIN_FOLDER = r"D:\GitHub\TheOX7\Best-Team-Selection-FPL"
    positions = ['gk', 'def', 'mid', 'fwd']
    all_dfs = []

    for pos in positions:
        folder_path = os.path.join(MAIN_FOLDER, f'data/fpl/gw-{gw_no}/{pos}')
        df_pos = combine_dataset(folder_path, pos.upper())
        all_dfs.append(df_pos)

    df_combined = pd.concat(all_dfs).reset_index(drop=True)

    team_map = {
        'ARS':'Arsenal', 'AVL':'Aston Villa', 'BHA':'Brighton & Hove Albion', 'BOU':'Bournemouth',
        'BRE':'Brentford', 'CHE':'Chelsea', 'CRY':'Crystal Palace', 'EVE':'Everton', 'FUL':'Fulham',
        'IPS':'Ipswich Town', 'LEI':'Leicester City', 'LIV':'Liverpool', 'MCI':'Manchester City',
        'MUN':'Manchester United', 'NEW':'Newcastle United', 'NFO':'Nottingham Forest', 'SOU':'Southampton',
        'TOT':'Tottenham Hotspur', 'WHU':'West Ham United', 'WOL':'Wolverhampton Wanderers'
    }

    df_combined['team'] = df_combined['team'].replace(team_map)
    df_combined['GW'] = gw_no

    # Save the combined data to CSV
    output_path = os.path.join(MAIN_FOLDER, f'data/fpl/price/fpl-price-gw-{gw_no}.csv')
    df_combined.to_csv(output_path, index=False)

    # Combine all gameweek CSVs into one
    combine_all_gws(MAIN_FOLDER)

def combine_all_gws(MAIN_FOLDER):
    FOLDER_PATH = os.path.join(MAIN_FOLDER, 'data/fpl/price')
    csv_files = [file for file in os.listdir(FOLDER_PATH) if file.endswith('.csv')]

    combined_dfs = [pd.read_csv(os.path.join(FOLDER_PATH, file)) for file in csv_files]
    combined_fpl_price_df = pd.concat(combined_dfs, ignore_index=True)

    combined_path = os.path.join(MAIN_FOLDER, 'data/fpl/combined-fpl-price.csv')
    combined_fpl_price_df.to_csv(combined_path, index=False)

    # Process fixtures merging
    process_fixtures(combined_fpl_price_df, MAIN_FOLDER)

def process_fixtures(combined_fpl_price_df, MAIN_FOLDER):
    fixtures_path = os.path.join(MAIN_FOLDER, 'data/fixtures/fixtures-2024-25.csv')
    fixtures_2425 = pd.read_csv(fixtures_path)
    
    merged_data = []
    for gw in combined_fpl_price_df['GW'].unique():
        gw_fixtures = fixtures_2425[fixtures_2425['GW'] == gw]

        merge_away = pd.merge(
            combined_fpl_price_df[combined_fpl_price_df['GW'] == gw], 
            gw_fixtures, 
            left_on=['team', 'GW'], right_on=['away_team', 'GW']
        )
        merge_away['opponent_team'] = merge_away['home_team']
        merge_away['was_home'] = 0
        merge_away.drop(columns=['away_team', 'home_team'], inplace=True)

        merge_home = pd.merge(
            combined_fpl_price_df[combined_fpl_price_df['GW'] == gw], 
            gw_fixtures, 
            left_on=['team', 'GW'], right_on=['home_team', 'GW']
        )
        merge_home['opponent_team'] = merge_home['away_team']
        merge_home['was_home'] = 1
        merge_home.drop(columns=['away_team', 'home_team'], inplace=True)

        merged_data.append(pd.concat([merge_away, merge_home], ignore_index=True))

    fpl_price_df = pd.concat(merged_data, ignore_index=True)
    output_path = os.path.join(MAIN_FOLDER, 'data/fpl/combined-fpl-price.csv')
    fpl_price_df.to_csv(output_path, index=False)

# Input gameweek number
gw_no = int(input("Input Gameweek: "))
process_fpl_data(gw_no)
