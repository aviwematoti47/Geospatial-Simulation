# ===================== Imports =========================
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from streamlit import session_state as state

# ===================== Page Setup =========================
st.set_page_config(page_title="Soweto Retail Simulation", layout="wide")
st.title("🏪 Soweto Retail Business Simulation")

st.markdown("""
This app models business competition in Soweto's subsistence retail market using a simplified reinforcement learning simulation.
Move the slider to explore how business strategies evolve across time and space.
""")

# ===================== Sidebar Controls =========================
st.sidebar.title("📅 Simulation Controls")
total_days = st.sidebar.slider("Simulate how many days?", 30, 365, 180)
selected_day = st.sidebar.slider("View zones and stats on day:", 1, total_days, 1)
run_simulation = st.sidebar.button("▶️ Run Simulation")

# ===================== Game Rule Display =========================
st.sidebar.markdown("### 🎮 Game Strategy Rules")
st.sidebar.info("""
**F:** First-to-Market  
**L:** Loyalty-Based  
**O:** Opposition

- F enters first, loses 0.1% per day  
- L enters after Day 30, slower churn  
- O enters after Day 90, hard to convert
""")

# ===================== Simulation Data Storage =========================
if "df_trends" not in state:
    state.df_trends = None
    state.df_churn = None
    state.zone_snapshots = []

# ===================== Simulation Logic =========================
if run_simulation:
    days = list(range(1, total_days + 1))
    first_market, loyalty_based, opposition = [], [], []
    churn_f, churn_l, churn_o = [], [], []

    f, l, o = 100, 0, 0
    zone_snapshots = []

    for day in days:
        # Churn and growth
        f_loss = f * 0.001
        f -= f_loss
        churn_f.append(f_loss)

        if day > 30:
            l += 1.5
            l_loss = 0.05 * l if day > 90 else 0.01 * l
            l -= l_loss
            churn_l.append(l_loss)
        else:
            churn_l.append(0)

        if day > 90:
            o_gain = 2
            o += o_gain
            f -= 1
            l -= 1
            churn_o.append(0.5)
        else:
            churn_o.append(0)

        first_market.append(max(f, 0))
        loyalty_based.append(max(l, 0))
        opposition.append(max(o, 0))

        # Generate 5x5 zone grid per day
        grid = np.full((5, 5), "", dtype=object)
        for i in range(5):
            for j in range(5):
                zone_id = i * 5 + j
                if day <= 30 and zone_id < 10:
                    grid[i][j] = 'F'
                elif 30 < day <= 90 and zone_id < 15:
                    grid[i][j] = 'L'
                elif day > 90 and zone_id < 25:
                    grid[i][j] = 'O'
        zone_snapshots.append(grid)

    # Store in session_state
    state.df_trends = pd.DataFrame({
        "Day": days,
        "First-to-Market": first_market,
        "Loyalty-Based": loyalty_based,
        "Opposition": opposition
    })
    state.df_churn = pd.DataFrame({
        "Day": days,
        "First-to-Market": churn_f,
        "Loyalty-Based": churn_l,
        "Opposition": churn_o
    })
    state.zone_snapshots = zone_snapshots

    # Export
    state.df_trends.to_csv("simulation_output.csv", index=False)
    state.df_churn.to_csv("churn_output.csv", index=False)
    st.success("✅ Simulation complete. Data exported.")

# ===================== Display Section =========================
if state.df_trends is not None:

    col1, col2 = st.columns([1, 2])

    # ========= Zone Grid =========
    col1.subheader(f"📦 Zone Ownership on Day {selected_day}")
    zone_df = pd.DataFrame(state.zone_snapshots[selected_day - 1])
    zone_colors = zone_df.replace({
        'F': '🟦 F',
        'L': '🟩 L',
        'O': '🟥 O',
        '': '⬜️'
    })
    col1.dataframe(zone_colors, use_container_width=True)

    # ========= Real-Time Map =========
    col2.subheader("🗺️ Business Distribution Map")
    grid_base_lat, grid_base_lon = -26.267, 27.858
    lat_step, lon_step = 0.002, 0.002
    day_grid = state.zone_snapshots[selected_day - 1]

    map_dynamic = folium.Map(location=[grid_base_lat, grid_base_lon], zoom_start=14)
    for i in range(5):
        for j in range(5):
            b_type = day_grid[i][j]
            if b_type != "":
                lat = grid_base_lat + (i * lat_step)
                lon = grid_base_lon + (j * lon_step)
                color = 'blue' if b_type == 'F' else 'green' if b_type == 'L' else 'red'
                folium.Marker(
                    location=[lat, lon],
                    popup=f"Zone ({i},{j}) – {b_type}",
                    icon=folium.Icon(color=color)
                ).add_to(map_dynamic)
    st_folium(map_dynamic, width=700, height=500)

    # ========= Daily Snapshot Charts =========
    st.subheader(f"📊 Market Share and Churn on Day {selected_day}")
    day_stats = {
        "First-to-Market": state.df_trends.loc[selected_day - 1, "First-to-Market"],
        "Loyalty-Based": state.df_trends.loc[selected_day - 1, "Loyalty-Based"],
        "Opposition": state.df_trends.loc[selected_day - 1, "Opposition"]
    }

    churn_stats = {
        "First-to-Market": state.df_churn.loc[selected_day - 1, "First-to-Market"],
        "Loyalty-Based": state.df_churn.loc[selected_day - 1, "Loyalty-Based"],
        "Opposition": state.df_churn.loc[selected_day - 1, "Opposition"]
    }

    st.markdown("**📦 Market Share:**")
    st.bar_chart(pd.DataFrame(day_stats, index=["Customers"]))

    st.markdown("**🔥 Churn:**")
    st.bar_chart(pd.DataFrame(churn_stats, index=["Churned"]))
