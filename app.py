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

# ===================== Step 1: Create 5x5 Zone Network using networkx =========================
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
business_types = ['F', 'L', 'O', '']
for node in G.nodes:
    G.nodes[node]['business'] = random.choice(business_types)

# Optional networkx visualization (can be commented out in Streamlit)
fig, ax = plt.subplots(figsize=(6, 5))
pos = nx.get_node_attributes(G, 'pos')
labels = nx.get_node_attributes(G, 'business')
color_map = []
for node in G:
    b_type = G.nodes[node]['business']
    if b_type == 'F':
        color_map.append('blue')
    elif b_type == 'L':
        color_map.append('green')
    elif b_type == 'O':
        color_map.append('red')
    else:
        color_map.append('lightgray')
nx.draw(G, pos, with_labels=True, node_color=color_map, node_size=800, edge_color='gray', ax=ax)
nx.draw_networkx_labels(G, pos, labels=labels, font_color='white', font_weight='bold', ax=ax)
plt.title("5x5 Zone Grid as Business Network")
plt.axis("off")
st.pyplot(fig)

# ===================== Simulation Logic =========================
if run_simulation:
    days = list(range(1, total_days + 1))
    first_market, loyalty_based, opposition = [], [], []
    churn_f, churn_l, churn_o = [], [], []

    f, l, o = 100, 0, 0
    zone_snapshots = []

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
    state.df_trends.to_csv("simulation_output.csv", index=False)
    state.df_churn.to_csv("churn_output.csv", index=False)
    st.success("✅ Simulation complete. Data exported.")
