import streamlit as st
import pandas as pd
from db.database import SessionLocal, init_db
from db import crud
from sqlalchemy.exc import IntegrityError
from fuzzywuzzy import process
import altair as alt

init_db()
db = SessionLocal()

st.title("EduMRV Emissions Calculator")

# Load emission factors
factors_df = pd.read_csv("data/emissions_factors.csv")
categories = factors_df["category"].tolist()

# --- User Login/Register ---
with st.sidebar:
    st.header("User Login")
    email = st.text_input("Email")
    name = st.text_input("Name")
    login_btn = st.button("Log In / Register")

if login_btn and email and name:
    user = crud.get_user(db, email)
    if not user:
        try:
            user = crud.create_user(db, email=email, name=name)
            st.sidebar.success("User registered.")
        except IntegrityError:
            st.sidebar.error("User exists. Try again.")
    else:
        st.sidebar.success(f"Welcome back, {user.name}!")

# Main app functionality
if email:
    st.subheader("Enter Emissions Data")

    # Fuzzy autocomplete for category
    user_input = st.text_input("Enter category (e.g. Diesel, Electricity)")
    matches = process.extract(user_input, categories, limit=3)
    suggested = matches[0][0] if matches else ""
    st.caption(f"Suggestion: {suggested}")
    selected_category = st.selectbox("Or choose from list", categories, index=categories.index(suggested) if suggested in categories else 0)

    quantity = st.number_input(f"Enter quantity ({factors_df[factors_df['category'] == selected_category]['unit'].values[0]})", min_value=0.0)

    if st.button("Calculate Emission"):
        factor_row = factors_df[factors_df['category'] == selected_category].iloc[0]
        emission = quantity * factor_row['factor']
        scope = factor_row['scope']
        user = crud.get_user(db, email)
        crud.create_emission_record(db, user.id, selected_category, quantity, emission, scope)
        st.success(f"Emission recorded: {emission:.2f} kg CO₂ ({scope})")

    # --- Visualize data ---
    st.subheader("Your Emissions Summary")

    user = crud.get_user(db, email)
    records = crud.get_user_emissions(db, user.id)
    if records:
        df = pd.DataFrame([{
            "Category": r.category,
            "Quantity": r.quantity,
            "Emission": r.emission,
            "Scope": r.scope,
            "Time": r.timestamp
        } for r in records])

        st.dataframe(df)

        chart = alt.Chart(df).mark_bar().encode(
            x='Category',
            y='Emission',
            color='Scope'
        ).properties(title="Emissions by Category and Scope")

        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No emissions data yet.")
