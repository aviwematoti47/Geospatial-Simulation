import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import folium
from streamlit_folium import st_folium

# Load simulation data or run from scratch
st.title("Soweto Retail Market RL Simulation")

# Sidebar control
st.sidebar.title("📅 Simulation Controls")
total_days = st.sidebar.slider("Select number of days to simulate", 30, 365, 180)
run_simulation = st.sidebar.button("▶️ Run Simulation")

# Placeholder business states
if run_simulation:
    st.subheader("📈 Business Market Share Over Time")

    # Initialize business counts
    days = list(range(1, total_days + 1))
    first_market = []
    loyalty_based = []
    opposition = []

    f = 100  # First-to-market starts with 100 customers
    l = 0
    o = 0

    for day in days:
        # First-to-Market: loses 0.1% daily
        f_loss = f * 0.001
        f -= f_loss

        # Loyalty-Based: enters after day 30, grows slowly
        if day > 30:
            l += 1.5  # stable growth

        # Opposition: enters after day 90, gains by taking from others
        if day > 90:
            o += 2
            f -= 1
            l -= 1

        first_market.append(max(f, 0))
        loyalty_based.append(max(l, 0))
        opposition.append(max(o, 0))

    # Build results dataframe
    df_trends = pd.DataFrame({
        "Day": days,
        "First-to-Market": first_market,
        "Loyalty-Based": loyalty_based,
        "Opposition": opposition
    })

    st.line_chart(df_trends.set_index("Day"))

    # Export for Looker Studio
    df_trends.to_csv("simulation_output.csv", index=False)

    st.success("Simulation complete. Data exported.")

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

---

### 🧠 Strategy Notes
- Businesses adapt based on past performance.
- Decisions can be made using rules or RL algorithms.
- This simulation uses fixed rules (for simplicity), but can be upgraded to Q-learning or PPO.
""")

# Add churn tracking
churn_f, churn_l, churn_o = [], [], []
for day in day:
    # First-to-Market churn
    f_loss = f * 0.001
    f -= f_loss
    churn_f.append(f_loss)

    # Loyalty-Based churn (enters after day 30)
    if day > 30:
        l += 1.5
        l_loss = 0.05 * l if day > 90 else 0.01 * l  # higher churn vs. opposition
        l -= l_loss
        churn_l.append(l_loss)
    else:
        churn_l.append(0)

    # Opposition churn (minimal)
    if day > 90:
        o_gain = 2
        o += o_gain
        f -= 1
        l -= 1
        churn_o.append(0.5)  # minimal churn
    else:
        churn_o.append(0)

    # Append updated values
    first_market.append(max(f, 0))
    loyalty_based.append(max(l, 0))
    opposition.append(max(o, 0))

# Churn Dataframe
df_churn = pd.DataFrame({
    "Day": days,
    "First-to-Market": churn_f,
    "Loyalty-Based": churn_l,
    "Opposition": churn_o
})

st.subheader("📉 Churn Rates Over Time")
st.markdown("This chart shows how many customers each business type loses daily.")
st.line_chart(df_churn.set_index("Day"))

#Export for Dashboard in LookerStudio
df_churn.to_csv("churn_output.csv", index=False)


