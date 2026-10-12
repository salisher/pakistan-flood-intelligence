
import requests
import pandas as pd
from pathlib import Path

# Cities we want to monitor
CITIES = {
    "Karachi": (24.8607, 67.0011),
    "Hyderabad": (25.3960, 68.3578),
    "Sukkur": (27.7052, 68.8574),
    "Larkana": (27.5584, 68.2120),
    "Islamabad": (33.6844, 73.0479),
}

START_DATE = "2022-06-01"
END_DATE = "2022-10-31"

all_data = []

for city, (latitude, longitude) in CITIES.items():
    print(f"Downloading rainfall data for {city}...")

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": "precipitation_sum",
        "timezone": "Asia/Karachi",
    }

    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    weather = response.json()

    city_data = pd.DataFrame({
        "date": weather["daily"]["time"],
        "rainfall_mm": weather["daily"]["precipitation_sum"],
        "city": city,
    })

    all_data.append(city_data)

# Combine data from all five cities
df = pd.concat(all_data, ignore_index=True)

# Create a data folder if it does not exist
data_folder = Path("data")
data_folder.mkdir(exist_ok=True)

# Save the downloaded data
output_file = data_folder / "pakistan_rainfall.csv"
df.to_csv(output_file, index=False)

print("\nDownload complete!")
print(f"Total records: {len(df)}")
print(f"Saved to: {output_file.resolve()}")
print(df.head())
