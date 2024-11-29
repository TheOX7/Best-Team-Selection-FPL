import pulp
import pandas as pd
import json
import joblib
import warnings
import os
pd.set_option('display.max_columns', None)
warnings.filterwarnings("ignore")

GW = int(input("Input Gameweek to Predict: "))

def fpl_selection(gw=GW, positions=['DEF', 'MID', 'FWD', 'GK']):
    all_positions_df = []  # List untuk menyimpan dataframe dari setiap posisi
    
    # Loop melalui semua posisi
    for position in positions:
        
        # Load dataset untuk GW tertentu
        df = pd.read_csv(rf'data/fpl/gw-{gw}/{position}_updated_features.csv')

        # Fungsi manual untuk scaling Min-Max
        def manual_min_max_scaling(value, min_val, max_val):
            return (value - min_val) / (max_val - min_val)

        # Load nilai min dan max dari JSON untuk scaling
        with open(rf'data/json/{position}/min_max_values.json', 'r') as json_file:
            min_max_dict = json.load(json_file)

        # Terapkan scaling untuk setiap kolom yang ada di min_max_dict
        for column, values in min_max_dict.items():
            min_val = values['min']
            max_val = values['max']
            df[column] = df[column].apply(lambda x: manual_min_max_scaling(x, min_val, max_val))

        # Simpan data kolom yang ingin dipertahankan
        df_ = pd.DataFrame()
        df_['total_points'] = df['total_points']
        df_['web_name'] = df['web_name']
        df_['element'] = df['element']

        # Hapus kolom yang tidak diperlukan
        df.drop(['total_points', 'web_name', 'kickoff_time', 'element'], axis=1, inplace=True)

        # Load dictionary untuk mapping data yang di-encode
        with open(rf'data/json/{position}/encoded_player_names.json', 'r') as json_file:
            player_dict = json.load(json_file)

        with open(rf'data/json/{position}/encoded_position.json', 'r') as json_file:
            position_dict = json.load(json_file)

        with open(rf'data/json/{position}/encoded_team_name.json', 'r') as json_file:
            team_dict = json.load(json_file)

        # Map data yang di-encode
        df['name'] = df['name'].map(player_dict)
        df['position'] = df['position'].map(position_dict)
        df['team'] = df['team'].map(team_dict)
        df['opponent_team'] = df['opponent_team'].map(team_dict)

        # Load model machine learning (Random Forest atau model lain yang sudah dilatih)
        model = joblib.load(rf'model/model_{position}.joblib')

        # Prediksi total points menggunakan model
        df['xTotPoints'] = model.predict(df)

        # Fungsi untuk inverse scaling
        def inverse_min_max_scaling(scaled_value, min_val, max_val):
            return (scaled_value * (max_val - min_val)) + min_val

        # Inverse scaling untuk setiap kolom kecuali 'total_points'
        columns_to_inverse = [col for col in min_max_dict.keys() if col != 'total_points']
        for column in columns_to_inverse:
            min_val = min_max_dict[column]['min']
            max_val = min_max_dict[column]['max']
            df[column] = df[column].apply(lambda x: inverse_min_max_scaling(x, min_val, max_val))

        # Inverse scaling untuk 'total_points'
        min_val = min_max_dict['total_points']['min']
        max_val = min_max_dict['total_points']['max']
        df_['total_points'] = df_['total_points'].apply(lambda x: inverse_min_max_scaling(x, min_val=min_val, max_val=max_val))

        # Inverse scaling untuk predicted total points (xTotPoints)
        df['xTotPoints'] = df['xTotPoints'].apply(lambda x: inverse_min_max_scaling(x, min_val, max_val))
        df['xTotPoints'] = round(df['xTotPoints'], 2)

        # Reverse mapping data untuk kolom name, position, dan team
        inverse_player_dict = {v: k for k, v in player_dict.items()}
        inverse_position_dict = {v: k for k, v in position_dict.items()}
        inverse_team_dict = {v: k for k, v in team_dict.items()}

        df['name'] = df['name'].map(inverse_player_dict)
        df['position'] = df['position'].map(inverse_position_dict)
        df['team'] = df['team'].map(inverse_team_dict)
        df['opponent_team'] = df['opponent_team'].map(inverse_team_dict)

        # Load data harga pemain untuk GW tertentu
        fpl_price_df_gw = pd.read_csv(rf'data/fpl/price/fpl-price-gw-{gw}.csv')
        fpl_price_df_gw.rename({'name': 'web_name'}, axis=1, inplace=True)

        # Gabungkan data dengan harga pemain
        pulp_df = df
        pulp_df['avg_h2h_last_5_points'] = df_['total_points']
        pulp_df['web_name'] = df_['web_name']
        pulp_df['element'] = df_['element']
        pulp_df = pulp_df.merge(fpl_price_df_gw, on=['web_name', 'position', 'team'], how='left')

        # Tambahkan dataframe hasil ke list
        all_positions_df.append(pulp_df)

    # Gabungkan semua dataframe dari berbagai posisi
    final_df = pd.concat(all_positions_df, ignore_index=True)
    final_df = final_df[~final_df['GW'].isna()].reset_index(drop=True)
    final_df = final_df[['name', 'element', 'position', 'team', 'opponent_team', 'condition', 'price', 'xTotPoints']]
            
    return final_df

def pulp_model(df):
    # Definisikan masalah optimisasi (tujuan: memaksimalkan total points)
    problem = pulp.LpProblem("Best_Starting_Eleven", pulp.LpMaximize)

    # Definisikan variabel keputusan (binary) untuk setiap pemain
    player_vars = pulp.LpVariable.dicts("Players", df.index, cat='Binary')

    # Fungsi objektif: Maksimalkan prediksi total points
    problem += pulp.lpSum([player_vars[i] * df.loc[i, 'xTotPoints'] for i in df.index]), "Total_Points"

    # Constraint 1: Total 15 pemain
    problem += pulp.lpSum([player_vars[i] for i in df.index]) == 15, "Total_15_Players"

    # Constraint 2: Kondisi pemain >= 0.75
    problem += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'condition'] >= 0.75]) == 15, "Condition_Above_0.75"

    # Constraint 3: Maksimal 3 pemain dari satu tim
    for team in df['team'].unique():
        problem += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'team'] == team]) <= 3, f"Max_3_Players_from_{team}"

    # Constraint 4: Minimal 3 pemain dari posisi DEF, MID, dan FWD
    for position in ['DEF', 'MID', 'FWD']:
        problem += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'position'] == position]) >= 3, f"Min_3_{position}"

    # Constraint 5: Tepat 2 pemain GK (Goalkeeper)
    problem += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'position'] == 'GK']) == 2, "Exactly_2_GK"

    # # Constraint 6: Batas harga total pemain <= 100
    problem += pulp.lpSum([player_vars[i] * df.loc[i, 'price'] for i in df.index]) <= 100, "Total_Price_Limit"

    # Solve the optimization problem
    problem.solve()

    # Ekstrak pemain yang terpilih
    selected_players = df.loc[[i for i in df.index if player_vars[i].varValue == 1]]

    # Definisikan urutan posisi untuk tampilan
    position_order = {'GK': 1, 'DEF': 2, 'MID': 3, 'FWD': 4}
    selected_players['position_order'] = selected_players['position'].map(position_order)

    # Urutkan pemain berdasarkan posisi dan hapus kolom bantuan
    sorted_players = selected_players.sort_values(by='position_order').drop(columns='position_order')

    return sorted_players

def rec_lineup(gw):
    pulp_df = fpl_selection(gw)
    pulp_df = pulp_df.dropna().reset_index(drop=True)

    df = pulp_model(df=pulp_df)
    df = df.reset_index(drop=True)

    url = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data/2024-25/gws/merged_gw.csv"
    df_2425 = pd.read_csv(url)

    if not df_2425[df_2425['GW'].isin([gw])].empty:
        df_2425 = df_2425[df_2425['GW'] == gw]
        df = df.merge(df_2425[['element', 'total_points']], on='element')
        pulp_df = pulp_df.merge(df_2425[['element', 'total_points']], on='element')

        df = df[['name', 'position', 'element', 'team', 'opponent_team', 'price', 'condition', 'xTotPoints','total_points']]
        pulp_df = pulp_df[['name', 'position', 'element', 'team', 'opponent_team', 'price', 'condition', 'xTotPoints','total_points']]
        
    elif df_2425[df_2425['GW'].isin([gw])].empty:
        df = df[['name', 'position', 'element', 'team', 'opponent_team', 'price', 'condition', 'xTotPoints']]
        pulp_df = pulp_df[['name', 'position', 'element', 'team', 'opponent_team', 'price', 'condition', 'xTotPoints']]

    df.to_csv(rf'data/pulp/gw-{gw}/per-position/rec_lineup.csv', index=False)
    pulp_df.to_csv(rf'data/pulp/gw-{gw}/per-position/not_rec_lineup.csv', index=False)

rec_lineup(gw=GW)

print("RUN SUCCESSFULLY")