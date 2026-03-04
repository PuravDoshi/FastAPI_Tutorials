from pydantic import BaseModel

class Address(BaseModel):
    city: str
    state: str
    pin: str

class Patient(BaseModel):
    name: str
    gender: str = 'Male'
    age: int
    address: Address

address_dict = {'city': 'gurgaon', 'state': 'haryana', 'pin': '122001'}
address1 = Address(**address_dict)

patient_dict = {'name': 'purav', 'age': 35, 'address': address1}
patient1 = Patient(**patient_dict)

temp = patient1.model_dump(exclude={'address':{'city','state'}}) # model.dump() returns a python dict, model.dump_json() returns json format

print(temp)
print(type(temp))