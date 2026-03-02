import streamlit as st
import pandas as pd
import io
import math
from fpdf import FPDF

# --- APP CONFIGURATION ---
st.set_page_config(page_title="2026 Seller Profit Master", layout="wide", page_icon="💰")

# --- MARCH 2026 LOGIC ---
def calculate_2026_economics(platform, price, cogs, region="National"):
    """Reflects structural fee changes as of March 2, 2026."""
    gst_rate = 0.18
    
    if platform == "Amazon":
        # Zero referral fee up to Rs. 1,000 (Structural change March 2026)
        referral = 0 if price <= 1000 else (price * 0.12)
        closing = 5 if price <= 250 else 30 if price <= 1000 else 60
        shipping = 45 if region == "Local" else 75
        total_fees = referral + closing + shipping
        return_loss = closing + shipping + (price * 0.02)
        
    elif platform == "Flipkart":
        # Zero commission up to Rs. 1,000 
        commission = 0 if price <= 1000 else (price * 0.08)
        fixed = 15 if price <= 500 else 35
        shipping = 40 if region == "Local" else 65
        total_fees = commission + fixed + shipping
        return_loss = (shipping * 1.2) + fixed
    else:
        total_fees = (price * 0.22) + 12 
        return_loss = total_fees * 0.6
        
    # 2026 Statutory Deductions
    fee_gst = total_fees * gst_rate
    tcs_gst = price * 0.005    # 0.5% GST TCS
    tds_it = price * 0.001     # 0.1% TDS u/s 194-O
    
    payout = price - (total_fees + fee_gst + tcs_gst + tds_it)
    profit = payout - cogs
    
    # Recovery Logic
    total_loss_per_return = return_loss + (return_loss * gst_rate) + 25 
    recovery_ratio = total_loss_per_return / profit if profit > 0 else 999
    
    return {
        "payout": round(payout, 2), "profit": round(profit, 2),
        "margin": round((profit/price)*100, 2) if price > 0 else 0,
        "loss": round(total_loss_per_return, 2), "recovery": round(recovery_ratio, 1)
    }

# --- PDF GENERATOR ---
def generate_pdf(data, plat, price, cogs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"Profit Report: {plat}", ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, f"Price: Rs. {price} | Profit: Rs. {data['profit']} ({data['margin']}%)", ln=True)
    pdf.cell(0, 10, f"To cover 1 return, you need to sell {data['recovery']} units.", ln=True)
    return pdf.output()

# --- USER INTERFACE ---
st.title("📈 2026 Marketplace Profit Suite")
st.info("💡 **March 2026 Update:** Amazon/Flipkart now have 0% commission for items under ₹1,000.")

with st.sidebar:
    st.header("📖 Layman's Guide")
    st.markdown("""
    **How to use this app:**
    1. **Setup:** Choose your marketplace and costs.
    2. **Payout:** This is the cash you get in your bank.
    3. **Profit:** This is your actual 'take-home' money.
    4. **War Room:** Match competitor prices safely.
    5. **Restock:** Don't run out of stock!
    """)

t1, t2, t3, t4 = st.tabs(["💰 Profit Calculator", "⚔️ War Room", "📅 Monthly Forecast", "📦 Restock"])

with t1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Enter Details")
        plat = st.selectbox("Marketplace", ["Amazon", "Flipkart"], help="Select where you sell.")
        price = st.number_input("Selling Price (₹)", value=999.0, help="What the customer pays.")
        cogs = st.number_input("Landing Cost (₹)", value=450.0, help="Your total cost to get the item ready to ship.")
        data = calculate_2026_economics(plat, price, cogs)
    with c2:
        st.subheader("Your Earnings")
        st.metric("Bank Payout", f"₹{data['payout']}", help="Cash after fees and taxes.")
        st.metric("Net Profit", f"₹{data['profit']}", f"{data['margin']}% Margin")
        st.download_button("📄 Download Report", data=generate_pdf(data, plat, price, cogs), file_name="report.pdf")

with t2:
    st.subheader("⚔️ Competitor War Room")
    comp_price = st.number_input("Competitor's Price", value=price-20)
    comp_res = calculate_2026_economics(plat, comp_price, cogs)
    if comp_res['profit'] > 50:
        st.success(f"Safe to Match! You still earn ₹{comp_res['profit']} per unit.")
    else:
        st.error(f"Danger! Matching this price leaves you only ₹{comp_res['profit']}. Avoid matching.")

with t3:
    st.subheader("📅 Cash Flow Forecast")
    daily = st.number_input("Daily Sales Units", value=10)
    ret = st.slider("Return Rate %", 0, 30, 10)
    monthly = (daily * 30 * (1-ret/100) * data['profit']) - (daily * 30 * (ret/100) * data['loss'])
    st.metric("Estimated Monthly Profit", f"₹{monthly:,.0f}")

with t4:
    st.subheader("📦 Smart Restock")
    stock = st.number_input("Current Stock", value=50)
    lead = st.number_input("Lead Time (Days)", value=7)
    reorder = daily * (lead + 2)
    if stock <= reorder:
        st.error(f"🚨 ORDER NOW! You need at least {reorder} units in stock to avoid going OOS.")
    else:
        st.success(f"✅ Stock is healthy. Reorder when you hit {reorder} units.")
