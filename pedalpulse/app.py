"""PedalPulse: a small Streamlit dashboard backed by Apache Spark."""
import hashlib
import html
import os
import plotly.express as px
import streamlit as st

from auth import login_user, signup_user
from spark_engine import (REQUIRED_COLUMNS, create_spark, load_and_clean,
                          calculate_kpis, chart_day, chart_heatmap,
                          chart_hour, chart_stations, chart_usertype)
from styles import CSS, chart_layout

ROOT = os.path.dirname(os.path.abspath(__file__))
SAMPLE_PATH = os.path.join(ROOT, "data", "Divvy_Trips_2019_Q1.csv")
UPLOAD_DIR = os.path.join(ROOT, "data", "uploads")
GRAPH_TITLES = {
    "Rides by hour": "Rides by hour",
    "Rides by day": "Rides by day",
    "User type": "Subscriber vs Customer",
    "Top stations": "Top 10 start stations",
    "Day x hour": "Day x hour",
}
GRAPH_TYPES = {
    "Rides by hour": "Line chart",
    "Rides by day": "Bar chart",
    "User type": "Donut chart",
    "Top stations": "Horizontal bar chart",
    "Day x hour": "Heatmap",
}

st.set_page_config(page_title="PedalPulse", page_icon="P", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "home"
if "username" not in st.session_state:
    st.session_state.username = None
if "data_path" not in st.session_state:
    st.session_state.data_path = None
if "using_sample" not in st.session_state:
    st.session_state.using_sample = False


@st.cache_resource(show_spinner="Starting local Spark...")
def spark_session():
    return create_spark()


@st.cache_resource(show_spinner="Spark is cleaning and caching the trip data...")
def cached_cleaned_data(_spark, file_path, modified_time, file_size):
    """Keep the cleaned Spark DataFrame alive while dashboard controls change."""
    return load_and_clean(_spark, file_path)


def go(page):
    st.session_state.page = page


def header():
    left, right = st.columns([5, 1])
    with left:
        st.markdown('<div class="brand"><span class="brand-mark">PP</span> PedalPulse <span class="badge">Powered by Apache Spark</span></div>', unsafe_allow_html=True)
    with right:
        if st.session_state.username:
            if st.button("Logout", key="logout"):
                st.session_state.username = None
                go("home")
                st.rerun()


def home_page():
    header()
    st.markdown('''<div class="hero-panel"><div class="hero-copy"><div class="eyebrow">BIG DATA, IN MOTION</div><h1>Every ride has<br>a story.</h1><p>Turn thousands of bike trips into clear patterns. Explore the pulse of Chicago with local Spark analytics.</p></div><div class="hero-art"><div class="orbit"></div><div class="orbit two"></div><div class="pulse-dot"></div><div class="hero-stat"><strong>50K+</strong><span>trips ready to explore</span></div></div></div>''', unsafe_allow_html=True)
    st.markdown('<div class="section-intro"><div class="eyebrow">YOUR DATA, IN MOTION</div><h2>Insights built for exploration</h2><p>Upload a Divvy dataset and find the patterns behind every trip.</p></div>', unsafe_allow_html=True)
    cta, helper = st.columns([1, 4])
    with cta:
        if st.button("Open my dashboard  ->", key="hero_login", use_container_width=True):
            go("auth")
            st.rerun()
    with helper:
        st.markdown('<div class="upload-note">Local analytics powered by Apache Spark. Your CSV is processed on this machine.</div>', unsafe_allow_html=True)
    cards = st.columns(3)
    features = [("CSV", "Upload any Divvy CSV", "Bring your own trip data and get a quick quality check before analysis."),
                ("SP", "Spark-powered analytics", "Run every transformation and aggregation locally with Apache Spark."),
                ("05", "Five interactive charts", "Explore hourly trends, weekdays, rider types, stations, and a trip heatmap.")]
    for col, (icon, title, body) in zip(cards, features):
        with col:
            st.markdown('<div class="feature"><div class="feature-icon">%s</div><h3>%s</h3><p>%s</p></div>' % (icon, title, body), unsafe_allow_html=True)
    st.markdown('<div class="architecture"><span>01 &nbsp; CSV</span><span class="step">&gt;</span><span>02 &nbsp; Apache Spark</span><span class="step">&gt;</span><span>03 &nbsp; Aggregates</span><span class="step">&gt;</span><span>04 &nbsp; Interactive charts</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="footer">Big Data Analytics Mini Project</div>', unsafe_allow_html=True)


def auth_page():
    header()
    left, right = st.columns([.95, 1.05], gap="large")
    with left:
        st.markdown('''<div class="auth-aside"><div class="eyebrow">WELCOME TO PEDALPULSE</div><h2>Make every ride count.</h2><p>Sign in to turn trip records into a clear picture of when, where, and how Chicago rides.</p><div class="auth-point"><span class="auth-check">01</span> Spark analysis runs locally</div><div class="auth-point"><span class="auth-check">02</span> Five interactive views</div><div class="auth-point"><span class="auth-check">03</span> Bring your own Divvy CSV</div></div>''', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="page-title"><div class="eyebrow">YOUR RIDE DATA</div><h2>Sign in or create an account</h2><p>Pick up where your next insight begins.</p></div>', unsafe_allow_html=True)
        login_tab, signup_tab = st.tabs(["Login", "Sign up"])
        with login_tab:
            st.markdown('<div class="upload-note">Demo access: <strong>demo</strong> / <strong>demo123</strong></div>', unsafe_allow_html=True)
            st.write("")
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Login to PedalPulse", use_container_width=True)
            if submitted:
                ok, message = login_user(username, password)
                if ok:
                    st.session_state.username = username.strip()
                    go("dashboard")
                    st.rerun()
                st.error(message)
        with signup_tab:
            with st.form("signup_form"):
                username = st.text_input("Choose a username", placeholder="e.g. cityrider")
                password = st.text_input("Choose a password", type="password", placeholder="At least 6 characters")
                confirm = st.text_input("Confirm password", type="password", placeholder="Repeat your password")
                submitted = st.form_submit_button("Create my account", use_container_width=True)
            if submitted:
                if password != confirm:
                    st.error("The passwords do not match.")
                else:
                    ok, message = signup_user(username, password)
                    if ok:
                        st.success(message)
                    else:
                        st.error(message)


def chart_data(df, cache_key):
    """Keep small Spark aggregations cached across UI changes for this upload."""
    return cached_charts(df, cache_key)


@st.cache_data(show_spinner=False)
def cached_charts(_df, cache_key):
    return {
        "Rides by hour": chart_hour(_df),
        "Rides by day": chart_day(_df),
        "User type": chart_usertype(_df),
        "Top stations": chart_stations(_df),
        "Day x hour": chart_heatmap(_df),
    }


def render_chart(title, result):
    data, elapsed = result
    if data.empty:
        st.info("No data is available for this chart.")
        return
    if title == "Rides by hour":
        fig = px.line(data, x="hour", y="rides", markers=True, color_discrete_sequence=["#0F6265"],
                      labels={"hour": "Hour of day", "rides": "Rides"})
        fig.update_traces(line={"color": "#0F6265", "width": 3},
                          marker={"color": "#E85E53", "size": 8, "line": {"color": "#FFFFFF", "width": 1.5}})
    elif title == "Rides by day":
        fig = px.bar(data, x="day", y="rides", color_discrete_sequence=["#0F6265"],
                     labels={"day": "Day", "rides": "Rides"})
        fig.update_traces(marker={"color": "#0F6265", "line": {"color": "#083F43", "width": 1}})
    elif title == "User type":
        fig = px.pie(data, names="usertype", values="rides", hole=0.58, hover_data=["avg_duration_min"],
                     color_discrete_sequence=["#0F6265", "#E85E53", "#D89C3C", "#4D7D82"],
                     labels={"avg_duration_min": "Avg duration (min)"})
        fig.update_traces(textinfo="percent", textfont={"color": "#FFFFFF", "size": 14},
                          marker={"line": {"color": "#FFFFFF", "width": 2}})
        fig.update_layout(legend={"font": {"color": "#172B3A", "size": 13}})
    elif title == "Top stations":
        fig = px.bar(data, x="rides", y="station", orientation="h", color_discrete_sequence=["#E85E53"],
                     labels={"station": "Start station", "rides": "Rides"})
        fig.update_traces(marker={"color": "#0F6265", "line": {"color": "#083F43", "width": 1}})
        fig.update_yaxes(autorange="reversed")
    else:
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        matrix = (data.pivot(index="day", columns="hour", values="rides")
                  .reindex(index=weekdays, columns=list(range(24)), fill_value=0).fillna(0))
        fig = px.imshow(matrix, aspect="auto", labels={"x": "Hour of day", "y": "Day", "color": "Rides"},
                        color_continuous_scale=["#F1E9DD", "#F7B1A4", "#E85E53", "#AD3B39", "#0A484C"])
    fig.update_layout(**chart_layout())
    fig.update_layout(legend={"font": {"color": "#172B3A", "size": 12}})
    fig.update_xaxes(tickfont={"color": "#263A48", "size": 12}, title_font={"color": "#172B3A", "size": 13},
                     gridcolor="#DDE5EA", zerolinecolor="#AAB9C2")
    fig.update_yaxes(tickfont={"color": "#263A48", "size": 12}, title_font={"color": "#172B3A", "size": 13},
                     gridcolor="#DDE5EA", zerolinecolor="#AAB9C2", automargin=True)
    if title == "Day x hour":
        fig.update_coloraxes(colorbar={"tickfont": {"color": "#263A48", "size": 11},
                                       "outlinecolor": "#AAB9C2", "outlinewidth": 1})
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.caption("Computed by Spark in %.2f s" % elapsed)


def dashboard():
    header()
    st.markdown('<div class="page-title"><div class="eyebrow">YOUR RIDE DATA</div><h1>Dashboard</h1><p>Bring in a CSV, scan the ride summary, and explore the patterns.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label"><span class="section-num">1</span> Add your trip data</div>', unsafe_allow_html=True)

    def select_sample():
        st.session_state.data_path = SAMPLE_PATH
        st.session_state.using_sample = True

    with st.container(border=True):
        st.markdown("#### Upload a Divvy CSV")
        st.caption("Required columns: start_time, tripduration, from_station_name, usertype")
        uploaded = st.file_uploader("Drop your CSV here or browse files", type=["csv"], label_visibility="collapsed")
        if uploaded is not None:
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            safe_name = os.path.basename(uploaded.name)
            upload_path = os.path.join(UPLOAD_DIR, safe_name)
            uploaded_bytes = uploaded.getvalue()
            upload_signature = (uploaded.name, hashlib.sha256(uploaded_bytes).hexdigest())
            if (st.session_state.get("upload_signature") != upload_signature
                    or not os.path.isfile(upload_path)):
                with open(upload_path, "wb") as output:
                    output.write(uploaded_bytes)
                st.session_state.upload_signature = upload_signature
                st.session_state.using_sample = False
                st.session_state.data_path = upload_path
            elif not st.session_state.using_sample:
                st.session_state.data_path = upload_path
        sample_col, note_col = st.columns([1, 3])
        with sample_col:
            if os.path.isfile(SAMPLE_PATH):
                st.button("Try the sample data", on_click=select_sample, use_container_width=True)
        with note_col:
            if os.path.isfile(SAMPLE_PATH):
                st.caption("Explore the included 50,000 ride demo dataset.")
    selected_path = st.session_state.data_path
    if not selected_path:
        st.info("Upload a CSV or choose the sample file to get started.")
        return
    st.markdown('<span class="loaded-pill">DATASET READY &nbsp; %s</span>' % html.escape(os.path.basename(selected_path)), unsafe_allow_html=True)
    try:
        spark = spark_session()
        file_mtime = os.path.getmtime(selected_path)
        file_size = os.path.getsize(selected_path)
        frame, row_count = cached_cleaned_data(spark, os.path.abspath(selected_path), file_mtime, file_size)
        if row_count == 0:
            st.error("No usable trips found. Check the date and duration columns in your CSV.")
            return
        st.success("Spark cleaned and cached %s usable rides." % format(row_count, ","))
        kpis, processing_time = calculate_kpis(frame)
        st.markdown('<div class="section-label"><span class="section-num">2</span> Trip snapshot</div>', unsafe_allow_html=True)
        cols = st.columns(5)
        labels = ["Total rides", "Avg duration", "Peak hour", "Most common user", "Spark processing"]
        vals = [format(kpis["total_rides"], ","), "%.1f min" % kpis["avg_duration_min"],
                "%02d:00" % kpis["peak_hour"], kpis["common_user"], "%.2f s" % processing_time]
        for col, label, value in zip(cols, labels, vals):
            col.markdown('<div class="kpi"><small>%s</small><strong>%s</strong></div>' %
                         (html.escape(label), html.escape(str(value))), unsafe_allow_html=True)
        st.markdown('<div class="section-label"><span class="section-num">3</span> Choose your graphs</div>', unsafe_allow_html=True)
        names = ["Rides by hour", "Rides by day", "User type", "Top stations", "Day x hour"]
        defaults = st.session_state.get("selected_charts", [names[0], names[1], names[2]])
        selected = []
        boxes = st.columns(5)
        for col, name in zip(boxes, names):
            with col:
                if st.checkbox(GRAPH_TITLES[name] + " · " + GRAPH_TYPES[name],
                               value=name in defaults, key="chart_" + name):
                    selected.append(name)
        b1, b2, b3, _ = st.columns([1, 1.5, 1.5, 4])
        def set_chart_preset(preset):
            st.session_state.selected_charts = preset
            for chart_name in names:
                st.session_state["chart_" + chart_name] = chart_name in preset

        b1.button("Show 1", on_click=set_chart_preset, args=(names[:1],))
        b2.button("Show 3 (top picks)", on_click=set_chart_preset, args=(names[:3],))
        b3.button("Show all 5", on_click=set_chart_preset, args=(names[:],))
        st.session_state.selected_charts = selected
        st.markdown('<div class="section-label"><span class="section-num">4</span> Choose a layout</div>', unsafe_allow_html=True)
        layout = st.radio("Choose a chart layout", ["Grid (2 columns)", "Stacked (full width)", "Tabs"], horizontal=True)
        if not selected:
            st.info("Select at least one graph above.")
            return
        # Path, modification time, and size identify the uploaded file for the cache.
        cache_key = (os.path.abspath(selected_path), file_mtime, file_size)
        results = chart_data(frame, cache_key)
        chosen = [(name, results[name]) for name in selected]
        if layout == "Tabs":
            tabs = st.tabs([name for name, _ in chosen])
            for tab, (name, result) in zip(tabs, chosen):
                with tab:
                    with st.container(border=True):
                        st.markdown('<div class="graph-heading"><h3>%s</h3><span>%s</span></div>' %
                                    (html.escape(GRAPH_TITLES[name]), html.escape(GRAPH_TYPES[name])), unsafe_allow_html=True)
                        render_chart(name, result)
        elif layout == "Stacked (full width)":
            for name, result in chosen:
                with st.container(border=True):
                    st.markdown('<div class="graph-heading"><h3>%s</h3><span>%s</span></div>' %
                                (html.escape(GRAPH_TITLES[name]), html.escape(GRAPH_TYPES[name])), unsafe_allow_html=True)
                    render_chart(name, result)
        else:
            for i in range(0, len(chosen), 2):
                cols = st.columns(2)
                for col, (name, result) in zip(cols, chosen[i:i + 2]):
                    with col:
                        with st.container(border=True):
                            st.markdown('<div class="graph-heading"><h3>%s</h3><span>%s</span></div>' %
                                        (html.escape(GRAPH_TITLES[name]), html.escape(GRAPH_TYPES[name])), unsafe_allow_html=True)
                            render_chart(name, result)
    except Exception as exc:
        message = str(exc)
        if ("JAVA_GATEWAY_EXITED" in message or "Java gateway" in message or "Java" in message
                or "getSubject is not supported" in message or "UnsupportedOperationException" in message):
            st.error("Could not start Spark. Please install Java 11 or Java 17, set JAVA_HOME, and restart the app.")
        else:
            st.error("Could not process this CSV. Please check that it is a valid Divvy trip file. Details: %s" % message[:250])


if st.session_state.page == "home":
    home_page()
elif st.session_state.page == "auth":
    auth_page()
elif st.session_state.page == "dashboard":
    if not st.session_state.username:
        go("auth")
        auth_page()
    else:
        dashboard()
