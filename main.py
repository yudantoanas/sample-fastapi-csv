from fastapi import FastAPI, HTTPException
import pandas as pd
from pydantic import BaseModel
from datetime import datetime


class Profile(BaseModel):
    '''
    Profile model is used for creating request body
    '''
    name: str
    age: int
    location: str

# create FastAPI object
app = FastAPI()


@app.get("/")
async def getWelcome():
    return {
        "msg": "Sample FastAPI CSV"
    }


@app.get("/data")
async def getAllData():
    df = pd.read_csv("dataset.csv")

    return {
        "data": df.to_dict(orient="records")
    }


@app.get("/data/{location}")
async def getDataByLocation(location: str):
    df = pd.read_csv("dataset.csv")

    df = df[df.location == location]

    # validate filter data
    if len(df) > 0:
        return {
            "data": df.to_dict(orient="records")
        }

    raise HTTPException(status_code=404, detail="Data not found")


@app.patch("/data/{id}")
async def updateProfile(id: int, profile: Profile):
    df = pd.read_csv("dataset.csv")

    filter = df[df.id == id]
    # check data existence
    if len(filter) == 0:
        raise HTTPException(status_code=404, detail="Data not found")

    # if exists, update specific row using .loc[]
    df.loc[df.id == id, ['name', 'age', 'location']] = [
        profile.name, profile.age, profile.location]

    df.sort_values(by=['id'], ignore_index=True, inplace=True)
    df.to_csv('dataset.csv', index=False)

    return {
        "msg": "Data has been updated"
    }


@app.post("/data")
async def createProfile(profile: Profile):
    df = pd.read_csv("dataset.csv")

    newData = pd.DataFrame()
    newData['id'] = df.tail(1)['id'] + 1
    newData['name'] = profile.name
    newData['age'] = profile.age
    newData['location'] = profile.location
    newData['created_at'] = datetime.now().date()

    df = pd.concat([df, newData], ignore_index=True)

    df.sort_values(by=['id'], ignore_index=True, inplace=True)
    df.to_csv('dataset.csv', index=False)

    return {
        "data": df.tail(1).to_dict(orient='records')
    }


@app.delete('/data/{id}')
async def deleteProfile(id: int):
    df = pd.read_csv("dataset.csv")

    # check data existence
    filter = df[df.id == id]
    if len(filter) == 0:
        raise HTTPException(status_code=404, detail="Data not found")

    # if exists, delete it
    df = df[df.id != id]
    df.sort_values(by=['id'], ignore_index=True, inplace=True)
    df.to_csv('dataset.csv', index=False)

    return {
        "msg": "Data has been deleted"
    }
