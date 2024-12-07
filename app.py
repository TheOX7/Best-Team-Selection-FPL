import streamlit as st
import pandas as pd
import base64
import os
from streamlit_option_menu import option_menu
from streamlit_echarts import st_echarts 
from pulp_rec_lineup import pulp_model  # Import fungsi dari file pulp_rec_lineup.py
from streamlit_extras.colored_header import colored_header

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

    logo_link('', r'assets/pl-logo.png', 100)
    enter()
    horizontal_line()

    selected = option_menu(menu_title=None, 
                          options=['Rec. Starting Eleven', 'Dataset Information'], 
                          icons=['house'], 
                          menu_icon='cast', default_index=0
                        )
    
    horizontal_line()
    
    st.markdown("""
        <div style='text-align: center; font-size:20px'>
            <b>Related Links</b> <br>
            <a href="https://fantasy.premierleague.com/help/rules" style="text-decoration: none;">FPL Rules</a> <br>
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
    horizontal_line()
    header_text('Fantasy Premier League (FPL) <br> Starting Lineup Recommendations', 36)
    horizontal_line()
    
    col_1, col_2 = st.columns(2)
    
    gw = 1
    option = ''
    
    with col_1:
        header_text('Starting Lineup Recommendations', 20)
        header_text('Includes Substitutions (15 Players & Under £100)', 16)
        
        col_1_1, col_1_2 = st.columns(2)
        with col_1_1:
            selected_gw = st.selectbox('Select Gameweek', [i for i in range(1,16)], index=0)
            gw = selected_gw
        with col_1_2:
            selected_option = st.selectbox('Select Model', ['General', 'per Position'], index=0)
            if selected_option == 'General': 
                option = 'general'
            else: 
                option = 'per-position'
        
        data = pd.read_csv(f'data/pulp/gw-{gw}/{option}/not_rec_lineup.csv')
        data = data.rename(columns={'total_points':'Actual Points'})
        if option == 'per-position':
            data = data.drop('element', axis=1)
        
        # Menggunakan fungsi pulp_model dengan data yang sudah di-load
        data_ = pulp_model(data)
        data_ = data_.drop(['condition'], axis=1)
        st.dataframe(data_, height=562, use_container_width=True, hide_index=True)
        
    with col_2:
        url = f'https://fantasy.premierleague.com/team-of-the-week/{gw}'
        st.markdown(f"""
            <div style='text-align: center; font-size:20px'>
                <a href={url} style="text-decoration: none;">
                    Team of The Week - Gameweek {gw}
                </a>
            </div>
            <br>
        """, unsafe_allow_html=True)
        
        # Path gambar berdasarkan gameweek
        image_path = f'assets/totw-gw-{gw}.png'
        
        # Cek apakah gambar tersedia
        if os.path.exists(image_path):
            st.image(image_path, use_column_width=True)
        else:
            st.warning(f'Team of The Week for Gameweek {gw} is not available yet.')
    
    horizontal_line()
    header_text(f'Gameweek {gw}: Expected Points (xTotPoints) for FPL Players', 32) 
    horizontal_line()
    data = data.sort_values(by='xTotPoints', ascending=False)
    st.dataframe(data, height=600, use_container_width=True, hide_index=True)
          
    # STACKED BAR CHART (COMPARING PLAYERS PERFORMANCE)
    data_last_5 = pd.read_csv(f'data/fpl/gw-{gw}/general_updated_features.csv')
    data_last_5 = pd.merge(data_last_5, data, on=['name', 'position', 'team', 'opponent_team'], how='left')    
    data_last_5 = data_last_5[~data_last_5['xTotPoints'].isna()]
    data_last_5 = data_last_5.sort_values(by='kickoff_time', ascending=False)
    data_last_5 = data_last_5.groupby('name').first().reset_index()
    
    enter() 
    
    col_subheader, col_mode_filter = st.columns([3, 1])
    with col_subheader:
        colored_header(
            label="Player Comparison",
            description="",
            color_name="orange-70",
        )

    with col_mode_filter:
        selected_how = st.selectbox(
            "Select Mode",
            ["Head to Head (Last 5 Games)", "Last 5 Games"], index=0
        )

    # Inisialisasi filtered_df dengan data_last_5
    filtered_df = data_last_5

    if selected_how == "Head to Head (Last 5 Games)":
        col_1, col_2, col_3 = st.columns(3)
        with col_1:
            selected_pos = st.selectbox("Select Position", filtered_df['position'].unique())

        # Filter dataframe berdasarkan position yang dipilih
        filtered_df = filtered_df[filtered_df['position'] == selected_pos]

        # Select home/away game
        with col_2:
            was_home_option = st.selectbox("Select Home or Away Game", ['Home', 'Away', 'Both'], index=2)

            was_home_mapping = {
                'Home': True,
                'Away': False,
                'Both': 'Both'
            }

            was_home = was_home_mapping[was_home_option]

        with col_3:
            selected_opponent_team = st.selectbox(
                "Select Opponent Team",
                data['opponent_team'].unique(),
                index=0
            )

        if was_home != 'Both':
            filtered_df = filtered_df[filtered_df['was_home'] == was_home]

        # Tambahkan filter untuk selected_opponent_team
        filtered_df = filtered_df[filtered_df['opponent_team'] == selected_opponent_team]

    elif selected_how == "Last 5 Games":
        col_1, col_2 = st.columns(2)
        with col_1:
            selected_pos = st.selectbox("Select Position", filtered_df['position'].unique())

        # Filter dataframe berdasarkan position yang dipilih
        filtered_df = filtered_df[filtered_df['position'] == selected_pos]

        # Select home/away game
        with col_2:
            was_home_option = st.selectbox("Select Home or Away Game", ['Home', 'Away', 'Both'], index=2)

            was_home_mapping = {
                'Home': True,
                'Away': False,
                'Both': 'Both'
            }

            was_home = was_home_mapping[was_home_option]

        # Filter dataframe berdasarkan home/away status
        if was_home != 'Both':
            filtered_df = filtered_df[filtered_df['was_home'] == was_home]

        
    # Non H2H column labels for comparison
    non_h2h_column_labels = {
        'xTotPoints': 'xTotPoints',
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

    # Modify column labels based on selected comparison mode
    if selected_how == "Head to Head (Last 5 Games)":
        non_h2h_column_labels = {
            'xTotPoints': 'xTotPoints',
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
    elif selected_how == "Last 5 Games":
        non_h2h_column_labels = {
            'xTotPoints': 'xTotPoints',
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
    non_h2h_display_labels = [non_h2h_column_labels.get(col, col) for col in non_h2h_column_labels]

    # Select features
    selected_labels = st.multiselect(
        "Select Features",
        non_h2h_display_labels
    )

    # Mapping balik dari label ke nama kolom asli
    selected_non_h2h_columns = [col for col in non_h2h_column_labels if non_h2h_column_labels.get(col, col) in selected_labels]

    if selected_non_h2h_columns:
        # Filter dataframe berdasarkan kolom yang dipilih
        filtered_df = filtered_df[['name', 'team', 'price', 'condition'] + selected_non_h2h_columns]

        # Rename kolom untuk tampilan yang lebih mudah dipahami
        rename_dict = {col: non_h2h_column_labels[col] for col in selected_non_h2h_columns}
        filtered_df = filtered_df.rename(columns=rename_dict)

        col_1_1, col_1_2 = st.columns(2)

        with col_1_1:
            st.subheader("Table Player's Stats")
            st.write("(Click on a Table Column to Order It)")
            st.dataframe(filtered_df, use_container_width=True, hide_index=True, height=500)

        with col_1_2:
            st.subheader('Player Comparison')
            
            selected_players = st.multiselect(
                "Select Players Name (Select at least two players)",
                filtered_df['name'].tolist()
            )

            if selected_players and selected_labels:
                # Filter dataframe berdasarkan pemain yang dipilih
                filtered_chart_df = filtered_df[filtered_df['name'].isin(selected_players)]

                # Pastikan dataframe diurutkan berdasarkan urutan pemain yang dipilih
                filtered_chart_df = filtered_chart_df.set_index('name').reindex(selected_players)

                # Data untuk chart
                series_data = []

                for feature in selected_labels:
                    # Get feature column from selected_non_h2h_columns
                    feature_column = [col for col in selected_non_h2h_columns if non_h2h_column_labels[col] == feature][0]
                    
                    # Ambil data dan pastikan diurutkan sesuai urutan pemain
                    data = filtered_chart_df[non_h2h_column_labels[feature_column]].tolist()

                    series_data.append({
                        "name": feature,
                        "type": "bar",
                        "stack": "total",
                        "label": {"show": True, "color": "#ffffff", "fontSize": 14},
                        "emphasis": {"focus": "series"},
                        "data": data,
                    })

                # Konfigurasi chart
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
                        "splitNumber": 5,
                        "minInterval": 1
                    },
                    "yAxis": {
                        "type": "category",
                        "data": selected_players,
                        "axisLabel": {"textStyle": {"color": "#ffffff", "fontSize": 14}},
                        "axisTick": {"show": False},
                    },
                    "series": series_data,
                }

                st_echarts(options=options, height="400px")


if selected == 'Dataset Information':
    pass