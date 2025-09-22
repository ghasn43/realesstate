import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# --- Page Setup ---
st.set_page_config(
    page_title="Experts Group Building Cost Estimator",
    page_icon="🏗",
    layout="wide"
)

st.title("🏗 Experts Group Building Cost Estimator")
st.markdown("### Powered by Experts Group — Smart Cost Planning for Riyadh, Jeddah, Dammam, and Dubai")

# --- Load Data (placeholder CSVs for consistency) ---
df = pd.read_csv("realistic_materials.csv")
df_luxury = pd.read_csv("realistic_materials_luxury.csv")
df["Location"] = df["Location"].str.strip()
df_luxury["Location"] = df_luxury["Location"].str.strip()

# --- Currency Conversion Rates ---
conversion_rates = {
    "SAR": 1,
    "AED": 0.98,   # 1 SAR ≈ 0.98 AED
    "USD": 0.27    # 1 SAR ≈ 0.27 USD
}

# --- Default Benchmarks & Multipliers ---
defaults = {
    "residential": 1800,
    "commercial": 2500,
    "riyadh_mult": 1.0,
    "jeddah_mult": 1.05,
    "dammam_mult": 0.95,
    "dubai_mult": 1.3
}

# --- Reset Flag ---
if "reset_triggered" not in st.session_state:
    st.session_state.reset_triggered = False

if st.sidebar.button("🔄 Reset to Default"):
    for k, v in defaults.items():
        st.session_state[k] = v
    st.session_state.reset_triggered = False
    st.rerun()

# --- Initialize Session State ---
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- Sidebar Inputs ---
st.sidebar.header("Project Inputs")
location = st.sidebar.selectbox("📍 Location", ["Riyadh", "Jeddah", "Dammam", "Dubai"])
year = st.sidebar.selectbox("📅 Year", df["Year"].unique())
building_type = st.sidebar.selectbox("🏠 Building Type", ["Residential", "Commercial"])
area = st.sidebar.number_input("📐 Total Area (m²)", min_value=100, max_value=20000, value=3000, step=100)
floors = st.sidebar.number_input("🏢 Number of Floors", min_value=1, max_value=10, value=2)
finishing_quality = st.sidebar.radio("🎨 Finishing Quality", ["Standard", "Luxury"])
currency = st.sidebar.selectbox("💱 Display Currency", ["SAR", "AED", "USD"])

# --- Configurable Benchmarks ---
st.sidebar.markdown("### ⚙️ Cost Benchmarks (SAR/m²)")
st.sidebar.number_input(
    "Residential Base Cost",
    min_value=500, max_value=5000,
    value=st.session_state["residential"],
    step=50,
    key="residential"
)
st.sidebar.number_input(
    "Commercial Base Cost",
    min_value=500, max_value=7000,
    value=st.session_state["commercial"],
    step=50,
    key="commercial"
)

# --- Configurable City Multipliers ---
st.sidebar.markdown("### 🌍 City Multipliers")
st.sidebar.number_input("Riyadh", 0.5, 2.0, value=st.session_state["riyadh_mult"], step=0.05, key="riyadh_mult")
st.sidebar.number_input("Jeddah", 0.5, 2.0, value=st.session_state["jeddah_mult"], step=0.05, key="jeddah_mult")
st.sidebar.number_input("Dammam", 0.5, 2.0, value=st.session_state["dammam_mult"], step=0.05, key="dammam_mult")
st.sidebar.number_input("Dubai",  0.5, 2.0, value=st.session_state["dubai_mult"],  step=0.05, key="dubai_mult")

# --- Use the values ---
base_residential = st.session_state["residential"]
base_commercial = st.session_state["commercial"]

city_factor = {
    "Riyadh": st.session_state["riyadh_mult"],
    "Jeddah": st.session_state["jeddah_mult"],
    "Dammam": st.session_state["dammam_mult"],
    "Dubai":  st.session_state["dubai_mult"]
}[location]

# --- Benchmark-Based Cost Calculation ---
base_costs = {
    "Residential": base_residential,
    "Commercial": base_commercial
}

# Apply finishing adjustment
if finishing_quality == "Luxury":
    if building_type == "Residential":
        base_costs["Residential"] *= 1.4   # +40% for luxury villas
    else:
        base_costs["Commercial"] *= 1.3    # +30% for luxury offices

# Final estimated cost
estimated_cost = base_costs[building_type] * area * city_factor
cost_per_m2 = estimated_cost / area

# Breakdown (approximate % split)
structural_cost = estimated_cost * 0.5
finishing_cost  = estimated_cost * 0.3
mep_cost        = estimated_cost * 0.1
labor_cost      = estimated_cost * 0.07
equipment_cost  = estimated_cost * 0.02
other_cost      = estimated_cost * 0.01

# --- Convert to Selected Currency ---
converted_cost = estimated_cost * conversion_rates[currency]
converted_cost_per_m2 = cost_per_m2 * conversion_rates[currency]

# --- Display Results ---
st.subheader("📊 Estimation Results")
st.success(f"💰 Estimated Total Cost: {converted_cost:,.0f} {currency}")
st.write(f"📐 Cost per m²: {converted_cost_per_m2:,.0f} {currency}")

# --- Project Summary ---
report_text = f"""
Experts Group – Building Cost Estimator

📑 Project Summary
------------------------
Location: {location}
Year: {year}
Building Type: {building_type}
Area: {area:,} m²
Floors: {floors}
Finishing Quality: {finishing_quality}
Currency: {currency}

💰 Results
------------------------
Estimated Total Cost: {converted_cost:,.0f} {currency}
Cost per m²: {converted_cost_per_m2:,.0f} {currency}
"""

st.subheader("📑 Project Summary")
st.text(report_text)

# --- Download as TXT ---
st.download_button(
    label="📥 Download Report (TXT)",
    data=report_text,
    file_name="building_cost_report.txt",
    mime="text/plain"
)

# --- Download as PDF ---
pdf_buffer = BytesIO()
c = canvas.Canvas(pdf_buffer, pagesize=letter)
text = c.beginText(50, 750)
for line in report_text.split("\n"):
    text.textLine(line)
c.drawText(text)
c.save()
pdf_buffer.seek(0)

st.download_button(
    label="📥 Download Report (PDF)",
    data=pdf_buffer,
    file_name="building_cost_report.pdf",
    mime="application/pdf"
)

# --- Download as Excel ---
df_report = pd.DataFrame({
    "Parameter": ["Location", "Year", "Building Type", "Area (m²)", "Floors", "Finishing Quality", "Currency", "Total Cost", "Cost per m²"],
    "Value": [location, year, building_type, area, floors, finishing_quality, currency, f"{converted_cost:,.0f}", f"{converted_cost_per_m2:,.0f}"]
})

excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    df_report.to_excel(writer, index=False, sheet_name="Report")
excel_buffer.seek(0)

st.download_button(
    label="📥 Download Report (Excel)",
    data=excel_buffer,
    file_name="building_cost_report.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# --- Bar Chart for Cost Breakdown ---
sizes = [structural_cost, finishing_cost, mep_cost, labor_cost, equipment_cost, other_cost]
labels = ["Structural", "Finishing", "MEP", "Labor", "Equipment", "Other"]
colors = ["#66b3ff", "#99ff99", "#ffcc99", "#ff9999", "#c2c2f0", "#f0e68c"]
converted_sizes = [c * conversion_rates[currency] for c in sizes]

fig_bar, ax_bar = plt.subplots(figsize=(4, 2))  # compact chart
bars = ax_bar.bar(labels, converted_sizes, color=colors)

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


