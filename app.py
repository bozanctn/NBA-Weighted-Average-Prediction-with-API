import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from nba_api.stats.endpoints import teamgamelog, teaminfocommon
from nba_api.stats.static import teams
import time
import warnings

# Suppress pandas warnings
warnings.filterwarnings('ignore', category=UserWarning)

# NBA team abbreviations and IDs
def get_team_info():
    all_teams = teams.get_teams()
    team_dict = {}
    for team in all_teams:
        team_dict[team['full_name']] = {
            'id': team['id'],
            'abbreviation': team['abbreviation']
        }
    return team_dict

def get_team_stats(team_id, team_name):
    try:
        # Get team statistics
        team_info = teaminfocommon.TeamInfoCommon(
            team_id=team_id,
            league_id='00'  # NBA league ID
        )
        team_stats = team_info.team_info_common.get_data_frame()
        
        if team_stats.empty:
            st.error(f"No statistics found for {team_name}.")
            return None
            
        return team_stats
    except Exception as e:
        st.error(f"Error fetching statistics ({team_name}): {e}")
        return None

def get_team_games(team_id, team_name):
    try:
        # Get all games
        gamelog = teamgamelog.TeamGameLog(
            team_id=team_id,
            season='2023-24',
            season_type_all_star='Regular Season'
        )
        df = gamelog.get_data_frames()[0]
        
        if df.empty:
            st.error(f"No game data found for {team_name}.")
            return None
        
        # Sort by date and get last 5 games
        try:
            # Try standard format first
            df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'], format='%b %d, %Y', errors='coerce')
        except ValueError:
            try:
                # Try alternative format
                df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'], format='%Y-%m-%d', errors='coerce')
            except ValueError:
                # Use automatic parsing as last resort
                df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'], errors='coerce')
        
        # Filter invalid dates
        df = df.dropna(subset=['GAME_DATE'])
        df = df.sort_values('GAME_DATE', ascending=False).head(5)
        
        # Check and fix column names
        required_columns = ['GAME_DATE', 'MATCHUP', 'WL', 'PTS']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Required columns not found for {team_name}.")
            return None
            
        # Calculate PLUS_MINUS if not present
        if 'PLUS_MINUS' not in df.columns:
            # Check column names from API
            if 'PLUS_MINUS' in df.columns:
                df['PLUS_MINUS'] = df['PLUS_MINUS']
            elif 'PLUS_MINUS_RANK' in df.columns:
                df['PLUS_MINUS'] = df['PLUS_MINUS_RANK']
            else:
                # Calculate opponent points
                df['OPP_PTS'] = df.apply(lambda row: int(row['MATCHUP'].split()[-1]) if row['MATCHUP'].split()[-1].isdigit() else 0, axis=1)
                df['PLUS_MINUS'] = df['PTS'] - df['OPP_PTS']
        
        # Select only needed columns
        df = df[['GAME_DATE', 'MATCHUP', 'WL', 'PTS', 'PLUS_MINUS']]
        
        # Separate home/away information
        df['homeaway'] = df['MATCHUP'].apply(lambda x: '@' if 'vs.' in x else '')
        
        # Separate scores
        df['Tm'] = df['PTS']
        df['Opp'] = df['PTS'] - df['PLUS_MINUS']
        
        # Format dates
        df['GAME_DATE'] = df['GAME_DATE'].dt.strftime('%d.%m.%Y')
        
        return df
    except Exception as e:
        st.error(f"Error fetching data ({team_name}): {e}")
        return None

def calculate_weighted_scores(team_name, team_info):
    try:
        team_id = team_info[team_name]['id']
        team_abbr = team_info[team_name]['abbreviation']
        
        st.info(f"Fetching data for {team_name} ({team_abbr})...")
        
        # Get team statistics
        team_stats = get_team_stats(team_id, team_name)
        if team_stats is None:
            return None, None
            
        # Get game data
        df = get_team_games(team_id, team_name)
        if df is None or df.empty:
            return None, None

        home_games = df[df['homeaway'] == ''].copy()
        away_games = df[df['homeaway'] == '@'].copy()

        if home_games.empty or away_games.empty:
            st.warning(f"Insufficient home/away data for {team_name}.")
            return None, None

        # Use season averages
        try:
            season_avg_pts = float(team_stats['PTS_PG'].iloc[0])
            season_avg_opp_pts = float(team_stats['OPP_PTS_PG'].iloc[0])
        except (KeyError, IndexError):
            # Use last games if season averages not available
            season_avg_pts = home_games['Tm'].mean()
            season_avg_opp_pts = away_games['Opp'].mean()

        # Calculate home team performance
        home_offense = home_games['Tm'].mean()  # Points scored as home team
        home_defense = home_games['Opp'].mean()  # Points allowed as home team
        
        # Calculate away team performance
        away_offense = away_games['Tm'].mean()  # Points scored as away team
        away_defense = away_games['Opp'].mean()  # Points allowed as away team

        # Calculate expected home score
        expected_home_score = (
            home_offense * 0.4 +  # Points scored as home team
            away_offense * 0.3 +  # Points scored as away team
            season_avg_pts * 0.3  # Season average
        )

        # Calculate expected away score
        expected_away_score = (
            away_offense * 0.4 +  # Points scored as away team
            home_offense * 0.3 +  # Points scored as home team
            season_avg_pts * 0.3  # Season average
        )

        # Apply home court advantage
        home_advantage = 1.05  # 5% advantage
        expected_home_score *= home_advantage

        return expected_home_score, expected_away_score
    except Exception as e:
        st.error(f"Calculation error ({team_name}): {e}")
        return None, None

# Streamlit interface
st.set_page_config(page_title="NBA Game Prediction App", page_icon="🏀")

st.title("🏀 NBA Game Prediction App")
st.markdown("""
This app predicts NBA game scores based on teams' last 5 games and season averages.
- Last 5 games performance (80% weight)
- Season averages (20% weight)
- Home court advantage is considered
""")

# Add GitHub link
st.markdown("""
[![GitHub](https://img.shields.io/badge/GitHub-View%20Source-181717?style=for-the-badge&logo=github)](https://github.com/bozanctn/NBA-Weighted-Average-Prediction-with-API)
""")

# Get team information
team_info = get_team_info()

# Team selection
col1, col2 = st.columns(2)
with col1:
    team_1_full = st.selectbox("Home Team", list(team_info.keys()))
    team_1 = team_info[team_1_full]['abbreviation']
with col2:
    team_2_full = st.selectbox("Away Team", list(team_info.keys()))
    team_2 = team_info[team_2_full]['abbreviation']

if st.button("Predict"):
    if team_1_full and team_2_full:
        if team_1_full == team_2_full:
            st.error("Please select different teams for home and away.")
        else:
            with st.spinner('Fetching data and calculating...'):
                home_scores = calculate_weighted_scores(team_1_full, team_info)
                time.sleep(1)  # API rate limit wait
                away_scores = calculate_weighted_scores(team_2_full, team_info)

                if home_scores is not None and away_scores is not None:
                    home_expected, _ = home_scores
                    _, away_expected = away_scores

                    if home_expected is not None and away_expected is not None:
                        total_basket = home_expected + away_expected
                        
                        # Show results
                        st.subheader("Prediction Results")
                        
                        # Create visualization
                        fig = go.Figure(data=[
                            go.Bar(name=f"{team_1_full} ({team_1})", x=['Home'], y=[home_expected], marker_color='blue'),
                            go.Bar(name=f"{team_2_full} ({team_2})", x=['Away'], y=[away_expected], marker_color='red')
                        ])
                        
                        fig.update_layout(
                            title="Expected Score Distribution",
                            xaxis_title="Team",
                            yaxis_title="Expected Points",
                            barmode='group',
                            annotations=[
                                dict(
                                    x=0,
                                    y=home_expected + 2,
                                    text=f"{home_expected:.1f}",
                                    showarrow=False,
                                    font=dict(size=12)
                                ),
                                dict(
                                    x=1,
                                    y=away_expected + 2,
                                    text=f"{away_expected:.1f}",
                                    showarrow=False,
                                    font=dict(size=12)
                                )
                            ]
                        )
                        
                        st.plotly_chart(fig)
                        
                        # Prediction explanation
                        st.markdown("""
                        ### Prediction Explanation
                        - **Blue bar**: Expected points for home team
                        - **Red bar**: Expected points for away team
                        - **Height**: Expected points for each team
                        - **Difference**: Expected point difference between teams
                        """)
                        
                        st.metric("Total Expected Points", f"{total_basket:.2f}")
                        
                        # Detailed information
                        st.subheader("Detailed Information")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(f"{team_1_full} ({team_1}) Expected Points", f"{home_expected:.2f}")
                        with col2:
                            st.metric(f"{team_2_full} ({team_2}) Expected Points", f"{away_expected:.2f}")
                        
                        # Last 5 games summary
                        st.subheader("Last 5 Games Summary")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**{team_1_full} ({team_1}) Last 5 Games:**")
                            df1 = get_team_games(team_info[team_1_full]['id'], team_1_full)
                            if df1 is not None:
                                st.dataframe(df1[['GAME_DATE', 'MATCHUP', 'WL', 'PTS']].style.set_properties(**{
                                    'background-color': 'lightblue',
                                    'color': 'black',
                                    'border-color': 'white'
                                }))
                        with col2:
                            st.write(f"**{team_2_full} ({team_2}) Last 5 Games:**")
                            df2 = get_team_games(team_info[team_2_full]['id'], team_2_full)
                            if df2 is not None:
                                st.dataframe(df2[['GAME_DATE', 'MATCHUP', 'WL', 'PTS']].style.set_properties(**{
                                    'background-color': 'lightblue',
                                    'color': 'black',
                                    'border-color': 'white'
                                }))
                    else:
                        st.error("An error occurred during calculation. Please try again.")
                else:
                    st.error("An error occurred while fetching data. Please try again.")
    else:
        st.warning("Please select both teams.") 
