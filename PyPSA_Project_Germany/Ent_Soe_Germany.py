import requests
import pandas as pd
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
from datetime import datetime

# CONFIG
API_KEY = "989162e8-10d5-4e35-b492-d6586e28f799"
COUNTRY_CODE = "10Y1001A1001A83F"
START_DATE = "20250719"
END_DATE = "20250819"
OUTPUT_FILE = "entsoe_germany_load_aug2025.csv"
# API REQUEST
url = (
    f"https://web-api.tp.entsoe.eu/api?securityToken={API_KEY}"
    f"&documentType=A65&processType=A16&outBiddingZone_Domain={COUNTRY_CODE}"
    f"&periodStart={START_DATE}0000&periodEnd={END_DATE}2300"
)
response = requests.get(url)

if response.status_code != 200:
    print("❌ Error fetching data:", response.text)
    exit()

# PARSE XML RESPONSE
root = ET.fromstring(response.content)
namespace = {"ns": "urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0"}

data = []
for timeseries in root.findall("ns:TimeSeries", namespace):
    for period in timeseries.findall("ns:Period", namespace):
        start = period.find("ns:timeInterval/ns:start", namespace).text
        resolution = period.find("ns:resolution", namespace).text

        for point in period.findall("ns:Point", namespace):
            position = int(point.find("ns:position", namespace).text)
            qty = float(point.find("ns:quantity", namespace).text)
            # Calculate timestamp
            timestamp = pd.to_datetime(start) + pd.Timedelta(hours=position - 1)
            data.append([timestamp, qty])

# CREATE DATAFRAME
df = pd.DataFrame(data, columns=["datetime", "load_MW"])
df = df.sort_values("datetime")
df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Saved Germany load data to {OUTPUT_FILE}")

# PLOT FIGURE
plt.figure(figsize = (12,6))
plt.plot (df["datetime"], df["load_MW"], label="Germany load(MW)", linewidth=1)
plt.title("Germany Electricity load last 30 days", fontsize=14)
plt.xlabel("Date", fontsize=12)
plt.ylabel("load_MW", fontsize=12)
plt.legend()
plt.grid(True, linestyle="--", alpha=0.6)
plt.tight_layout()
plt.savefig("germany_load_last_30days.png", dpi=300)
plt.show()

print("📊 Plot saved as germany_load_last_30days.png")

