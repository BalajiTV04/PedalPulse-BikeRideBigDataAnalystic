# PedalPulse

**PedalPulse** is a small web application for exploring Divvy bike-share trip data. It combines Python, Streamlit, Apache Spark (PySpark), and Plotly to turn a CSV file into a set of interactive ride summaries and charts.

This README documents the project for setup, demonstration, and report preparation.

## 1. Project overview

The Divvy Trips 2019 Q1 dataset contains trip-level records, including when a ride started, how long it lasted, its start and end stations, and the rider type. PedalPulse lets a user upload a compatible CSV and investigate its trip patterns in a browser.

Spark performs the data reading, cleaning, KPI calculations, and chart aggregations. The application converts only the small, aggregated Spark results to pandas DataFrames so Plotly can render them. The full trip dataset is not loaded into pandas for analysis.

### Project objectives

- Build a clear, lightweight interface for exploring Divvy trip data.
- Use Apache Spark for data preparation and all analytical aggregations.
- Summarize ride volume, duration, time of day, rider type, and popular stations.
- Let a user choose which charts to view and how to arrange them.
- Provide a repeatable local demonstration using generated sample data.

### Report-ready summary

PedalPulse demonstrates a local big-data analytics workflow using Divvy bike-share trip records. A user supplies a CSV through a Streamlit interface. PySpark validates and cleans the records, derives time-related fields, and computes headline statistics and chart aggregates. Plotly displays those small aggregate results as interactive charts. The implementation keeps the full trip processing in Spark and uses pandas only as the handoff format for plotting. A deterministic synthetic dataset supports demonstrations when the official dataset is unavailable.

### Technology stack

| Technology | Role in the project |
| --- | --- |
| Python | Application and data-processing language |
| Streamlit | Page layout, forms, file upload, controls, and interactive app flow |
| PySpark | Local Spark session, CSV processing, cleaning, KPIs, and aggregations |
| Plotly Express | Interactive charts rendered in the browser |
| pandas | Converts small Spark aggregate results to a format Plotly accepts |
| JSON and hashlib | Local user records and salted password hashes |

The application is designed for a local Spark session (`local[*]`). It does not require a Spark cluster.

## 2. Application workflow and architecture

The data path through the application is:

```text
Divvy CSV
   |
   v
Spark CSV reader and schema inference
   |
   v
Spark cleaning and derived columns
   |
   v
Cached cleaned Spark DataFrame
   |
   +--> Spark KPI aggregations
   +--> Spark chart aggregations
             |
             v
       Small pandas results
             |
             v
       Plotly visualizations in Streamlit
```

The user path is:

1. Open the public home page.
2. Sign in with an account or create a local account.
3. Upload a CSV or select the included sample dataset.
4. Review the ride KPIs.
5. Select charts and a layout.

The home, login, and dashboard pages share the same white interface, high-contrast text, and teal and coral accent colors.

## 3. Pages and features

### Home page

The public home page introduces PedalPulse, explains its Spark-based analysis, and describes the CSV-to-chart flow. The page includes a login action and three feature cards covering CSV upload, Spark analytics, and the five available charts.

### Login and sign-up

The authentication page provides separate Login and Sign up tabs. The first authentication action creates `users.json` and seeds the demonstration account:

| Username | Password |
| --- | --- |
| `demo` | `demo123` |

Passwords are not written as plain text. Each account has a random salt and a SHA-256 hash stored in the local JSON file. Sign-up checks for blank fields, duplicate usernames, and passwords shorter than six characters. Login failures display a clear message.

### Dashboard

The dashboard requires a logged-in user and provides:

- A CSV file uploader and a button for using the included sample data.
- Validation of the required columns: `start_time`, `tripduration`, `from_station_name`, and `usertype`.
- Five Spark-derived KPI cards.
- Five selectable charts, including quick options to show one, three, or all five.
- Grid, stacked, and tabbed chart layouts.
- A per-chart caption showing the recorded Spark aggregation time.
- A Logout button in the page header.

Selected file and Spark results are cached so changing chart selection or layout does not reload and clean the file each time. Uploaded CSV files are stored in `data/uploads/`.

## 4. Dataset and data preparation

### Expected schema

The Divvy Trips 2019 Q1 dataset has the following columns:

| Column | Description | Used by PedalPulse |
| --- | --- | --- |
| `trip_id` | Unique trip identifier | No |
| `start_time` | Ride start date and time | Yes |
| `end_time` | Ride end date and time | Cast when present |
| `bikeid` | Bicycle identifier | No |
| `tripduration` | Trip length in seconds | Yes |
| `from_station_id` | Start station identifier | No |
| `from_station_name` | Start station name | Yes |
| `to_station_id` | End station identifier | No |
| `to_station_name` | End station name | No |
| `usertype` | Subscriber or customer category | Yes |
| `gender` | Rider gender field in the source data | No |
| `birthyear` | Rider birth year field in the source data | No |

Only four columns are required for the implemented analyses: `start_time`, `tripduration`, `from_station_name`, and `usertype`. If `end_time` is present, Spark casts it to a timestamp; the current charts do not depend on it.

### Spark cleaning steps

The `load_and_clean` function in `spark_engine.py` performs these operations:

1. Reads the CSV using Spark's CSV reader with a header and inferred schema.
2. Checks the four required columns and reports any missing names.
3. Removes comma characters from `tripduration`, then casts the value to a number. This handles values such as `1,200` seconds.
4. Converts `start_time` and (when present) `end_time` to Spark timestamps.
5. Removes rows that have a null start time.
6. Keeps trips with a duration from 60 through 10,800 seconds (one minute through three hours), inclusive.
7. Derives `hour`, a short weekday name, Monday-first `day_order`, and `duration_min`.
8. Caches the cleaned Spark DataFrame and calls `count()` to materialize it.

All of these operations happen in Spark. The cleaning function returns both the cached DataFrame and its valid row count.

## 5. KPIs and visualizations

### KPI cards

The dashboard calculates these summary values from the cleaned Spark DataFrame:

- **Total rides:** number of rows remaining after cleaning.
- **Average duration:** mean ride duration, in minutes.
- **Peak hour:** hour of the day with the highest ride count.
- **Most common user:** user type with the highest ride count.
- **Spark processing:** elapsed time for the KPI aggregation group, displayed in seconds.

### Charts

Each chart's aggregation is defined as its own function in `spark_engine.py`. Each function performs a Spark `groupBy`, creates the small result, records elapsed time, and converts that result to pandas for Plotly.

| Chart | Spark aggregation | Plotly view |
| --- | --- | --- |
| Rides by hour | Group by `hour`; count rides; sort 0–23 | Line chart with markers |
| Rides by day | Group by weekday; count rides; sort Monday–Sunday | Bar chart |
| Subscriber vs Customer | Group by `usertype`; count rides and average duration | Donut chart; average duration is available on hover |
| Top 10 start stations | Group by `from_station_name`; count, sort descending, and limit to ten | Horizontal bar chart |
| Day x hour | Group by weekday and hour; count rides | Day-by-hour heatmap |

The chart aggregation results are cached for the selected file. Switching layouts or toggling charts reuses the results instead of repeating the Spark groupBy calculations.

## 6. Project file structure

```text
pedalpulse/
|-- app.py                  Streamlit page flow and interface
|-- spark_engine.py         Spark session, cleaning, KPIs, and chart aggregates
|-- auth.py                 Local sign-up, login, and password hashing
|-- styles.py               White theme, shared CSS, and Plotly palette
|-- make_sample.py          50,000-row synthetic CSV generator
|-- requirements.txt        Python dependencies
|-- README.md               Setup and project documentation
|-- users.json              Created when authentication is first used
|-- data/
    |-- Divvy_Trips_2019_Q1.csv  Local demonstration dataset
    |-- uploads/                 Uploaded CSV files
```

`users.json` and uploaded files are local runtime data. The `.gitignore` file excludes user records and upload contents from source control.

## 7. Setup and run (Windows PowerShell)

### Prerequisites

- Python 3.10 or newer.
- Java 11 or Java 17 (a JDK installation is recommended).
- Internet access for the initial Python dependency installation.

Check the installed tools:

```powershell
python --version
java -version
```

If Java is installed but Spark cannot find it, set `JAVA_HOME` to the JDK folder. For example, adjust the path below to match the installed JDK:

```powershell
$env:JAVA_HOME = "C:\Program Files\Eclipse Adoptium\jdk-17.0.21.9-hotspot"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"
```

### Create an environment and install dependencies

From the project directory:

```powershell
cd D:\big_data_project\pedalpulse
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Start the app

```powershell
streamlit run app.py
```

Streamlit prints a local address, normally `http://localhost:8501`. Open that address in a browser.

## 8. Demo instructions

1. Open the app at `http://localhost:8501`.
2. Select **Open my dashboard**.
3. Sign in with `demo` and `demo123`, or create a separate account.
4. On the dashboard, choose **Try the sample data** or upload a Divvy CSV.
5. Wait for Spark to clean and cache the data. The dashboard reports the number of usable rides.
6. Review the KPI cards.
7. Select any chart combination, or use **Show 1**, **Show 3 (top picks)**, or **Show all 5**.
8. Choose Grid, Stacked, or Tabs to change the chart arrangement.
9. Select **Logout** in the header to return to the public experience.

## 9. Synthetic sample data

`make_sample.py` creates 50,000 deterministic, synthetic trip records using only Python's standard library. It uses the same 12-column schema as the expected Divvy data, a fixed random seed, dates within the first quarter of 2019, a set of Chicago station names, and a weighted Subscriber/Customer mix. It is intended for application demonstrations and development; it is not an official Divvy dataset and should not be used to make claims about actual ridership.

Generate or replace the sample file with:

```powershell
python make_sample.py
```

The generated file is written to `data/Divvy_Trips_2019_Q1.csv`. The default generator output has 50,000 rows plus the CSV header.

## 10. Spark implementation details

The `spark_session` function in `app.py` is decorated with `st.cache_resource`, so Streamlit creates one Spark session for the running application. The session uses:

- `master("local[*]")` to run Spark locally using the available processor cores.
- `appName("PedalPulse")` as the Spark application name.
- Eight SQL shuffle partitions.
- A disabled Spark Web UI.
- `PYSPARK_PYTHON` and `PYSPARK_DRIVER_PYTHON` set to the active Python executable.

The cleaned Spark DataFrame is cached as a resource by file path, modification time, and size. Small chart outputs use Streamlit's data cache. This separation allows the app to retain the large Spark-side dataset while only transferring aggregated results to pandas and Plotly.

## 11. Error handling and limitations

- A CSV missing required columns is rejected with a message that names the missing columns.
- Rows with unusable start times or out-of-range trip durations are filtered out.
- An empty cleaned dataset is reported to the user instead of producing blank charts.
- Spark startup failures show a Java setup message. Use Java 11 or Java 17 for this project configuration.
- User records are stored locally in `users.json`; this is a small educational project, not a production authentication service.
- CSV uploads are written to local disk under `data/uploads/` and are not automatically deleted by the app.
- The sample dataset is synthetic. For analysis of actual Divvy usage, use the original source CSV.
- Google Fonts are optional; the CSS includes sans-serif fallbacks if the font service is unavailable.

## 12. Validation performed

The included synthetic dataset was used to verify the local Spark path. The cleaned 50,000-row sample produced KPI values and aggregate results for all five charts. A Streamlit dashboard smoke check rendered all five charts, including the heatmap, without app exceptions.

## 13. Dependencies

The project intentionally keeps its direct dependencies small:

```text
pyspark
streamlit
plotly
pandas
```

See `requirements.txt` for the dependency list used by pip.

## 14. Suggested report structure

The sections in this README can be used as the basis for a project report:

1. **Introduction and problem statement:** use the project overview and explain the need to explore trip-level bike-share data.
2. **Objectives and scope:** use the project objectives and expected dataset schema.
3. **Tools and technologies:** use the technology stack table and explain each component's role.
4. **System architecture:** use the workflow diagram and describe the CSV-to-Spark-to-Plotly path.
5. **Methodology:** describe the Spark cleaning steps, KPI logic, chart aggregations, and caching approach.
6. **Application design:** describe the home, authentication, upload, KPI, chart-selection, and layout screens.
7. **Implementation:** use the project file structure and Spark implementation details.
8. **Testing and results:** report the sample-data validation and the five chart outputs. Clearly identify the sample as synthetic if it was used.
9. **Limitations and conclusion:** use the limitations section and summarize what the prototype demonstrates.
