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

#Simulation coordinates(Map)
# Soweto map center (adjust if you have better coordinates)
map_center = [-26.267, 27.858]
m = folium.Map(location=map_center, zoom_start=13)

# Simulate 10 business locations (with random lat/lon offsets)
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

# Render map in Streamlit
st.title("🗺️ Soweto Subsistence Retail Map")
st.markdown("**Markers show simulated business types:** F = First-to-Market, L = Loyalty-Based, O = Opposition")
st_folium(m, width=700, height=500)



