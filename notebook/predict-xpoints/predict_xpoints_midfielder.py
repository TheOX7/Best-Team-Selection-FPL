import os
import pandas as pd
import warnings
import json
import joblib
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

warnings.filterwarnings('ignore')

"""#### Load Dataset"""

GW_TO_PRED = int(input("Input Gameweek to Predict: "))
GW_BEFORE = GW_TO_PRED-1
CURRENT_GW = int(input("Input Current Gameweek: "))

position_ = 'MID'
position = position_.lower()

# Main folder
MAIN_FOLDER = r"D:\GitHub\TheOX7\Best-Team-Selection-FPL"

# Relative path to your CSV file
FILE_PATH = os.path.join(MAIN_FOLDER, 'data/processed/final-dataset.csv')
df = pd.read_csv(FILE_PATH)

# Kondisi khusus GW_TO_PRED = 1
if GW_TO_PRED == 1:
    GW_TO_PRED = 2
    SAVE_GW_DATA = 1
    GW_BEFORE = 1
else:
    GW_BEFORE = GW_TO_PRED - 1
    SAVE_GW_DATA = GW_TO_PRED

print(f" -- Dataset Loaded -- \n")

# df = df[~df['season'].isin(['2016-17', '2017-18', '2018-19', '2020-21', '2021-22'])]
df = df[~((df['season'] == '2024-25') & (df['GW'].between(GW_TO_PRED, CURRENT_GW)))]
df = df[df['position'] == position_].reset_index(drop=True)
df = df.sort_values(by=['season', 'GW']).reset_index(drop=True)

"""#### Feature Engineering

##### Add Row Dataset for GW to Predict
"""
# File Path
FILE_PATH = os.path.join(MAIN_FOLDER, 'data/fixtures/fixtures-2024-25.csv')
fixtures_2425_df = pd.read_csv(FILE_PATH)

# Filter data untuk season 2024/25 dan GW == GW_BEFORE (GW 5)
gw_before_df = df[(df['season'] == '2024-25') & (df['GW'] == GW_BEFORE)].copy()

# Tidak mengubah nilai fitur menjadi nol kali ini.
# Ubah nilai GW menjadi GW_TO_PRED (GW 6)
gw_before_df['GW'] = GW_TO_PRED

# Tambahkan data fixtures untuk GW == GW_TO_PRED
fixtures_gw_to_pred = fixtures_2425_df[fixtures_2425_df['GW'] == GW_TO_PRED]

# Fungsi untuk mengubah was_home dan opponent_team berdasarkan fixtures
def update_team_info(row, fixtures):
    team = row['team']

    # Cek jika team ada di home_team atau away_team di fixtures GW GW_TO_PRED
    home_match = fixtures[fixtures['home_team'] == team]
    away_match = fixtures[fixtures['away_team'] == team]

    if not home_match.empty:
        row['was_home'] = True
        row['opponent_team'] = home_match['away_team'].values[0]
    elif not away_match.empty:
        row['was_home'] = False
        row['opponent_team'] = away_match['home_team'].values[0]

    return row

# Terapkan fungsi update ke data GW == GW_TO_PRED
gw_to_pred_df = gw_before_df.apply(update_team_info, axis=1, fixtures=fixtures_gw_to_pred)

# Tambahkan data GW == GW_TO_PRED ke df
df = pd.concat([df, gw_to_pred_df], ignore_index=True)
df = df.reset_index(drop=True)

"""##### Create New Features

Calculate Team Points
"""

def calculate_points(row):
    if row['was_home'] == 1:
        # Tim bermain kandang
        if row['team_a_score'] < row['team_h_score']:
            return 3  # Menang kandang
        elif row['team_a_score'] > row['team_h_score']:
            return 0  # Kalah kandang
        else:
            return 1  # Imbang
    else:
        # Tim bermain tandang
        if row['team_a_score'] > row['team_h_score']:
            return 3  # Menang tandang
        elif row['team_a_score'] < row['team_h_score']:
            return 0  # Kalah tandang
        else:
            return 1  # Imbang

df['team_points'] = df.apply(calculate_points, axis=1)

"""Set numeric features values to 0 for GW that will be predict"""

# Kolom numerik selain 'value' dan 'GW'
numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.difference(['value', 'GW', 'element', 'fixture'])

# Mengisi kolom numerik dengan 0 untuk baris dengan GW_TO_PRED di season 2024-25
df.loc[((df['GW'] == GW_TO_PRED) & (df['season'] == '2024-25')), numeric_cols] = 0

"""Set 'numeric_cols' values by Average Last 5 GW for GW that will be predicted"""

# Menghitung rata-rata 5 GW sebelumnya untuk tiap fitur numerik
def calculate_last_5_average(row, df, numeric_cols):
    # Dapatkan season dari baris yang akan diprediksi
    current_season = row['season']
    current_gw = row['GW']

    # Filter data berdasarkan pemain yang sama, dari season saat ini dan season sebelumnya
    relevant_games = df[(df['name'] == row['name']) &
                        ((df['season'] == current_season) |
                         (df['season'] == previous_season(current_season)))]

    # Ambil hanya GW yang lebih kecil dari GW yang akan diprediksi
    relevant_games = relevant_games[relevant_games['GW'] < current_gw].tail(5)

    # Hitung rata-rata dari fitur numerik
    avg_values = relevant_games[numeric_cols].mean()

    # Isi nilai rata-rata pada baris yang diprediksi
    for col in numeric_cols:
        row[col] = avg_values[col] if not pd.isna(avg_values[col]) else 0

    return row

# Fungsi untuk mendapatkan season sebelumnya
def previous_season(current_season):
    season_start, season_end = current_season.split('-')
    previous_season_start = str(int(season_start) - 1)
    previous_season_end = str(int(season_end) - 1)
    return f"{previous_season_start}-{previous_season_end}"

# Terapkan fungsi untuk menghitung rata-rata 5 GW sebelumnya dan langsung update dataframe asli menggunakan .loc
df.loc[(df['GW'] == GW_TO_PRED) & (df['season'] == '2024-25'), :] = df.loc[(df['GW'] == GW_TO_PRED) & (df['season'] == '2024-25')].apply(
    lambda row: calculate_last_5_average(row, df, numeric_cols), axis=1
)

"""Calculate Team Last 5 Total Points Against Specific Team & No Specific Team"""

# Last 5 total_points melawan opponent_team
def team_last_5_total_points_vs_specific_opponent(df):
    # Grouping by 'team' and 'opponent_team', then applying a rolling window for the last 5 gameweeks
    df['team_last_5_points_h2h'] = df.groupby(['team', 'opponent_team'])['team_points']\
        .rolling(window=5, min_periods=1).sum().reset_index(level=[0, 1], drop=True)

    # Fill missing values with 0 in case a team hasn't played 5 games against the opponent
    df['team_last_5_points_h2h'] = df['team_last_5_points_h2h'].fillna(0).astype(int)

    return df

# Last 5 total_points melawan semua tim (tanpa filter opponent_team)
def team_last_5_total_points_vs_all_teams(df):
    # Grouping by 'team' only and applying a rolling window for the last 5 gameweeks
    df['team_last_5_points_vs_all'] = df.groupby(['team'])['team_points']\
        .rolling(window=5, min_periods=1).sum().reset_index(level=0, drop=True)

    # Fill missing values with 0 for cases with fewer than 5 matches
    df['team_last_5_points_vs_all'] = df['team_last_5_points_vs_all'].fillna(0).astype(int)

    return df

# Apply the function to calculate last 5 total_points vs specific opponent
df = team_last_5_total_points_vs_specific_opponent(df)

# Apply the function to calculate last 5 total_points vs all teams
df = team_last_5_total_points_vs_all_teams(df)

def display_team_points_vs_opponent(df, team, opponent_team):
    # Filter dataframe dimana 'team' sebagai team atau opponent_team, dan lawannya adalah opponent_team atau team
    filtered_df = df[((df['team'] == team) & (df['opponent_team'] == opponent_team)) |
                     ((df['team'] == opponent_team) & (df['opponent_team'] == team))]

    # Pilih kolom yang relevan untuk ditampilkan
    columns_to_display = ['name', 'GW', 'season', 'team', 'opponent_team', 'was_home', 'team_points', 'team_last_5_points_h2h']

    # Tampilkan dataframe yang difilter
    filtered_df = filtered_df[columns_to_display].drop_duplicates().sort_values(by=['season', 'GW'])
    return filtered_df

"""Calculate Players Last 5 Features Against Specific Teams & No Specific Teams"""

sum_cols = ['assists', 'bonus', 'bps', 'clean_sheets', 'goals_conceded', 'goals_scored', 'own_goals', 'penalties_missed',
            'penalties_saved', 'red_cards', 'yellow_cards', 'saves', 'total_points', 'team_points']

avg_cols = ['ict_index', 'influence', 'creativity', 'threat', 'selected', 'minutes']

def players_last_5_feature_vs_every_team(df, agg_type, column_name):
    if agg_type == 'sum':
        df[f'tot_{column_name}_last_5'] = df.groupby(['name'])[column_name]\
            .rolling(window=5, min_periods=1).sum().reset_index(level=0, drop=True)
        df[f'tot_{column_name}_last_5'] = df[f'tot_{column_name}_last_5'].fillna(0).astype(int)

    elif agg_type == 'avg':
        df[f'avg_{column_name}_last_5'] = df.groupby(['name'])[column_name]\
            .rolling(window=5, min_periods=1).mean().reset_index(level=0, drop=True)
        df[f'avg_{column_name}_last_5'] = round(df[f'avg_{column_name}_last_5'].fillna(0).astype(float))

    return df

def players_last_5_feature_vs_specific_team(df, agg_type, column_name):
    if agg_type == 'sum':
        df[f'tot_{column_name}_last_5_h2h'] = df.groupby(['name', 'opponent_team'])[column_name].\
            rolling(window=5, min_periods=1).sum().reset_index(level=[0, 1], drop=True)
        df[f'tot_{column_name}_last_5_h2h'] = df[f'tot_{column_name}_last_5_h2h'].fillna(0).astype(int)

    elif agg_type == 'avg':
        df[f'avg_{column_name}_last_5_h2h'] = df.groupby(['name', 'opponent_team'])[column_name].\
            rolling(window=5, min_periods=1).mean().reset_index(level=[0, 1], drop=True)
        df[f'avg_{column_name}_last_5_h2h'] = round(df[f'avg_{column_name}_last_5_h2h'].fillna(0).astype(float))

    return df

print(" -- Feature Engineering (Start) -- ")
for col in sum_cols:
    df = players_last_5_feature_vs_specific_team(df, 'sum', col)
    df = players_last_5_feature_vs_every_team(df, 'sum', col)

for col in avg_cols:
    df = players_last_5_feature_vs_specific_team(df, 'avg', col)
    df = players_last_5_feature_vs_every_team(df, 'avg', col)
print(f" -- Feature Engineering (Success) -- \n")


"""### Save GW Predict Dataset"""

def save_gw_data(df, gw=SAVE_GW_DATA):
    df = df[(df['season'] == '2024-25') & (df['GW'] == gw)]
    df = df.drop(['season', 'GW'], axis=1)
    FILE_PATH = os.path.join(MAIN_FOLDER, f'data/fpl/gw-{gw}/{position}_updated_features.csv')
    df.reset_index(drop=True).to_csv(FILE_PATH, index=False)

"""Feature Selection"""
other_cols = ['fixture', 'transfers_balance', 'transfers_in', 'transfers_out',
              'team_a_score', 'team_h_score', 'minutes', 'xP', 'xA', 'xGI', 'xG', 'xGC']

feat_selection = ['tot_penalties_saved_last_5_h2h', 'tot_penalties_saved_last_5', 'tot_saves_last_5_h2h', 'tot_saves_last_5']

drop_cols = sum_cols + avg_cols + other_cols + feat_selection
drop_cols = [col for col in drop_cols if col not in ['total_points']] ## 'total_points' not included, cause this feature will be used for target model

df = df.drop(columns=(drop_cols))
save_gw_data(df)
print(f" -- Dataset Saved -- \n")

"""### Scaling Dataset"""

print(" -- Numerical Features Scaling (Start) -- ")
df = df.drop(['season', 'GW', 'kickoff_time', 'web_name', 'element'], axis=1)
cols = df.select_dtypes(exclude=['object']).columns.tolist()

min_max_dict = {}
for col in cols:
    min_max_dict[col] = {
        "min": float(df[col].min()),
        "max": float(df[col].max())
    }

FILE_PATH = os.path.join(MAIN_FOLDER, f'data/json/{position}/min_max_values.json')

# Simpan dictionary sebagai JSON file
with open(FILE_PATH, 'w') as json_file:
    json.dump(min_max_dict, json_file, indent=2)

cols = df.select_dtypes(exclude=['object']).columns.tolist()
cols = [col for col in cols if col not in ['was_home', 'GW']]

scaler = MinMaxScaler()
df[cols] = scaler.fit_transform(df[cols])

print(f" -- Numerical Features Scaling (Success) -- \n")

"""### Encoding"""
print(" -- Label Encoding (Start) -- ")
le_name = LabelEncoder()
le_position = LabelEncoder()
le_team = LabelEncoder()

df['name'] = le_name.fit_transform(df['name'])
df['position'] = le_position.fit_transform(df['position'])
df['team'] = le_team.fit_transform(df['team'])
df['opponent_team'] = le_team.fit_transform(df['opponent_team'])
df['was_home'] = df['was_home'].map({False:0, True:1})

player_dict = {name: i for i, name in enumerate(le_name.classes_.tolist())}
position_dict = {position: i for i, position in enumerate(le_position.classes_.tolist())}
team_dict = {team: i for i, team in enumerate(le_team.classes_.tolist())}


FILE_PATH = os.path.join(MAIN_FOLDER, f'data/json/{position}/encoded_player_names.json')
with open(FILE_PATH, 'w') as json_file:
    json.dump(player_dict, json_file, indent=2)

FILE_PATH = os.path.join(MAIN_FOLDER, f'data/json/{position}/encoded_position.json')
with open(FILE_PATH, 'w') as json_file:
    json.dump(position_dict, json_file, indent=2)

FILE_PATH = os.path.join(MAIN_FOLDER, f'data/json/{position}/encoded_team_name.json')
with open(FILE_PATH, 'w') as json_file:
    json.dump(team_dict, json_file, indent=2)

print(f" -- Label Encoding (Success) -- \n")

"""### Modelling"""

X = df.drop('total_points', axis=1)
y = df['total_points']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20)

"""Random Forest"""

rf = RandomForestRegressor(n_estimators=150, min_samples_split=4, min_samples_leaf=2, max_depth=40)
rf.fit(X_train, y_train)
print(f" -- Model Fitted -- \n")

"""Dumping Model"""

FILE_PATH = os.path.join(MAIN_FOLDER, f'model/model_{position}.joblib')
joblib.dump(rf, FILE_PATH)
print(f" -- Model Dumped -- \n")