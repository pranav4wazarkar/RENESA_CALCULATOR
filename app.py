import streamlit as st
import pandas as pd
import io
import math
from fpdf import FPDF

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Seller Command Center", layout="wide", page_icon="📈")

# --- CORE LOGIC (MARCH 2026) ---
def calculate_2026_economics(platform, price, cogs, region="National"):
    """March 2, 2026: Amazon/Flipkart 0% referral/commission < 1000 INR."""
    gst_rate, tcs, tds = 0.18, 0.005, 0.001
    
    if platform == "Amazon":
        referral = 0 if price <= 1000 else (price * 0.12)
        closing = 5 if price <= 250 else 30 if price <= 1000 else 60
        shipping = 45 if region == "Local" else 75
        total_fees = referral + closing + shipping
        return_loss = closing + shipping + (price * 0.02)
        
    elif platform == "Flipkart":
        commission = 0 if price <= 1000 else (price * 0.08)
        fixed = 15 if price <= 500 else 35
        shipping = 40 if region == "Local" else 65
        total_fees = commission + fixed + shipping
        return_loss = (shipping * 1.2) + fixed
    else: # Swiggy / Quick Commerce
        total_fees = (price * 0.22) + 12 
        return_loss = total_fees * 0.6
        
    fee_gst = total_fees * gst_rate
    payout = price - (total_fees + fee_gst + (price * tcs) + (price * tds))
    profit = payout - cogs
    
    total_loss_per_return = return_loss + (return_loss * gst_rate) + 25 
    recovery_ratio = total_loss_per_return / profit if profit > 0 else 999
    
    return {
        "payout": round(payout, 2), "profit": round(profit, 2),
        "margin": round((profit/price)*100, 2) if price > 0 else 0,
        "loss": round(total_loss_per_return, 2), "recovery": round(recovery_ratio, 1),
        "tax_credit": round(fee_gst + (price * tcs) + (price * tds), 2)
    }

# --- PDF GENERATOR ---
def generate_pdf_report(data, plat, price, cogs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 15, f"2026 Profit Report: {plat}", ln=True, align='C')
    pdf.set_font("Helvetica", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Selling Price: Rs. {price} | Landing Cost: Rs. {cogs}", ln=True)
    pdf.cell(0, 10, f"Net Bank Payout: Rs. {data['payout']}", ln=True)
    pdf.cell(0, 10, f"Net Profit: Rs. {data['profit']} ({data['margin']}%)", ln=True)
    pdf.cell(0, 10, f"Recovery Ratio: {data['recovery']} (Sales needed per 1 return)", ln=True)
    return pdf.output()

# --- UI HEADER ---
st.title("🚀 2026 Marketplace Command Center")
st.info("⚡ **Live Policy Update:** Amazon/Flipkart 0% Fees for items under ₹1,000 is active.")

# --- SIDEBAR GUIDE ---
with st.sidebar:
    st.header("📖 Layman's Manual")
    st.markdown("""
    1. **SKU Profit:** Calculate your 'take-home' money.
    2. **War Room:** Match competitors safely.
    3. **Cash Flow:** See your monthly bank balance.
    4. **Smart Restock:** Know when to order.
    5. **Bulk Upload:** Check 100 items at once.
    """)
    st.divider()
    st.caption("v4.0 - March 2026 Production Build")

# --- APP TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💰 SKU Profit", "⚔️ War Room", "📅 Cash Flow", "📦 Smart Restock", "📊 Bulk Upload"])

with tab1:
    c1, c2, c3 = st.columns([1, 1.2, 1.2])
    with c1:
        st.subheader("1. Setup")
        plat = st.selectbox("Marketplace", ["Amazon", "Flipkart", "Quick Commerce"])
        price = st.number_input("Selling Price (₹)", value=999.0)
        cogs = st.number_input("Landing Cost (₹)", value=450.0)
        region = st.radio("Region", ["Local", "National"])
        data = calculate_2026_economics(plat, price, cogs, region)
    with c2:
        st.subheader("2. Net Results")
        st.metric("Bank Payout", f"₹{data['payout']}")
        st.metric("Net Profit", f"₹{data['profit']}", delta=f"{data['margin']}% Margin")
        st.divider()
        st.write("**Ads Simulator**")
        target_acos = st.slider("Target ACOS %", 0.0, float(max(0.1, data['margin'])), float(data['margin']*0.6))
        st.info(f"Profit after Ads: **₹{data['profit'] - (price * target_acos/100):.2f}**")
    with c3:
        st.subheader("3. Risk & Export")
        st.error(f"Loss/Return: ₹{data['loss']}")
        st.warning(f"Recovery Ratio: {data['recovery']}")
        st.divider()
        pdf_data = generate_pdf_report(data, plat, price, cogs)
        st.download_button("📄 Download PDF Report", data=bytes(pdf_data), file_name="Report.pdf", mime="application/pdf")

with tab2:
    st.subheader("⚔️ Competitor War Room")
    comp_p = st.number_input("Competitor's Lower Price (₹)", value=price-50)
    comp_d = calculate_2026_economics(plat, comp_p, cogs)
    st.write(f"Profit if you match: **₹{comp_d['profit']}**")
    if comp_d['profit'] > (price * 0.05):
        st.success("💪 Safe to Match: Margin is still healthy.")
    else:
        st.error("🚫 Do Not Match: Margin will be too thin or negative.")

with tab3:
    st.subheader("📅 30-Day Cash Flow Forecast")
    daily_sales = st.number_input("Daily Units Sold", value=10)
    ret_rate = st.slider("Return Rate %", 0, 40, 10)
    monthly_profit = ((daily_sales * 30) * (1 - ret_rate/100) * data['profit']) - ((daily_sales * 30) * (ret_rate/100) * data['loss'])
    st.metric("Est. Monthly Profit", f"₹{monthly_profit:,.0f}")
    st.success(f"Claimable Tax Credits: ₹{data['tax_credit'] * daily_sales * 30:,.0f}")

with tab4:
    st.subheader("📦 Smart Restock")
    curr_stock = st.number_input("Stock on Hand", value=100)
    lead_time = st.number_input("Supplier Lead Time (Days)", value=7)
    reorder_point = daily_sales * (lead_time + 3)
    if curr_stock <= reorder_point:
        st.error(f"🚨 ORDER NOW! You need at least {reorder_point} units in stock.")
    else:
        st.success(f"✅ Stock is healthy. Reorder when you hit {reorder_point} units.")

with tab5:
    st.subheader("📊 Bulk Upload Analysis")
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        results = []
        for _, row in df.iterrows():
            calc = calculate_2026_economics(row['Platform'], row['Price'], row['COGS'])
            results.append({**row, "Profit": calc['profit'], "Margin%": calc['margin'], "Recovery": calc['recovery']})
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.write("Upload a CSV with columns: **Platform, Price, COGS, Product**")
