import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

# Load simulation data or run from scratch
st.title("Soweto Retail Market RL Simulation")

st.sidebar.header("Simulation Controls")
days = st.sidebar.slider("Simulate Days", min_value=1, max_value=365, value=30)
start_sim = st.sidebar.button("Run Simulation")

# Placeholder business states
if start_sim:
    st.subheader("Simulating Business Dynamics...")
    
    # Example: Initialize 3 business types
    results = []
    for day in range(1, days+1):
        results.append({
            'Day': day,
            'First_to_Market': np.random.randint(50, 200),
            'Loyalty_Based': np.random.randint(30, 150),
            'Opposition': np.random.randint(10, 100),
        })
    
    df_sim = pd.DataFrame(results)
    
    st.line_chart(df_sim.set_index('Day'))

    st.subheader("Business Market Share")
    last_day = df_sim.iloc[-1][['First_to_Market', 'Loyalty_Based', 'Opposition']]
    st.bar_chart(last_day)

    st.dataframe(df_sim)


# Simulate 5x5 zone map and color-code zones
zones = np.random.choice(['F', 'L', 'O'], size=(5,5))
st.write("Zone Map (F=First, L=Loyalty, O=Opposition)")
st.dataframe(pd.DataFrame(zones))

#Simulation coordinates
# Soweto center
m = folium.Map(location=[-26.267, 27.858], zoom_start=12)

# Add store locations or zones
folium.Marker(location=[-26.267, 27.858], popup="F").add_to(m)

# Render in Streamlit
st_folium(m, width=700, height=500)



