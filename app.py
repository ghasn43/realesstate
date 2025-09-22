import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Page Setup ---
st.set_page_config(
    page_title="Experts Group Building Cost Estimator",
    page_icon="🏗",
    layout="wide"
)


# --- Currency Conversion Rates ---
conversion_rates = {
    "SAR": 1,
    "AED": 0.98,   # 1 SAR ≈ 0.98 AED
    "USD": 0.27    # 1 SAR ≈ 0.27 USD
}


# --- Title ---
#st.title("🏗 Saudi Arabia Building Cost Estimator (with Finishing)")
st.title("🏗 Experts Group Building Cost Estimator")
st.markdown("### Powered by Experts Group — Smart Cost Planning for Riyadh, Jeddah, Dammam, and Dubai")

st.write("Now includes Structural + Finishing + MEP + Labor + Equipment")

# --- Load Data ---
df = pd.read_csv("realistic_materials.csv")
df["Location"] = df["Location"].str.strip()

#st.write("DEBUG - Locations:", df["Location"].unique())

df.columns = df.columns.str.strip()

# --- User Inputs ---
st.sidebar.header("Enter Project Details")

location = st.sidebar.selectbox("📍 Location", df["Location"].unique())
#location = st.sidebar.selectbox("📍 Location", ["Riyadh", "Jeddah", "Dammam"])
year = st.sidebar.slider("📅 Year", 2023, 2025, 2025)
building_type = st.sidebar.selectbox("🏢 Type", ["Residential", "Commercial"])
area = st.sidebar.number_input("📐 Building Area (m²)", min_value=500, max_value=10000, value=3000)
floors = st.sidebar.slider("🏗 Number of Floors", 1, 10, 4)

# ✅ NEW finishing quality radio button
finishing_quality = st.sidebar.radio("⭐ Finishing Quality", ["Standard", "Luxury"])

# --- Load correct dataset based on choice ---
if finishing_quality == "Standard":
    df = pd.read_csv("realistic_materials.csv")
else:
    df = pd.read_csv("realistic_materials_luxury.csv")

df.columns = df.columns.str.strip()
currency = st.sidebar.selectbox("💱 Display Currency", ["SAR", "AED", "USD"])


# --- Get prices for chosen year/location ---
row = df[(df["Year"] == year) & (df["Location"] == location)].iloc[0]

cement_price = row["Cement (SAR/ton)"]
steel_price = row["Steel (SAR/ton)"]
concrete_price = row["Concrete (SAR/m3)"]
blocks_price = row["Blocks (SAR/1000)"]
tiles_price = row["Tiles (SAR/m2)"]
paint_price = row["Paint (SAR/m2)"]
glass_price = row["Glass (SAR/m2)"]
wood_price = row["Wood (SAR/m2)"]
labor_price = row["Labor (SAR/hour)"]
equipment_price = row["Equipment (SAR/day)"]

# --- Estimate quantities (very simplified for demo) ---
cement_qty = area * floors * 0.15    # tons
steel_qty = area * floors * 0.05     # tons
concrete_qty = area * floors * 0.5   # m³
blocks_qty = area * floors * 1.2     # 1000 blocks
tiles_qty = area                     # m²
paint_qty = area * 2                 # m² (walls & ceilings)
glass_qty = area * 0.15              # m²
wood_qty = area * 0.12               # m²
labor_hours = area * floors * 2      # hours
equipment_days = floors * 5          # days

# --- Calculate costs ---
cement_cost = cement_qty * cement_price
steel_cost = steel_qty * steel_price
concrete_cost = concrete_qty * concrete_price
blocks_cost = blocks_qty * blocks_price
tiles_cost = tiles_qty * tiles_price
paint_cost = paint_qty * paint_price
glass_cost = glass_qty * glass_price
wood_cost = wood_qty * wood_price
labor_cost = labor_hours * labor_price
equipment_cost = equipment_days * equipment_price

# --- Group categories ---
structural_cost = cement_cost + steel_cost + concrete_cost + blocks_cost
finishing_cost = tiles_cost + paint_cost + glass_cost + wood_cost
mep_cost = 0.15 * (structural_cost + finishing_cost)  # placeholder % for MEP
other_cost = 0.05 * (structural_cost + finishing_cost)  # contingency

estimated_cost = structural_cost + finishing_cost + mep_cost + labor_cost + equipment_cost + other_cost
cost_per_m2 = estimated_cost / area

# --- Display Results ---
#st.subheader("📊 Estimation Results")
#st.success(f"💰 Estimated Total Cost: {estimated_cost:,.0f} SAR")
#st.write(f"📐 Cost per m²: {cost_per_m2:,.0f} SAR")

# --- Currency Conversion ---
converted_cost = estimated_cost * conversion_rates[currency]
converted_cost_per_m2 = cost_per_m2 * conversion_rates[currency]

# --- Display Results ---
st.subheader("📊 Estimation Results")
st.success(f"💰 Estimated Total Cost: {converted_cost:,.0f} {currency}")
st.write(f"📐 Cost per m²: {converted_cost_per_m2:,.0f} {currency}")



# --- Cost Breakdown Bar Chart ---
# Define cost categories
sizes = [structural_cost, finishing_cost, mep_cost, labor_cost, equipment_cost, other_cost]
labels = ["Structural", "Finishing", "MEP", "Labor", "Equipment", "Other"]

# Define colors (consistent palette)
colors = ["#66b3ff", "#99ff99", "#ffcc99", "#ff9999", "#c2c2f0", "#f0e68c"]

# Convert to selected currency
converted_sizes = [c * conversion_rates[currency] for c in sizes]

# Plot bar chart
fig_bar, ax_bar = plt.subplots(figsize=(4, 2))  # compact
bars = ax_bar.bar(labels, converted_sizes, color=colors)

# Titles and labels
ax_bar.set_ylabel(f"Cost ({currency})", fontsize=7)
ax_bar.set_title("Cost Breakdown by Category", fontsize=9, pad=5)
ax_bar.tick_params(axis='x', labelrotation=30, labelsize=7)
ax_bar.tick_params(axis='y', labelsize=7)

# Add values on top of bars
for bar, value in zip(bars, converted_sizes):
    ax_bar.text(
        bar.get_x() + bar.get_width()/2, value,
        f"{value:,.0f}", ha='center', va='bottom', fontsize=6
    )

st.pyplot(fig_bar)
