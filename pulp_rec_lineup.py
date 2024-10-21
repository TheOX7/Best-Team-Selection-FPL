import pulp

def pulp_model(df):
    
    # Definisikan masalah optimisasi (tujuan: memaksimalkan total points)
    problem = pulp.LpProblem("Best_Starting_Eleven", pulp.LpMaximize)

    # Definisikan variabel keputusan (binary) untuk setiap pemain
    player_vars = pulp.LpVariable.dicts("Players", df.index, cat='Binary')

    # Fungsi objektif: Maksimalkan prediksi total points
    problem += pulp.lpSum([player_vars[i] * df.loc[i, 'xTotPoints'] for i in df.index]), "Total_Points"

    # Constraint 1: Total 15 pemain (termasuk starting lineup + cadangan)
    problem += pulp.lpSum([player_vars[i] for i in df.index]) == 15, "Total_15_Players"

    # Constraint 2: Kondisi pemain >= 0.75
    problem += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'condition'] >= 0.75]) == 15, "Condition_Above_0.75"

    # Constraint 3: Maksimal 3 pemain dari satu tim
    for team in df['team'].unique():
        problem += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'team'] == team]) <= 3, f"Max_3_Players_from_{team}"

    # Constraint 5: Batas maksimal jumlah pemain per posisi
    problem += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'position'] == 'DEF']) == 5, "Max_5_DEF"
    problem += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'position'] == 'MID']) == 5, "Max_5_MID"
    problem += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'position'] == 'FWD']) == 3, "Max_3_FWD"
    problem += pulp.lpSum([player_vars[i] for i in df.index if df.loc[i, 'position'] == 'GK']) == 2, "Max_2_GK"

    # Constraint 6: Batas harga total pemain <= 100
    problem += pulp.lpSum([player_vars[i] * df.loc[i, 'price'] for i in df.index]) <= 100, "Total_Price_Limit"

    # Solve the optimization problem
    problem.solve()

    # Ekstrak pemain yang terpilih
    selected_players = df.loc[[i for i in df.index if player_vars[i].varValue == 1]]

    # Definisikan urutan posisi untuk tampilan
    position_order = {'GK': 1, 'DEF': 2, 'MID': 3, 'FWD': 4}
    selected_players['position_order'] = selected_players['position'].map(position_order)

    # Urutkan pemain berdasarkan posisi dan hapus kolom bantuan
    selected_players = selected_players.sort_values(by='position_order').drop(columns='position_order')

    return selected_players
