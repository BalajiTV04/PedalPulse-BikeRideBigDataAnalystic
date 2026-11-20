"""Generate a reproducible 50,000-row Divvy-like CSV for local demos."""
import csv
import os
import random
from datetime import datetime, timedelta


def make_sample(path=None, rows=50000):
    """Write realistic trip rows using only Python's standard library."""
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "Divvy_Trips_2019_Q1.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    random.seed(2019)
    stations = ["Streeter Dr & Grand Ave", "Theater on the Lake", "Clark St & Elm St",
                "Michigan Ave & Oak St", "Canal St & Adams St", "Wells St & Hubbard St",
                "State St & Van Buren St", "Broadway & Barry Ave", "Damen Ave & Division St",
                "Lake Shore Dr & Monroe St", "Dearborn St & Adams St", "Clinton St & Madison St"]
    start_base = datetime(2019, 1, 1)
    with open(path, "w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output)
        writer.writerow(["trip_id", "start_time", "end_time", "bikeid", "tripduration",
                         "from_station_id", "from_station_name", "to_station_id",
                         "to_station_name", "usertype", "gender", "birthyear"])
        for trip_id in range(1, rows + 1):
            start = start_base + timedelta(seconds=random.randrange(90 * 24 * 60 * 60))
            duration = random.triangular(90, 5400, 780)
            end = start + timedelta(seconds=duration)
            start_station = random.randrange(len(stations))
            end_station = random.randrange(len(stations))
            usertype = random.choices(["Subscriber", "Customer"], weights=[0.82, 0.18])[0]
            gender = random.choice(["Male", "Female", ""])
            birthyear = random.randint(1940, 2001) if gender else ""
            writer.writerow([trip_id, start.strftime("%Y-%m-%d %H:%M:%S"),
                             end.strftime("%Y-%m-%d %H:%M:%S"), random.randint(1000, 9999),
                             int(duration), 1000 + start_station, stations[start_station],
                             1000 + end_station, stations[end_station], usertype, gender, birthyear])
    return path


if __name__ == "__main__":
    print("Created:", make_sample())
