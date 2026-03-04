from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
import json
import pandas as pd 
import pickle
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal

with open('model.pkl', 'rb') as f:
    model = pickle.load(f) # loads it into memory

tier_1_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]
tier_2_cities = [
        "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam", "Coimbatore",
        "Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
        "Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
        "Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
        "Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal",
        "Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri"
    ]  

app = FastAPI()

class UserInput(BaseModel):
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of the client")]
    weight: Annotated[float, Field(..., gt=0, description="Weight of the client in kgs")]
    height: Annotated[float, Field(..., gt=0, description="Height of the client in metres")]
    income_lpa: Annotated[float, Field(..., gt=0, description="Salary of the client")]
    smoker: Annotated[bool, Field(..., description="Is the client a smoker ?")]
    city: Annotated[str, Field(..., description="City of the client")]
    occupation: Annotated[Literal['retired', 'freelancer', 'student', 'government_job',
    'business_owner', 'unemployed', 'private_job'], Field(..., description="Occupation of the client")]
    
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def lifestyle_risk(self) -> str:
        if self.smoker and self.bmi > 30:
            return "high"
        elif self.smoker and self.bmi > 27:
            return "medium"
        else:
            return "low"
    
    @computed_field
    @property
    def age_group(self) -> str:
        if self.age < 25:
            return "young"
        elif self.age < 45:
            return "adult"
        elif self.age < 60:
            return "middle_aged"
        return "senior"
    
    @computed_field
    @property
    def city_tier(self) -> int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3

@app.post("/predict")
def predict_premium(data: UserInput):
    # ML models expect a 2D structure (rows × columns), so we create a one-row DataFrame
    input_df = pd.DataFrame([{
        'bmi': data.bmi,
        'age_group': data.age_group,
        'lifestyle_risk': data.lifestyle_risk,
        'city_tier': data.city_tier,
        'income_lpa': data.income_lpa,
        'occupation': data.occupation
    }])
    prediction = model.predict(input_df)[0] # model.predict() returns an array, even for one input it returns something like [2]. '[0]' extracts the actual value.
    
    return JSONResponse(status_code=200, content={"predicted_category": prediction})