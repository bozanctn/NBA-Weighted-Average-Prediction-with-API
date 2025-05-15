# NBA Game Prediction App

This application predicts NBA game scores based on teams' recent performance and season averages. It uses the NBA API to fetch real-time data and provides a user-friendly interface for making predictions.

## Features

- Real-time data fetching from NBA API
- Score predictions based on:
  - Last 5 games performance (80% weight)
  - Season averages (20% weight)
  - Home court advantage (5% boost)
- Interactive team selection
- Visual score distribution
- Detailed game statistics
- Last 5 games summary for both teams

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/NBA-Weighted-Average-Predictions.git
cd NBA-Weighted-Average-Predictions
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit application:
```bash
streamlit run app.py
```

2. Select the home and away teams from the dropdown menus
3. Click "Predict" to see the expected score distribution
4. View detailed statistics and last 5 games summary

## How It Works

The application uses a weighted average system to predict game scores:

1. **Recent Performance (80%)**
   - Last 5 games statistics
   - Home and away game performance
   - Points scored and allowed

2. **Season Averages (20%)**
   - Team's season scoring average
   - Team's season defensive average

3. **Home Court Advantage**
   - 5% boost for home team
   - Based on historical NBA data

## Dependencies

- streamlit
- pandas
- plotly
- nba_api

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
