# ===================== Imports =========================
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from streamlit import session_state as state
import networkx as nx
import matplotlib.pyplot as plt
import random

# ===================== Page Setup =========================
st.set_page_config(page_title="Soweto Retail Simulation", layout="wide")
st.title("\U0001F3EA Soweto Retail Business Simulation")

st.markdown("""
This app models business competition in Soweto's subsistence retail market using a simplified reinforcement learning simulation.
Move the slider to explore how business strategies evolve across time and space.
""")

# ===================== Sidebar Controls =========================
st.sidebar.title("\U0001F4C5 Simulation Controls")
total_days = st.sidebar.slider("Simulate how many days?", 30, 365, 180)
selected_day = st.sidebar.slider("View zones and stats on day:", 1, total_days, 1)
run_simulation = st.sidebar.button("▶️ Run Simulation")

# ===================== Game Rule Display =========================
st.sidebar.markdown("### \U0001F3AE Game Strategy Rules")
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

# ===================== Step 1: Create 5x5 Zone Network =========================
rows, cols = 5, 5
G = nx.Graph()
for i in range(rows):
    for j in range(cols):
        node_id = f"Z{i*cols + j}"
        G.add_node(node_id, pos=(j, -i))
for i in range(rows):
    for j in range(cols):
        current = f"Z{i*cols + j}"
        if j < cols - 1:
            G.add_edge(current, f"Z{i*cols + (j+1)}")
        if i < rows - 1:
            G.add_edge(current, f"Z{(i+1)*cols + j}")

# ===================== Step 2: Simulation Logic =========================
if run_simulation:
    days = list(range(1, total_days + 1))
    first_market, loyalty_based, opposition = [], [], []
    churn_f, churn_l, churn_o = [], [], []

    f, l, o = 100, 0, 0
    zone_snapshots = []

    for node in G.nodes:
        G.nodes[node]['business'] = ''
        G.nodes[node]['history'] = []

    for day in days:
        for node in G.nodes:
            current_type = G.nodes[node].get('business', '')
            neighbors = list(G.neighbors(node))

            if current_type == '':
                if day <= 30 and random.random() < 0.2:
                    G.nodes[node]['business'] = 'F'
                elif 30 < day <= 90 and any(G.nodes[n]['business'] == 'F' for n in neighbors):
                    if random.random() < 0.3:
                        G.nodes[node]['business'] = 'L'
                elif day > 90 and any(G.nodes[n]['business'] in ['F', 'L'] for n in neighbors):
                    if random.random() < 0.4:
                        G.nodes[node]['business'] = 'O'

            elif current_type == 'F' and day > 90 and random.random() < 0.05:
                G.nodes[node]['business'] = 'O'
            elif current_type == 'L' and day > 90 and random.random() < 0.1:
                G.nodes[node]['business'] = 'O'

            G.nodes[node]['history'].append(G.nodes[node]['business'])

        # Track business totals
        f = sum(1 for n in G.nodes if G.nodes[n]['business'] == 'F')
        l = sum(1 for n in G.nodes if G.nodes[n]['business'] == 'L')
        o = sum(1 for n in G.nodes if G.nodes[n]['business'] == 'O')
        first_market.append(f)
        loyalty_based.append(l)
        opposition.append(o)
        churn_f.append(random.uniform(0.1, 1.0))
        churn_l.append(random.uniform(0.1, 1.5))
        churn_o.append(random.uniform(0.1, 2.0))

        # Snapshot grid for map rendering
        grid = np.full((5, 5), '', dtype=object)
        for i in range(5):
            for j in range(5):
                node_id = f"Z{i*cols + j}"
                grid[i][j] = G.nodes[node_id]['business']
        zone_snapshots.append(grid)

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
    st.success("✅ Simulation complete. Data generated.")

# ===================== Display Section =========================
if state.df_trends is not None:
    col1, col2 = st.columns([1, 2])

    col1.subheader(f"\U0001F4E6 Zone Ownership on Day {selected_day}")
    zone_df = pd.DataFrame(state.zone_snapshots[selected_day - 1])
    zone_colors = zone_df.replace({
        'F': '🟦 F',
        'L': '🟩 L',
        'O': '🟥 O',
        '': '⬜️'
    })
    col1.dataframe(zone_colors, use_container_width=True)

    col2.subheader("\U0001F5FA️ Business Distribution Map")
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

    st.subheader(f"\U0001F4CA Market Share and Churn on Day {selected_day}")
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
    st.markdown("**\U0001F4E6 Market Share:**")
    st.bar_chart(pd.DataFrame(day_stats, index=["Customers"]))

    st.markdown("**\U0001F525 Churn:**")
    st.bar_chart(pd.DataFrame(churn_stats, index=["Churned"]))
