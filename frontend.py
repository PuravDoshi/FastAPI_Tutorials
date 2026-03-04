import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/predict" 
# 127.0.0.1 → local machine
# 8000 → FastAPI server port
# /predict → your backend endpoint

st.title("Insurance Premium Category Predictor")
st.markdown("Enter your details below:")

# Input fields
age = st.number_input("Age", min_value=1, max_value=119, value=30)
weight = st.number_input("Weight (kg)", min_value=1.0, value=65.0)
height = st.number_input("Height (m)", min_value=0.5, max_value=2.5, value=1.7)
income_lpa = st.number_input("Annual Income (LPA)", min_value=0.1, value=10.0)
smoker = st.selectbox("Are you a smoker?", options=[True, False])
city = st.text_input("City", value="Mumbai")
occupation = st.selectbox(
    "Occupation",
    ['retired', 'freelancer', 'student', 'government_job', 'business_owner', 'unemployed', 'private_job']
)

if st.button("Predict Premium Category"):
    # This dictionary is prepared to match the FastAPI "UserInput" model.
    input_data = {
        "age": age,
        "weight": weight,
        "height": height,
        "income_lpa": income_lpa,
        "smoker": smoker,
        "city": city,
        "occupation": occupation
    }

    try:
        response = requests.post(API_URL, json=input_data)
        result = response.json()
        # What happens internally:
        # 1. requests.post() sends HTTP POST request
        # 2. json=input_data converts dictionary → JSON
        # 3. FastAPI receives request at /predict

        if response.status_code == 200:
            result = response.json() # .json() converts the JSON response → Python dictionary.
            st.success(f"Predicted Insurance Premium Category: **{result['predicted_category']}**")

        else:
            st.error(f"API Error: {response.status_code}")
            st.write(result)

    # If the FastAPI Server is not running
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the FastAPI server. Make sure it's running.")