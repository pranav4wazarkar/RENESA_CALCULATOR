import streamlit as st
import pandas as pd
import math
from fpdf import FPDF

# --- MARCH 2026 POLICY-ALIGNED CALCULATOR ---
def calculate_2026_economics(platform, price, cogs, region="National"):
    """
    March 2026 Rules: 
    - Amazon: 0% Referral for items < ₹1,000 (Structural Change).
    - Flipkart: 0% Commission for items < ₹1,000.
    - Statutory: 0.1% TDS and 0.5% GST TCS.
    """
    gst_rate = 0.18
    
    if platform == "Amazon":
        # New March 16, 2026 Policy
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
    else: # Quick Commerce (Swiggy/Blinkit)
        total_fees = (price * 0.22) + 12 
        return_loss = total_fees * 0.6
        
    # 2026 Statutory Deductions
    fee_gst = total_fees * gst_rate
    tcs_gst = price * 0.005    # 0.5% GST TCS
    tds_it = price * 0.001     # 0.1% TDS
    
    payout = price - (total_fees + fee_gst + tcs_gst + tds_it)
    profit = payout - cogs
    
    # Recovery Calculation
    total_loss_per_return = return_loss + (return_loss * gst_rate) + 25 
    recovery_ratio = total_loss_per_return / profit if profit > 0 else 999
    
    return {
        "payout": round(payout, 2), "profit": round(profit, 2),
        "margin": round((profit/price)*100, 2) if price > 0 else 0,
        "loss": round(total_loss_per_return, 2), "recovery": round(recovery_ratio, 1)
    }

# --- PDF GENERATOR (FIXED FOR DEPLOYMENT) ---
def generate_pdf_report(data, plat, price, cogs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 15, f"2026 Profit Report: {plat}", ln=True, align='C')
    pdf.set_font("Helvetica", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Selling Price: Rs. {price}", ln=True)
    pdf.cell(0, 10, f"Landing Cost (COGS): Rs. {cogs}", ln=True)
    pdf.cell(0, 10, f"Bank Payout: Rs. {data['payout']}", ln=True)
    pdf.cell(0, 10, f"Net Profit: Rs. {data['profit']} ({data['margin']}%)", ln=True)
    pdf.cell(0, 10, f"Return Recovery Ratio: {data['recovery']} (Sales needed per 1 return)", ln=True)
    
    # IMPORTANT: Output the PDF as a string/bytes for Streamlit
    return pdf.output()

# --- APP LAYOUT ---
st.set_page_config(page_title="2026 Seller Suite", layout="wide")
st.title("🚀 2026 Marketplace Command Center")

# --- SIDEBAR GUIDE ---
with st.sidebar:
    st.header("📖 Layman's Manual")
    st.info("**What is Bank Payout?** This is the money that actually hits your bank after the platform takes its cut.")
    st.info("**What is Recovery Ratio?** If it is '5', you must sell 5 items to cover the loss of 1 customer return.")

# --- TABS ---
t1, t2, t3 = st.tabs(["💰 Profit Calculator", "⚔️ Competitor War Room", "📦 Smart Restock"])

with t1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Input Details")
        plat = st.selectbox("Marketplace", ["Amazon", "Flipkart", "Quick Commerce"])
        price = st.number_input("Selling Price (₹)", value=999.0)
        cogs = st.number_input("Landing Cost (₹)", value=450.0)
        data = calculate_2026_economics(plat, price, cogs)
        
    with c2:
        st.subheader("Profitability Metrics")
        st.metric("In-Hand Profit", f"₹{data['profit']}", f"{data['margin']}% Margin")
        
        # PDF FIX: Convert output to bytes before download
        pdf_data = generate_pdf_report(data, plat, price, cogs)
        st.download_button(
            label="📄 Download Business Report",
            data=bytes(pdf_data), # THIS FIXES YOUR ERROR
            file_name=f"{plat}_Profit_Report.pdf",
            mime="application/pdf"
        )

with t2:
    st.subheader("⚔️ Price Match Analysis")
    comp_p = st.number_input("Competitor's Lower Price", value=price-100)
    comp_d = calculate_2026_economics(plat, comp_p, cogs)
    if comp_d['profit'] > 50:
        st.success(f"Safe to Match! Profit remains ₹{comp_d['profit']}")
    else:
        st.error(f"Loss Warning! Match will leave you with only ₹{comp_d['profit']}")

with t3:
    st.subheader("📦 Stock Manager")
    daily = st.number_input("Daily Sales", value=10)
    stock = st.number_input("Current Inventory", value=50)
    if daily > 0:
        days = stock // daily
        st.write(f"You have approximately **{days} days** of stock left.")
        if days < 7:
            st.warning("⚠️ Time to restock soon!")
