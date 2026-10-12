# Pakistan Flood Intelligence Dashboard

An interactive rainfall monitoring dashboard built with Python to explore historical rainfall patterns across selected cities in Pakistan.

## Project Overview

This project analyses historical precipitation estimates for selected Pakistani cities to help users explore rainfall trends, compare cities, and identify days with unusually high rainfall.

## Features

- Interactive rainfall monitoring dashboard
- Daily rainfall trend visualisation
- City-to-city rainfall comparisons
- Monthly rainfall analysis
- City and date filters
- Rainfall threshold alerts
- City monitoring map
- Summary statistics and monitoring status table

## Technologies Used

- Python
- Streamlit
- Pandas
- Plotly
- Open-Meteo Historical Weather API

## Cities Included

- Karachi
- Hyderabad
- Sukkur
- Larkana
- Islamabad

## Dataset

The project uses historical precipitation estimates from 1 June 2022 to 31 October 2022, retrieved using the Open-Meteo Historical Weather API.

## How to Run Locally

1. Clone this repository:

   ```bash
   git clone https://github.com/salisher/pakistan-flood-intelligence.git
   ```

2. Open the project folder:

   ```bash
   cd pakistan-flood-intelligence
   ```

3. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

4. Activate the environment on Windows PowerShell:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

5. Install the dependencies:

   ```bash
   pip install streamlit pandas requests plotly
   ```

6. Launch the dashboard:

   ```bash
   streamlit run app.py
   ```

## Important Limitations

This is an educational data analytics project, not an official flood forecasting or early-warning system. Rainfall values are weather-model estimates and should not be treated as verified flood reports. The rainfall thresholds used for monitoring are illustrative, not official warning thresholds.

## Author

Syed Ali Sher Hashmi

[GitHub Profile](https://github.com/salisher)