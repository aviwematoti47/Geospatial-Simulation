# ===================== Imports =========================
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from streamlit import session_state as state

# ===================== Sidebar Controls =========================
st.sidebar.title("📅 Simulation Controls")
total_days = st.sidebar.slider("Select number of days to simulate", 30, 365, 180)
run_simulation = st.sidebar.button("▶️ Run Simulation")

# ===================== Page Title =========================
st.title("🏪 Soweto Retail Business Simulation")
st.markdown("This app models business competition in Soweto's subsistence market using reinforcement learning strategies.")

# ===================== Game Rules and RL Explanation =========================
st.subheader("🎮 Game Rules and Simulation Logic")

st.markdown("""
### 👔 Business Strategies:
- **First-to-Market (F)**:
  - Enters first.
  - Grows fast early.
  - Suffers **10% intent loss per month** due to churn.

- **Loyalty-Based (L)**:
  - Enters after 30 days.
  - Grows slowly, retains customers better.
  - Loses **10% more customers to Opposition**.

- **Opposition (O)**:
  - Enters after day 90.
  - Only sets up where others already exist.
  - Hard to convert back once gained.

---

### 🤖 Reinforcement Learning Setup

- **State**:
  - Current day (1–365)
  - Zone status (which business is present)
  - Customer scores (e.g. Purchase Intention)
  - Churn risk

- **Actions**:
  - Open Store
  - Expand to adjacent zone
  - Lower prices
  - Do nothing

- **Rewards**:
  - +1 for customer gain
  - -1 for churn
  - +2 bonus if taking over competitor zone
""")

# ===================== Zone Grid Simulation =========================
# Simulate evolving 5x5 zone map
zone_map = np.full((5, 5), "", dtype=object)
phase_loyalty = 30
phase_opposition = 90
zone_snapshots = []

for day in range(1, total_days + 1):
    grid = np.full((5, 5), "", dtype=object)
    for i in range(5):
        for j in range(5):
            zone_id = i * 5 + j
            if day <= phase_loyalty and zone_id < 10:
                grid[i][j] = 'F'
            elif phase_loyalty < day <= phase_opposition and zone_id < 15:
                grid[i][j] = 'L'
            elif day > phase_opposition and zone_id < 25:
                grid[i][j] = 'O'
    zone_snapshots.append(grid)

# Sidebar zone slider
st.sidebar.markdown("### 📍 Explore Zone Changes")
selected_day = st.sidebar.slider("View zones on day:", 1, total_days, 1)

# Display the grid for the selected day
st.subheader(f"📦 Zone Ownership on Day {selected_day}")
current_grid = zone_snapshots[selected_day - 1]
zone_df = pd.DataFrame(current_grid)
zone_colors = zone_df.replace({
    'F': '🟦 F',
    'L': '🟩 L',
    'O': '🟥 O',
    '': '⬜️'
})
st.dataframe(zone_colors, use_container_width=True)

# ===================== Dynamic Zone Map =========================
st.subheader("🗺️ Dynamic Map of Zone Business Types")

# Define a fixed spatial grid (5x5) using lat/lon offsets
grid_base_lat, grid_base_lon = -26.267, 27.858  # Soweto center
lat_step, lon_step = 0.002, 0.002  # adjust spacing
day_grid = zone_snapshots[selected_day - 1]

# New map for the day
day_map = folium.Map(location=[grid_base_lat, grid_base_lon], zoom_start=14)

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
            ).add_to(day_map)

st_folium(day_map, width=700, height=500)

# ===================== Business Simulation Block =========================
if run_simulation:
    st.subheader("📈 Business Market Share Over Time")

    days = list(range(1, total_days + 1))
    first_market, loyalty_based, opposition = [], [], []
    churn_f, churn_l, churn_o = [], [], []

    f = 100  # Initial First-to-Market customers
    l = 0
    o = 0

    for day in days:
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

    # Create dataframes
    df_trends = pd.DataFrame({
        "Day": days,
        "First-to-Market": first_market,
        "Loyalty-Based": loyalty_based,
        "Opposition": opposition
    })

    df_churn = pd.DataFrame({
        "Day": days,
        "First-to-Market": churn_f,
        "Loyalty-Based": churn_l,
        "Opposition": churn_o
    })

    # Charts
    st.markdown("#### 📊 Market Share Trends")
    st.line_chart(df_trends.set_index("Day"))

    st.markdown("#### 📉 Churn Rates Per Business Type")
    st.line_chart(df_churn.set_index("Day"))

    # Export to CSV
    df_trends.to_csv("simulation_output.csv", index=False)
    df_churn.to_csv("churn_output.csv", index=False)
    st.success("Simulation complete. CSVs exported for Looker Studio.")
