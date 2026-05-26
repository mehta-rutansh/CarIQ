import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go
from sklearn.preprocessing import LabelEncoder
 
st.set_page_config(
    page_title="CarIQ",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)
 
# Load data
df = pd.read_csv('cariq_display.xls')
 
# Load model
with open('selling_price_prediction.pkl', 'rb') as f:
    model = pickle.load(f)
 
# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
 
def calculate_dynamic_score(row, w_safety, w_performance, w_reliability, w_maintenance, w_price):
    cap_safety = 5
    cap_performance = 227
    cap_reliability = 548000
    cap_maintenance = 600000
    cap_price = 2500000
 
    safety_score      = (min(row['gncap_rating'], cap_safety) / cap_safety) * w_safety
    performance_score = (min(row['max_power'], cap_performance) / cap_performance) * w_performance
    reliability_score = (1 - min(row['wear_score'], cap_reliability) / cap_reliability) * w_reliability
    maintenance_score = (1 - min(row['final_maintenance_cost'], cap_maintenance) / cap_maintenance) * w_maintenance
    price_score       = (1 - min(row['selling_price'], cap_price) / cap_price) * w_price
 
    return round(safety_score + performance_score + reliability_score + maintenance_score + price_score, 2)
 
 
def create_radar_chart(car_row, w_safety, w_performance, w_reliability, w_maintenance, w_price):
    safety      = round((min(car_row['gncap_rating'], 5) / 5) * w_safety, 1)
    performance = round((min(car_row['max_power'], 227) / 227) * w_performance, 1)
    reliability = round((1 - min(car_row['wear_score'], 548000) / 548000) * w_reliability, 1)
    maintenance = round((1 - min(car_row['final_maintenance_cost'], 600000) / 600000) * w_maintenance, 1)
    value       = round((1 - min(car_row['selling_price'], 2500000) / 2500000) * w_price, 1)
 
    categories = ['Safety', 'Performance', 'Reliability', 'Maintenance', 'Value']
    scores     = [safety, performance, reliability, maintenance, value]
 
    fig = go.Figure(data=go.Scatterpolar(
        r=scores + [scores[0]],
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(230, 57, 70, 0.2)',
        line=dict(color='#E63946', width=2),
        marker=dict(size=6)
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(
            visible=True,
            range=[0, max(w_safety, w_performance, w_reliability, w_maintenance, w_price)]
        )),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=40, b=40),
        height=300
    )
    return fig, scores, categories
 
 
def why_this_car(car):
    reasons = []
 
    if car['gncap_rating'] >= 4:
        reasons.append(f"✅ Excellent safety — {car['gncap_rating']} star GNCAP rating")
    elif car['gncap_rating'] >= 2:
        reasons.append(f"⚠️ Moderate safety — {car['gncap_rating']} star GNCAP rating")
    else:
        reasons.append("⚠️ Safety not tested — verify before buying")
 
    if car['km_driven'] < 50000:
        reasons.append(f"✅ Low mileage — only {car['km_driven']:,.0f} km driven")
    elif car['km_driven'] < 100000:
        reasons.append(f"✅ Moderate mileage — {car['km_driven']:,.0f} km driven")
    else:
        reasons.append(f"⚠️ High mileage — {car['km_driven']:,.0f} km driven")
 
    if car['vehicle_age'] <= 3:
        reasons.append(f"✅ Relatively new — only {car['vehicle_age']} years old")
    elif car['vehicle_age'] <= 7:
        reasons.append(f"✅ Well maintained age — {car['vehicle_age']} years old")
    else:
        reasons.append(f"⚠️ Older car — {car['vehicle_age']} years old, inspect carefully")
 
    if car['final_maintenance_cost'] < 200000:
        reasons.append(f"✅ Low maintenance — ₹{car['final_maintenance_cost']:,.0f} over 5 years")
    elif car['final_maintenance_cost'] < 400000:
        reasons.append(f"✅ Moderate maintenance — ₹{car['final_maintenance_cost']:,.0f} over 5 years")
    else:
        reasons.append(f"⚠️ High maintenance — ₹{car['final_maintenance_cost']:,.0f} over 5 years")
 
    if car['selling_price'] < 500000:
        reasons.append(f"✅ Budget friendly — ₹{car['selling_price']:,.0f}")
    elif car['selling_price'] < 1200000:
        reasons.append(f"✅ Reasonably priced — ₹{car['selling_price']:,.0f}")
    else:
        reasons.append(f"ℹ️ Premium pricing — ₹{car['selling_price']:,.0f}")
 
    return reasons
 
 
# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
 
st.sidebar.title("🔍 Find Your Car")
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚖️ What Matters Most To You?")
 
w_safety      = st.sidebar.slider("Safety", 0, 40, 20)
w_performance = st.sidebar.slider("Performance", 0, 40, 20)
w_reliability = st.sidebar.slider("Reliability", 0, 40, 25)
w_maintenance = st.sidebar.slider("Maintenance Cost", 0, 40, 20)
w_price       = st.sidebar.slider("Value for Money", 0, 40, 15)
 
total_weight = w_safety + w_performance + w_reliability + w_maintenance + w_price
 
st.sidebar.markdown("---")
if total_weight == 100:
    st.sidebar.success(f"✅ Total: {total_weight}/100")
else:
    st.sidebar.info(f"ℹ️ Total: {total_weight}/100 — Auto-adjusting to 100")
    w_safety      = round((w_safety / total_weight) * 100)
    w_performance = round((w_performance / total_weight) * 100)
    w_reliability = round((w_reliability / total_weight) * 100)
    w_maintenance = round((w_maintenance / total_weight) * 100)
    w_price       = 100 - w_safety - w_performance - w_reliability - w_maintenance
 
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Filters")
 
budget_min, budget_max = st.sidebar.slider(
    "Budget Range (₹)",
    min_value=40000, max_value=2500000,
    value=(300000, 1200000), step=10000
)
 
fuel = st.sidebar.multiselect(
    "Fuel Type",
    options=df['fuel_type'].unique().tolist(),
    default=['Petrol']
)
 
transmission = st.sidebar.multiselect(
    "Transmission",
    options=df['transmission_type'].unique().tolist(),
    default=['Manual']
)
 
seats = st.sidebar.multiselect(
    "Seats",
    options=sorted(df['seats'].unique().tolist()),
    default=[5]
)
 
 
# ─────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────
 
st.title("🚗 CarIQ")
st.subheader("Find your perfect used car in seconds")
st.markdown("---")
 
 
# ─────────────────────────────────────────────
# PAGE 1 — CAR FINDER
# ─────────────────────────────────────────────
 
st.markdown("## 🏆 Top Cars For You")
 
filtered = df[
    (df['selling_price'] >= budget_min) &
    (df['selling_price'] <= budget_max) &
    (df['fuel_type'].isin(fuel)) &
    (df['transmission_type'].isin(transmission)) &
    (df['seats'].isin(seats))
]
 
if len(filtered) == 0:
    st.warning("No cars found matching your criteria. Try adjusting your filters.")
else:
    filtered = filtered.copy()
    filtered['dynamic_score'] = filtered.apply(
        lambda row: calculate_dynamic_score(
            row, w_safety, w_performance, w_reliability, w_maintenance, w_price
        ), axis=1
    )
 
    top5 = filtered.sort_values('dynamic_score', ascending=False).head(5)
 
    st.write(f"Found **{len(filtered)}** cars matching your criteria. Showing top 5:")
 
    st.dataframe(
        top5[['brand', 'model', 'vehicle_age', 'km_driven',
              'fuel_type', 'selling_price', 'dynamic_score']]
        .rename(columns={
            'brand':         'Brand',
            'model':         'Model',
            'vehicle_age':   'Age (Yrs)',
            'km_driven':     'KM Driven',
            'fuel_type':     'Fuel',
            'selling_price': 'Price (₹)',
            'dynamic_score': 'CarIQ Score'
        }),
        hide_index=True
    )
 
    st.markdown("---")
    st.markdown("### 🎯 Individual Car Analysis")
    st.write("Click on a car below to see its full breakdown:")
 
    for i, (_, car) in enumerate(top5.iterrows()):
        with st.expander(f"#{i+1} — {car['brand']} {car['model']} | Score: {car['dynamic_score']}/100 | ₹{car['selling_price']:,.0f}"):
 
            col1, col2 = st.columns([1, 1])
 
            with col1:
                fig, scores, categories = create_radar_chart(
                    car, w_safety, w_performance, w_reliability, w_maintenance, w_price
                )
                st.plotly_chart(fig, use_container_width=True, key=f"radar_{i}")
 
            with col2:
                st.markdown("**📊 Score Breakdown**")
                for cat, score, weight in zip(
                    categories, scores,
                    [w_safety, w_performance, w_reliability, w_maintenance, w_price]
                ):
                    st.write(f"{cat}: **{score}/{weight}**")
 
                st.markdown("---")
                st.markdown("**🚘 Car Details**")
                st.write(f"🗓️ Age: {car['vehicle_age']} years")
                st.write(f"🛣️ KM Driven: {car['km_driven']:,.0f} km")
                st.write(f"⛽ Fuel: {car['fuel_type']}")
                st.write(f"⚙️ Transmission: {car['transmission_type']}")
                st.write(f"🔧 Engine: {car['engine']} cc")
                st.write(f"💪 Power: {car['max_power']} bhp")
                st.write(f"🛡️ GNCAP Rating: {car['gncap_rating']} ⭐")
                st.write(f"💰 Maintenance (5yr): ₹{car['final_maintenance_cost']:,.0f}")
 
                if car['gncap_tested'] == 0:
                    st.warning("⚠️ This car has not been GNCAP safety tested")
 
            st.markdown("---")
            st.markdown("**💡 Why This Car?**")
            for reason in why_this_car(car):
                st.write(reason)
 
 
# ─────────────────────────────────────────────
# PAGE 2 — PRICE CHECKER
# ─────────────────────────────────────────────
 
st.markdown("---")
st.markdown("## 💰 Price Checker")
st.write("Enter details of a car you found on OLX, CarDekho or any third party — find out if it's fairly priced.")
 
col1, col2 = st.columns(2)
 
with col1:
    pc_brand        = st.selectbox("Brand", sorted(df['brand'].unique().tolist()))
    pc_model        = st.selectbox("Model", sorted(df[df['brand'] == pc_brand]['model'].unique().tolist()))
    pc_fuel         = st.selectbox("Fuel Type", df['fuel_type'].unique().tolist())
    pc_transmission = st.selectbox("Transmission", df['transmission_type'].unique().tolist())
    pc_seller       = st.selectbox("Seller Type", df['seller_type'].unique().tolist())
 
with col2:
    pc_age          = st.number_input("Vehicle Age (Years)", min_value=0, max_value=30, value=5)
    pc_km           = st.number_input("KM Driven", min_value=100, max_value=1500000, value=50000)
    pc_mileage      = st.number_input("Mileage (kmpl)", min_value=4.0, max_value=35.0, value=18.0)
    pc_engine       = st.number_input("Engine (CC)", min_value=500, max_value=6000, value=1200)
    pc_power        = st.number_input("Max Power (bhp)", min_value=30.0, max_value=500.0, value=80.0)
    pc_seats        = st.number_input("Seats", min_value=2, max_value=9, value=5)
    pc_asking_price = st.number_input("Seller's Asking Price (₹)", min_value=40000, max_value=10000000, value=500000)
 
if st.button("🔍 Check Price"):
 
    input_data = pd.DataFrame({
        'brand':                        [pc_brand],
        'model':                        [pc_model],
        'vehicle_age':                  [pc_age],
        'km_driven':                    [pc_km],
        'mileage':                      [pc_mileage],
        'engine':                       [pc_engine],
        'max_power':                    [pc_power],
        'seats':                        [pc_seats],
        'airbags':                      [0],
        'gncap_rating':                 [0],
        'gncap_tested':                 [0],
        'final_maintenance_cost':       [0],
        'wear_score':                   [pc_km + (pc_age * 12000)],
        'seller_type_Dealer':           [1 if pc_seller == 'Dealer' else 0],
        'seller_type_Individual':       [1 if pc_seller == 'Individual' else 0],
        'seller_type_Trustmark Dealer': [1 if pc_seller == 'Trustmark Dealer' else 0],
        'fuel_type_CNG':                [1 if pc_fuel == 'CNG' else 0],
        'fuel_type_Diesel':             [1 if pc_fuel == 'Diesel' else 0],
        'fuel_type_Electric':           [1 if pc_fuel == 'Electric' else 0],
        'fuel_type_LPG':                [1 if pc_fuel == 'LPG' else 0],
        'fuel_type_Petrol':             [1 if pc_fuel == 'Petrol' else 0],
        'transmission_type_Automatic':  [1 if pc_transmission == 'Automatic' else 0],
        'transmission_type_Manual':     [1 if pc_transmission == 'Manual' else 0],
    })
 
    le = LabelEncoder()
    le.fit(df['brand'])
    input_data['brand'] = le.transform([pc_brand])
    le.fit(df['model'])
    input_data['model'] = le.transform([pc_model])
 
    predicted_price = model.predict(input_data)[0]
    difference      = pc_asking_price - predicted_price
 
    st.markdown("### 🎯 Price Analysis")
 
    c1, c2, c3 = st.columns(3)
    c1.metric("Fair Market Price", f"₹{predicted_price:,.0f}")
    c2.metric("Asking Price",      f"₹{pc_asking_price:,.0f}")
 
    if difference > 0:
        c3.metric("Verdict", f"Overpriced by ₹{difference:,.0f}", delta=f"-₹{difference:,.0f}")
        st.error(f"⚠️ Seller is asking ₹{difference:,.0f} MORE than fair market price. Negotiate!")
    elif difference < 0:
        c3.metric("Verdict", f"Good Deal by ₹{abs(difference):,.0f}", delta=f"+₹{abs(difference):,.0f}")
        st.success(f"✅ This is a GOOD DEAL. Car is priced ₹{abs(difference):,.0f} BELOW market value!")
    else:
        c3.metric("Verdict", "Fairly Priced")
        st.info("✅ This car is fairly priced at market value.")
 