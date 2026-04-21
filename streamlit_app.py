
st.set_page_config(page_title="Deal Underwriter", layout="wide")
st.title("Deal Underwriter")
st.subheader("Adrian Martinez Borrega | Disposition Agent")
st.subheader("Contact (562)734-94-90 for more info and comps")

# -----------------------------
# Inputs
# -----------------------------
deal_type = st.selectbox("Financing Type", ["Cash", "Hard Money"])
hoa_checked = st.checkbox("HOA (+$1,000)")

col1, col2, col3 = st.columns(3)

with col1:
    purchase_price = st.number_input("Acquisition Price", min_value=0.0, step=1000.0)
    rehab = st.number_input("Rehab Estimate", min_value=0.0, step=1000.0)
    arv = st.number_input("ARV", min_value=0.0, step=1000.0)

with col2:
    interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=11.0, step=0.1) / 100
    hold_months = st.number_input("Holding Time (Months)", min_value=0.0, value=6.0, step=1.0)
    property_tax_annual = st.number_input("Annual Property Tax", min_value=0.0, step=1000.0)

with col3:
    realtor_fee_pct = st.number_input("Realtor Fee (%)", min_value=0.0, value=5.0, step=0.1) / 100
    insurance_pct = st.number_input("Insurance (% of ARV)", min_value=0.0, value=1.0, step=0.1) / 100
    sqft = st.number_input("Square Feet", min_value=0.0, step=50.0)

# -----------------------------
# Helper functions
# -----------------------------
def buyer_closing_cost(price, hoa=False):
    if price >= 500000:
        cost = 13000
    elif price >= 450000:
        cost = 12000
    elif price >= 400000:
        cost = 11000
    elif price >= 350000:
        cost = 10000
    elif price >= 300000:
        cost = 9000
    elif price >= 250000:
        cost = 8000
    elif price >= 200000:
        cost = 7000
    elif price >= 150000:
        cost = 6000
    elif price >= 1:
        cost = 5000
    else:
        cost = 0

    if hoa:
        cost += 1000

    return cost


def escrow_money(price):
    if price <= 250000:
        return 7500
    elif price <= 500000:
        return 10000
    elif price <= 750000:
        return 20000
    elif price <= 1000000:
        return 30000
    elif price <= 1500000:
        return 35000
    return 40000

# -----------------------------
# Core calculations
# -----------------------------
closing_buy = buyer_closing_cost(purchase_price, hoa_checked)
seller_closing = arv * 0.01  # K4

if deal_type == "Hard Money":
    monthly_interest = (purchase_price + rehab) * interest_rate / 12
else:
    monthly_interest = 0.0

tax_at_closing = (property_tax_annual / 12) * hold_months
holding_cost = (monthly_interest * hold_months) + tax_at_closing
realtor_cost = arv * realtor_fee_pct
insurance_cost = ((insurance_pct * arv) / 12) * hold_months

price_sqft_before = 0 if sqft == 0 else purchase_price / sqft
price_sqft_after = 0 if sqft == 0 else arv / sqft

escrow = escrow_money(purchase_price)

# -----------------------------
# Capital / ROI logic
# -----------------------------
if deal_type == "Cash":
    loan_amount = 0.0
    down_payment = 0.0
    cash_to_close = purchase_price + rehab + closing_buy
    liquidity_reserved = 0.0
    est_cash_needed = cash_to_close

    money_in = purchase_price + rehab + closing_buy + holding_cost
    money_out = arv - realtor_cost - insurance_cost - seller_closing - holding_cost

else:
    total_project_basis = purchase_price + rehab + closing_buy
    loan_amount = total_project_basis * 0.9
    down_payment = total_project_basis * 0.1

    cash_to_close = down_payment + escrow
    liquidity_reserved = loan_amount * 0.3
    est_cash_needed = max(cash_to_close, liquidity_reserved)

    money_in = down_payment + holding_cost

    money_out = (
        arv
        - realtor_cost
        - insurance_cost
        - seller_closing
        - holding_cost
        - loan_amount
    )

roi = 0 if money_in == 0 else (money_out - money_in) / money_in

# -----------------------------
# Profit calculations
# -----------------------------
# Corrected profit logic: tax counted once through holding_cost
profit_corrected = arv - (
    purchase_price
    + rehab
    + closing_buy
    + holding_cost
    + realtor_cost
    + insurance_cost
    + tax_at_closing
    + seller_closing
)

# Exact Excel-style profit if your workbook subtracts tax twice
profit_excel_exact = arv - (
    purchase_price
    + rehab
    + closing_buy
    + holding_cost
    + tax_at_closing
    + realtor_cost
    + insurance_cost
    + seller_closing
)

profit = profit_corrected

# -----------------------------
# Top summary
# -----------------------------
st.subheader("Results")

top1, top2 = st.columns(2)
top1.metric("Profit", f"${profit:,.0f}")
top2.metric("ROI", f"{roi:.2%}")



st.markdown("---")

# -----------------------------
# Capital Needed + Return Summary
# -----------------------------
left, right = st.columns(2)

with left:
    st.markdown("#### Capital Needed")
    a, b = st.columns(2)
    a.metric("Est Cash Needed", f"${est_cash_needed:,.0f}")
    b.metric("Loan Amount", f"${loan_amount:,.0f}")

    c, d = st.columns(2)
    c.metric("Cash to Close", f"${cash_to_close:,.0f}")
    d.metric("Liquidity Reserved", f"${liquidity_reserved:,.0f}")

    st.metric("Escrow Money", f"${escrow:,.0f}")

with right:
    st.markdown("#### Return Summary")
    e, f, g = st.columns(3)
    e.metric("Money In", f"${money_in:,.0f}")
    f.metric("Money Out", f"${money_out:,.0f}")
    g.metric("ROI", f"{roi:.2%}")

st.markdown("---")

# -----------------------------
# Cost Breakdown
# -----------------------------
st.markdown("#### Cost Breakdown")
c1, c2, c3 = st.columns(3)

with c1:
    st.write(f"Buyer Closing: ${closing_buy:,.0f}")
    st.write(f"Seller Closing: ${seller_closing:,.0f}")
    st.write(f"Realtor Cost: ${realtor_cost:,.0f}")

with c2:
    st.write(f"Tax at Closing: ${tax_at_closing:,.0f}")
    st.write(f"Insurance Cost: ${insurance_cost:,.0f}")
    st.write(f"Holding Cost: ${holding_cost:,.0f}")

with c3:
    st.write(f"Interest / Month: ${monthly_interest:,.0f}")
    st.write(f"Price/SqFt Before: ${price_sqft_before:,.2f}")
    st.write(f"Price/SqFt After: ${price_sqft_after:,.2f}")

st.markdown("---")    
