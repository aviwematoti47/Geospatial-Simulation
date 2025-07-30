# ===================== Imports =========================
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

# ===================== Sidebar Controls =========================
st.sidebar.title("📅 Simulation Controls")
total_days = st.sidebar.slider("Select number of days to simulate", 30, 365, 180)
run_simulation = st.sidebar.button("▶️ Run Simulation")

# ===================== Interactive Soweto Map =========================
st.title("🏪 Soweto Retail Business Simulation")
st.markdown("This app models business competition in Soweto's subsistence market using reinforcement learning strategies.")

map_center = [-26.267, 27.858]
m = folium.Map(location=map_center, zoom_start=13)

# Simulate business markers (static for now)
np.random.seed(42)
business_types = ['F', 'L', 'O']
for i in range(10):
    lat_offset = np.random.uniform(-0.01, 0.01)
    lon_offset = np.random.uniform(-0.01, 0.01)
    b_type = np.random.choice(business_types)
    folium.Marker(
        location=[map_center[0] + lat_offset, map_center[1] + lon_offset],
        popup=f"Business Type: {b_type}",
        icon=folium.Icon(color='blue' if b_type == 'F' else 'green' if b_type == 'L' else 'red')
    ).add_to(m)

# Display the map
st.subheader("🗺️ Soweto Market Map")
st.markdown("F = First-to-Market, L = Loyalty-Based, O = Opposition")
st_folium(m, width=700, height=500)

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

# ===================== Simulation Block =========================
if run_simulation:
    st.subheader("📈 Business Market Share Over Time")

    days = list(range(1, total_days + 1))
    first_market, loyalty_based, opposition = [], [], []
    churn_f, churn_l, churn_o = [], [], []

    f = 100  # Initial customers for First-to-Market
    l = 0
    o = 0

    for day in days:
        # First-to-Market
        f_loss = f * 0.001
        f -= f_loss
        churn_f.append(f_loss)

        # Loyalty-Based
        if day > 30:
            l += 1.5
            l_loss = 0.05 * l if day > 90 else 0.01 * l
            l -= l_loss
            churn_l.append(l_loss)
        else:
            churn_l.append(0)

        # Opposition
        if day > 90:
            o_gain = 2
            o += o_gain
            f -= 1
            l -= 1
            churn_o.append(0.5)
        else:
            churn_o.append(0)

        # Track totals
        first_market.append(max(f, 0))
        loyalty_based.append(max(l, 0))
        opposition.append(max(o, 0))

    # Build DataFrames
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

    # ===== Charts =====
    st.markdown("#### 📊 Market Share Trends")
    st.line_chart(df_trends.set_index("Day"))

    st.markdown("#### 📉 Churn Rates Per Business Type")
    st.line_chart(df_churn.set_index("Day"))

    # ===== Export =====
    df_trends.to_csv("simulation_output.csv", index=False)
    df_churn.to_csv("churn_output.csv", index=False)
    st.success("Simulation complete. CSVs exported for Looker Studio.")
