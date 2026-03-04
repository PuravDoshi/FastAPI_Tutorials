from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Optional, Literal

app=FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="ID of the patient", examples=["P001"])]
    name: Annotated[str, Field(..., description="Name of the patient")]
    city: Annotated[str, Field(..., description="City where the patient stays")]
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of the patient")]
    gender: Annotated[Literal["Male", "Female", "Others"], Field(..., description="Gender of the patient")]
    height: Annotated[float, Field(..., gt=0, description="Height of the patient in metres")]
    weight: Annotated[float, Field(..., gt=0, description="Weight of the patient in kgs")]
    
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif self.bmi < 30:
            return "Normal"
        else:
            return "Overweight"

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)] # Optional allows partial updates
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0, lt=120)]
    gender: Annotated[Optional[Literal["Male", "Female", "Others"]], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

def load_data(): # load_data() → Translate json file language into Python language (dict)
    with open("patients.json", 'r') as f:
        data = json.load(f)
    return data

def save_data(data): # save_data() → Translate Python language (dict) back into json file language
    with open("patients.json", 'w') as f:
        json.dump(data, f)
    return data

@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient already exists")
    
    # You use patient ID as dictionary key
    # Actual stored value excludes ID (since it's already used as key)
    data[patient.id] = patient.model_dump(exclude=["id"]) 
    save_data(data)
    return JSONResponse(status_code=201, content={"message":"patient created successfully"})

@app.get("/")
def hello():
    return {'message': 'A Patient Management System API'}

@app.get("/about")
def about():
    return {'message': 'A fully functional API to manage your patient records'}

@app.get("/view")
def view():
    data = load_data()
    return data

@app.get("/patient/{patient_id}")
def view_patient(patient_id: str=Path(..., description="ID of the patient in the DB", example="P001")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='Patient ID not found')

@app.get("/sort")
def sort_patients(sort_by: str = Query(..., description="Sort on the basis of height, weight or bmi"), order: str = Query("asc", description="Sort in ascending (asc) or descending order (desc)")):
    
    valid_fields = ["height", "weight", "bmi"]
    valid_orders = ["asc", "desc"]
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code=404, detail=f'Select only from {valid_fields}')
    if order not in valid_orders:
        raise HTTPException(status_code=404, detail=f'Select only from {valid_orders}')
    
    sort_order = True if order=="desc" else False
    
    data = load_data()
    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)
    
    return sorted_data

@app.put("/edit/{patient_id}")
def update_patient(patient_id: str, patient_update: PatientUpdate):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient ID not found')

    existing_info = data[patient_id] # This loads the full existing patient dictionary
    updated_patient_info = patient_update.model_dump(exclude_unset=True) # Only include fields that were actually provided by the user
    
    for key, value in updated_patient_info.items():
        existing_info[key] = value
    
    # Now we need to recalculated the new BMI and verdict
    # existing_info -> Pydantic object -> Updated BMI and Verdict -> Convert to Dictionary -> Add to data
    existing_info['id'] = patient_id # This updates only provided fields, remaining fields are unchanged
    patient_pydantic = Patient(**existing_info)
    existing_info = patient_pydantic.model_dump(exclude='id')
    data[patient_id] = existing_info
    save_data(data)
    return JSONResponse(status_code=200, content={"message":"patient updated successfully"})

@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient ID not found')
    
    del data[patient_id]
    save_data(data)
    return JSONResponse(status_code=200, content={"message":"patient deleted successfully"})