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
    positions = ['gk', 'def', 'mid', 'fwd']
    all_dfs = []

    for pos in positions:
        df_pos = combine_dataset(rf'data/fpl/gw-{gw_no}/{pos}', pos.upper())
        all_dfs.append(df_pos)

    df_combined = pd.concat(all_dfs).reset_index(drop=True)

    team_map = {
        'ARS':'Arsenal', 'AVL':'Aston Villa', 'BHA':'Brighton & Hove Albion', 
        'BOU':'Bournemouth', 'BRE':'Brentford', 'CHE':'Chelsea', 'CRY':'Crystal Palace', 
        'EVE':'Everton', 'FUL':'Fulham', 'IPS':'Ipswich Town', 'LEI':'Leicester City', 
        'LIV':'Liverpool', 'MCI':'Manchester City', 'MUN':'Manchester United', 
        'NEW':'Newcastle United', 'NFO':'Nottingham Forest', 'SOU':'Southampton',
        'TOT':'Tottenham Hotspur', 'WHU':'West Ham United', 'WOL':'Wolverhampton Wanderers'
    }

    df_combined['team'] = df_combined['team'].replace(team_map)
    df_combined['GW'] = gw_no

    # Save the combined data to CSV
    df_combined.to_csv(rf'data/fpl/price/fpl-price-gw-{gw_no}.csv', index=False)

    # Finalize data by combining all gameweek data and processing fixtures
    finalize_combined_data()

def finalize_combined_data():
    FOLDER_PATH = r'data/fpl/price'
    csv_files = [file for file in os.listdir(FOLDER_PATH) if file.endswith('.csv')]

    # Load and concatenate all gameweek data
    combined_dfs = [pd.read_csv(os.path.join(FOLDER_PATH, file)) for file in csv_files]
    combined_fpl_price_df = pd.concat(combined_dfs, ignore_index=True)

    # Save the combined data to a single CSV
    combined_fpl_price_df.to_csv(r'data/fpl/combined-fpl-price.csv', index=False)

    # Process and merge with fixtures data
    process_fixtures(combined_fpl_price_df)

def process_fixtures(combined_fpl_price_df):
    fixtures_2425 = pd.read_csv(r'data/fixtures/fixtures-2024-25.csv')
    
    merged_data = []
    for gw in combined_fpl_price_df['GW'].unique():
        gw_fixtures = fixtures_2425[fixtures_2425['GW'] == gw]

        # Merge as away team
        merge_away = pd.merge(
            combined_fpl_price_df[combined_fpl_price_df['GW'] == gw], 
            gw_fixtures, 
            left_on=['team', 'GW'], right_on=['away_team', 'GW']
        )
        merge_away['opponent_team'] = merge_away['home_team']
        merge_away['was_home'] = 0
        merge_away.drop(columns=['away_team', 'home_team'], inplace=True)

        # Merge as home team
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
    fpl_price_df.to_csv(r'data/fpl/combined-fpl-price.csv', index=False)

# Input gameweek number
gw_no = int(input("Input Gameweek: "))
process_fpl_data(gw_no)
print("All datasets have been merged")
