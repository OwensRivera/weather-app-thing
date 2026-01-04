import tkinter as tk
from tkinter import ttk
import urllib.request
import urllib.parse
import json



def fetch_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


Weather_Code_Map = [
    ([0], "Clear Sky"),
    ([1, 2, 3], "Cloudy"),
    ([45, 48], "Fog"),
    ([51, 53, 55], "Drizzle"),
    ([61, 63, 65], "Rain"),
    ([71, 73, 75], "Snow"),
    ([80, 81, 82], "Rain Showers"),
    ([95], "Thunderstorm"),
    ([96, 99], "Thunderstorm with hail"),
]


def describe_weather_code(code: int) -> str:
    for codes, desc in Weather_Code_Map:
        if code in codes:
            return desc
    return "Unknown"
##

def geocode_city(city: str):
    city = city.strip()
    if not city:
        return None

    params = urllib.parse.urlencode({
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    })
    url = "https://geocoding-api.open-meteo.com/v1/search?" + params
    data = fetch_json(url)

    results = data.get("results", [])
    if not results:
        return None

    place = results[0]
    lat = place["latitude"]
    lon = place["longitude"]
    display = f"{place.get('name', city)}, {place.get('country', '')}".strip().strip(",")
    return (lat, lon, display)


def get_current_weather(lat: float, lon: float) -> dict:
    params = urllib.parse.urlencode({
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "timezone": "auto"
    })
    url = "https://api.open-meteo.com/v1/forecast?" + params
    data = fetch_json(url)

    current = data.get("current_weather")
    if not current:
        return {}

    code = int(current.get("weathercode", -1))
    return {
        "temperature_c": current.get("temperature"),
        "windspeed_kmh": current.get("windspeed"),
        "time": current.get("time"),
        "description": describe_weather_code(code)
    }


def get_7day_forecast(lat: float, lon: float) -> list:
    params = urllib.parse.urlencode({
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto"
    })
    url = "https://api.open-meteo.com/v1/forecast?" + params
    data = fetch_json(url)

    daily = data.get("daily", {})
    dates = daily.get("time", [])
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])

    forecast = []
    for d, hi, lo in zip(dates, highs, lows):
        forecast.append({"date": d, "high_c": hi, "low_c": lo})
    return forecast


def c_to_f(c):
    return (c * 9 / 5) + 32




def format_day(day: dict) -> str:
    return f"{day['date']}  High: {day['high_c']}°C  Low: {day['low_c']}°C"


def on_get_weather():
    city = city_entry.get().strip()
    if not city:
        status_var.set("Enter a city.")
        return

    location_var.set("—")
    temp_var.set("—")
    wind_var.set("—")
    time_var.set("—")
    desc_var.set("—")
    forecast_listbox.delete(0, tk.END)

    status_var.set("Loading...")
    root.update_idletasks()

    try:
        loc = geocode_city(city)
        if not loc:
            status_var.set("City not found.")
            return

        lat, lon, name = loc
        current = get_current_weather(lat, lon)
        forecast = get_7day_forecast(lat, lon)

        if not current:
            status_var.set("Weather unavailable.")
            return

        location_var.set(name)
        #temp_var.set(f"{current.get('temperature_c')} °C")
        c = current.get("temperature_c")
        f = c_to_f(c)
        temp_var.set(f"{round(c,1)} °C  /  {round(f,1)} °F")





        wind_var.set(f"{current.get('windspeed_kmh')} km/h")
        time_var.set(str(current.get("time")))
        desc_var.set(str(current.get("description")))

        for day in forecast:
            forecast_listbox.insert(tk.END, format_day(day))

        status_var.set("Done.")
    except Exception:
        status_var.set("Network error.")


root = tk.Tk()
root.title("Weather App")
root.geometry("700x700")
root.resizable(False, False)

main = ttk.Frame(root, padding=12)
main.pack(fill="both", expand=True)

ttk.Label(main, text="City:").grid(row=0, column=0, sticky="w")
city_entry = ttk.Entry(main, width=30)
city_entry.grid(row=0, column=1, sticky="we", padx=(8, 0))

ttk.Button(main, text="Get Weather", command=on_get_weather).grid(row=0, column=2, padx=(8, 0))

location_var = tk.StringVar(value="—")
temp_var = tk.StringVar(value="—")
wind_var = tk.StringVar(value="—")
time_var = tk.StringVar(value="—")
desc_var = tk.StringVar(value="—")
status_var = tk.StringVar(value="Ready.")

ttk.Label(main, text="Location:").grid(row=1, column=0, sticky="w", pady=(12, 0))
ttk.Label(main, textvariable=location_var).grid(row=1, column=1, columnspan=2, sticky="w", pady=(12, 0))

ttk.Label(main, text="Temp:").grid(row=2, column=0, sticky="w")
ttk.Label(main, textvariable=temp_var).grid(row=2, column=1, columnspan=2, sticky="w")

ttk.Label(main, text="Wind:").grid(row=3, column=0, sticky="w")
ttk.Label(main, textvariable=wind_var).grid(row=3, column=1, columnspan=2, sticky="w")

ttk.Label(main, text="Time:").grid(row=4, column=0, sticky="w")
ttk.Label(main, textvariable=time_var).grid(row=4, column=1, columnspan=2, sticky="w")

ttk.Label(main, text="Conditions:").grid(row=5, column=0, sticky="w")
ttk.Label(main, textvariable=desc_var).grid(row=5, column=1, columnspan=2, sticky="w")

ttk.Separator(main).grid(row=6, column=0, columnspan=3, pady=12, sticky="we")

ttk.Label(main, text="7-Day Forecast:").grid(row=7, column=0, sticky="w")
forecast_listbox = tk.Listbox(main, height=10, width=60)
forecast_listbox.grid(row=8, column=0, columnspan=3, sticky="we", pady=(6, 0))

ttk.Separator(main).grid(row=9, column=0, columnspan=3, pady=12, sticky="we")

ttk.Label(main, textvariable=status_var).grid(row=10, column=0, columnspan=3, sticky="w")

main.columnconfigure(1, weight=1)

root.bind("<Return>", lambda e: on_get_weather())
city_entry.focus()

root.mainloop()
