import streamlit as st
import pandas as pd
import base64
from streamlit_option_menu import option_menu
from streamlit_echarts import st_echarts 

def horizontal_line():
    st.markdown(f'<hr>', unsafe_allow_html=True)
    
def enter():
    st.markdown('<br>', unsafe_allow_html=True)
        
def logo_link(link, path_img, width):
    st.markdown(
        """<div style="display: grid; place-items: center;">
        <a href="{}">
        <img src="data:image/png;base64,{}" width="{}">
        </a></div>""".format(
            link,
            base64.b64encode(open(path_img, "rb").read()).decode(),
            width,
        ),
        unsafe_allow_html=True,
    )
        
def header_text(text, size):
    st.markdown(f"""
        <div style='text-align: center; font-size:{size}px'>
            <b>
            {text}
            </b>
        </div>
    """, unsafe_allow_html=True)
   
st.set_page_config(
    page_title='Fantasy Premier League 2024/25',
    layout='wide'
)

with st.sidebar:
    st.markdown("""
        <div style='text-align: center; font-size:24px'>
            <b>
            Fantasy <br> Premier League <br>
            </b>
        </div>
    """, unsafe_allow_html=True)
    
    enter()

    # logo_link('', r'../assets/pl-logo.png', 100)
    enter()
    horizontal_line()

    selected = option_menu(menu_title=None, 
                          options=['Rec. Starting Eleven', 'Player Performance H2H', 'Player Stats'], 
                          icons=['house'], 
                          menu_icon='cast', default_index=0
                        )
    
    horizontal_line()
    
    st.markdown("""
        <div style='text-align: center; font-size:20px'>
            <b>Related Links</b> <br>
            <a href="https://github.com/vaastav/Fantasy-Premier-League/" style="text-decoration: none;">Data Source</a> <br>
            <a href="https://fantasy.premierleague.com/fixtures/" style="text-decoration: none;">FPL Fixtures</a> <br>
            <a href="https://github.com/TheOX7/Best-Team-Selection-FPL" style="text-decoration: none;">Github Repository</a> <br>
        </div>
    """, unsafe_allow_html=True)
    
    horizontal_line()
    
    st.markdown("""
        <div style='text-align: center; font-size:20px'>
            <b>Created By</b> <br>
            <a href="https://www.linkedin.com/in/marselius-agus-dhion/" style="text-decoration: none;">Marselius Agus Dhion</a> <br>
        </div>
    """, unsafe_allow_html=True)
    
if selected == 'Rec. Starting Eleven':
    header_text('Fantasy Premier League (FPL) <br> Starting Lineup Recommendation', 36)
    horizontal_line()
    
    col_1, col_2 = st.columns(2)
    
    gw = 1
    
    data = pd.read_csv(f'../data/pulp/gw-{gw}/rec-gw-{gw}-starting-lineup.csv')
    
    with col_1:
        header_text('Predicted Starting Lineup + Substitution (15 Players & Under 100£)', 20 )
        
        selected_gw = st.selectbox('Select Gameweek', [1, 2])
        gw = selected_gw
        
        data = pd.read_csv(f'../data/pulp/gw-{gw}/rec-gw-{gw}-starting-lineup.csv')
        st.dataframe(data, height=562, use_container_width=True, hide_index=True)
        
    with col_2:                
        if gw == 1:
            url = f'https://fantasy.premierleague.com/team-of-the-week/{gw}'
            st.markdown(f"""
                <div style='text-align: center; font-size:20px'>
                    <a href={url} style="text-decoration: none;">Team of The Week - Gameweek {gw}</a>
                </div>
            """, unsafe_allow_html=True)
            st.image('../assets/totw-gw-1.png', use_column_width=True)
        if gw == 2:
            url = f'https://fantasy.premierleague.com/team-of-the-week/{gw}'
            st.markdown(f"""
                <div style='text-align: center; font-size:20px'>
                    <a href={url} style="text-decoration: none;">Team of The Week - Gameweek {gw}</a>
                </div>
            """, unsafe_allow_html=True)
            st.image('../assets/totw-gw-2.png', use_column_width=True)
    
    horizontal_line()
    
    header_text(f'All Premier League Players Predicted Points for GW {gw}', 32)
    
    horizontal_line()
    
    col_1, col_2 = st.columns(2)
    
    data = pd.read_csv(f'../data/pulp/gw-{gw}/players-predicted-gw-{gw}-points.csv')
    data = data.sort_values(by='predicted_total_points', ascending=False)
    
    with col_1:
        selected_team = st.multiselect('Select Team', data['team'].sort_values().unique())
    with col_2:
        selected_pos = st.multiselect('Select Position', data['position'].sort_values().unique())

    if selected_team and not selected_pos: 
        data = data[data['team'].isin(selected_team)]
    elif selected_pos and not selected_team: 
        data = data[data['position'].isin(selected_pos)]
    elif selected_team and selected_pos:
        data = data[(data['team'].isin(selected_team)) & (data['position'].isin(selected_pos))]

    st.dataframe(data, height=600, use_container_width=True, hide_index=True) 

if selected == 'Player Performance H2H':
    
    horizontal_line()
    header_text('Players Stats - Last 5 Games Against Specific Team', size=40)
    horizontal_line()
 
    # Load data
    data = pd.read_csv('../data/processed/last-5-stats.csv')

    # Filter berdasarkan musim
    data_last_5 = data[data['season'].isin(['2023/24', '2024/25'])].reset_index(drop=True)

    col_1, col_2, col_3 = st.columns(3)

    with col_1:
        # Membuat filter untuk opponent_team tanpa nilai default
        selected_opponent = st.selectbox("Select Opponent Team", data_last_5['opponent_team'].unique())

    with col_2:
        # Membuat filter untuk position tanpa nilai default
        selected_pos = st.selectbox("Select Position", data_last_5['position'].unique())

    # Filter dataframe berdasarkan opponent_team dan position yang dipilih
    filtered_df = data_last_5[(data_last_5['opponent_team'] == selected_opponent) & (data_last_5['position'] == selected_pos)]

    with col_3:
        # Membuat filter untuk status home atau away (was_home) dengan label 'Home', 'Away', 'Both'
        was_home_option = st.selectbox("Select Home or Away Game", ['Home', 'Away', 'Both'])

        # Mapping opsi ke nilai boolean
        was_home_mapping = {
            'Home': True,
            'Away': False,
            'Both': 'Both'
        }

        # Menggunakan nilai boolean yang sesuai untuk filtering
        was_home = was_home_mapping[was_home_option]

    # Filter dataframe berdasarkan status home atau away
    if was_home != 'Both':
        filtered_df = filtered_df[filtered_df['was_home'] == was_home]

    # Mapping kolom ke nama yang lebih enak dibaca
    h2h_column_labels = {
        'tot_assists_last_5_h2h': 'Total Assists',
        'tot_bonus_last_5_h2h': 'Total Bonus',
        'tot_bps_last_5_h2h': 'Total BPS',
        'tot_own_goals_last_5_h2h': 'Total Own Goals',
        'tot_penalties_missed_last_5_h2h': 'Total Penalties Missed',
        'tot_penalties_saved_last_5_h2h': 'Total Penalties Saved',
        'tot_red_cards_last_5_h2h': 'Total Red Cards',
        'tot_yellow_cards_last_5_h2h': 'Total Yellow Cards',
        'tot_total_points_last_5_h2h': 'Total Points',
        'tot_goals_scored_last_5_h2h': 'Total Goals Scored',
        'tot_goals_conceded_last_5_h2h': 'Total Goals Conceded',
        'tot_clean_sheets_last_5_h2h': 'Total Clean Sheets',
        'tot_saves_last_5_h2h': 'Total Saves',
        'avg_minutes_last_5_h2h': 'Average Minutes',
        'avg_ict_index_last_5_h2h': 'Average ICT Index',
        'avg_influence_last_5_h2h': 'Average Influence',
        'avg_creativity_last_5_h2h': 'Average Creativity',
        'avg_threat_last_5_h2h': 'Average Threat',
        'avg_selected_last_5_h2h': 'Average Selected',
    }

    # Membuat filter multiselect tanpa nilai default
    h2h_columns = [col for col in filtered_df.columns if col.endswith('_h2h') and not col.startswith('team')]
    h2h_display_labels = [h2h_column_labels.get(col, col) for col in h2h_columns]

    selected_labels = st.multiselect(
        "Select Features",
        h2h_display_labels
    )

    # Mapping balik dari label ke nama kolom asli
    selected_h2h_columns = [col for col in h2h_columns if h2h_column_labels.get(col, col) in selected_labels]

    if selected_h2h_columns:
        filtered_df = filtered_df[['name', 'team'] + selected_h2h_columns]

        rename_dict = {col: h2h_column_labels[col] for col in selected_h2h_columns}
        filtered_df = filtered_df.rename(columns=rename_dict)

        col_1, col_2 = st.columns(2)

        with col_1:
            enter()
            header_text("Table Player's Stats", 20)
            header_text("(Click on a Table Column to Order It)", 16)
            enter()
            
            st.dataframe(filtered_df, use_container_width=True, hide_index=True, height=500)
        
        with col_2:
            enter()
            header_text('Player Comparison', 20)
            
            selected_players = st.multiselect(
                "Select Players Name (Select at least two players)",
                filtered_df['name'].tolist()
            )

            if selected_players and selected_labels:
                # Filter dataframe berdasarkan pemain yang dipilih
                filtered_df = filtered_df[filtered_df['name'].isin(selected_players)]
                filtered_df = filtered_df.set_index('name')

                # Series data untuk chart
                series_data = []

                for feature in selected_labels:
                    feature_column = rename_dict.get([col for col in selected_h2h_columns if h2h_column_labels[col] == feature][0])
                    data = filtered_df[feature_column].tolist()

                    series_data.append({
                        "name": feature,
                        "type": "bar",
                        "stack": "total",
                        "label": {"show": True, "color": "#ffffff", "fontSize": 14},
                        "emphasis": {"focus": "series"},
                        "data": data,
                    })

                options = {
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "legend": {
                        "data": selected_labels,
                        "textStyle": {"color": "#ffffff", "fontSize": 14}
                    },
                    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
                    "xAxis": {
                        "type": "value",
                        "axisLabel": {"textStyle": {"color": "#ffffff", "fontSize": 14}},
                        "splitNumber": 5,  # Number of ticks
                        "minInterval": 1  # Ensure ticks are integer values
                    },
                    "yAxis": {
                        "type": "category",
                        "data": selected_players,
                        "axisLabel": {"textStyle": {"color": "#ffffff", "fontSize": 14}},
                        "axisTick": {"show": False},  # Hide axis ticks if needed
                    },
                    "series": series_data,
                }

                st_echarts(options=options, height="400px")
                    
if selected == 'Player Stats':
    
    horizontal_line()
    header_text('Players Stats - Last 5 Games Against Every Team', size=40)
    horizontal_line()
 
    # Load data
    data = pd.read_csv('../data/processed/last-5-stats.csv')

    # Filter berdasarkan musim
    data_last_5 = data[data['season'].isin(['2023/24', '2024/25'])].reset_index(drop=True)
    
    # Sort data by date to get the most recent games
    # Assume 'date' is the column indicating the match date
    data_last_5 = data_last_5.sort_values(by='kickoff_time', ascending=False)

    # Group by player name and keep the most recent data
    data_last_5 = data_last_5.groupby('name').first().reset_index()

    col_1, col_2 = st.columns(2)

    with col_1:
        selected_pos = st.selectbox("Select Position", data_last_5['position'].unique())

    # Filter dataframe berdasarkan opponent_team dan position yang dipilih
    filtered_df = data_last_5[(data_last_5['position'] == selected_pos)]

    with col_2:
        was_home_option = st.selectbox("Select Home or Away Game", ['Home', 'Away', 'Both'])

        was_home_mapping = {
            'Home': True,
            'Away': False,
            'Both': 'Both'
        }

        was_home = was_home_mapping[was_home_option]

    # Filter dataframe berdasarkan status home atau away
    if was_home != 'Both':
        filtered_df = filtered_df[filtered_df['was_home'] == was_home]

    # Mapping kolom ke nama yang lebih mudah dibaca
    non_h2h_column_labels = {
        'tot_assists_last_5': 'Total Assists',
        'tot_bonus_last_5': 'Total Bonus',
        'tot_bps_last_5': 'Total BPS',
        'tot_own_goals_last_5': 'Total Own Goals',
        'tot_penalties_missed_last_5': 'Total Penalties Missed',
        'tot_penalties_saved_last_5': 'Total Penalties Saved',
        'tot_red_cards_last_5': 'Total Red Cards',
        'tot_yellow_cards_last_5': 'Total Yellow Cards',
        'tot_total_points_last_5': 'Total Points',
        'tot_goals_scored_last_5': 'Total Goals Scored',
        'tot_goals_conceded_last_5': 'Total Goals Conceded',
        'tot_clean_sheets_last_5': 'Total Clean Sheets',
        'tot_saves_last_5': 'Total Saves',
        'avg_minutes_last_5': 'Average Minutes',
        'avg_ict_index_last_5': 'Average ICT Index',
        'avg_influence_last_5': 'Average Influence',
        'avg_creativity_last_5': 'Average Creativity',
        'avg_threat_last_5': 'Average Threat',
        'avg_selected_last_5': 'Average Selected',
    }

    # Membuat filter multiselect tanpa nilai default
    non_h2h_columns = [col for col in filtered_df.columns if col.endswith('last_5') and not col.endswith('_h2h') and not col.startswith('team')]
    non_h2h_display_labels = [non_h2h_column_labels.get(col, col) for col in non_h2h_columns]

    selected_labels = st.multiselect(
        "Select Features",
        non_h2h_display_labels
    )

    # Mapping balik dari label ke nama kolom asli
    selected_non_h2h_columns = [col for col in non_h2h_columns if non_h2h_column_labels.get(col, col) in selected_labels]

    if selected_non_h2h_columns:
        filtered_df = filtered_df[['name', 'team'] + selected_non_h2h_columns]

        rename_dict = {col: non_h2h_column_labels[col] for col in selected_non_h2h_columns}
        filtered_df = filtered_df.rename(columns=rename_dict)

        col_1_1, col_1_2 = st.columns(2)

        with col_1_1:
            enter()
            header_text("Table Player's Stats", 20)
            header_text("(Click on a Table Column to Order It)", 16)
            enter()
                        
            st.dataframe(filtered_df, use_container_width=True, hide_index=True, height=500)
        
        with col_1_2:
            enter()
            header_text('Player Comparison', 20)
            enter()
            
            selected_players = st.multiselect(
                "Select Players Name (Select at least two players)",
                filtered_df['name'].tolist()
            )

            if selected_players and selected_labels:
                # Filter dataframe berdasarkan pemain yang dipilih
                filtered_df = filtered_df[filtered_df['name'].isin(selected_players)]
                filtered_df = filtered_df.set_index('name')

                # Series data untuk chart
                series_data = []

                for feature in selected_labels:
                    feature_column = rename_dict.get([col for col in selected_non_h2h_columns if non_h2h_column_labels[col] == feature][0])
                    data = filtered_df[feature_column].tolist()

                    series_data.append({
                        "name": feature,
                        "type": "bar",
                        "stack": "total",
                        "label": {"show": True, "color": "#ffffff", "fontSize": 14},
                        "emphasis": {"focus": "series"},
                        "data": data,
                    })

                options = {
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "legend": {
                        "data": selected_labels,
                        "textStyle": {"color": "#ffffff", "fontSize": 14}
                    },
                    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
                    "xAxis": {
                        "type": "value",
                        "axisLabel": {"textStyle": {"color": "#ffffff", "fontSize": 14}},
                        "splitNumber": 5,  # Number of ticks
                        "minInterval": 1  # Ensure ticks are integer values
                    },
                    "yAxis": {
                        "type": "category",
                        "data": selected_players,
                        "axisLabel": {"textStyle": {"color": "#ffffff", "fontSize": 14}},
                        "axisTick": {"show": False},  # Hide axis ticks if needed
                    },
                    "series": series_data,
                }

                st_echarts(options=options, height="400px")