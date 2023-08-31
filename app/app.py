from fastapi import FastAPI, HTTPException, Query, Response
from typing import List
import csv
import sqlite3
import asyncio
import numpy as np


app = FastAPI()

# Load data source from config
with open('config.txt', 'r') as config_file:
    data_source = config_file.readline().strip()

#
# Load CSV data into memory
data = []
if data_source == 'CSV':
    with open('./titanic_data.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        data = list(csv_reader)
elif data_source == 'SQLITE':
    conn = sqlite3.connect('titanic.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM passengers')
    data = [dict(row) for row in cursor.fetchall()]
    conn.close()


# Connect to SQLite database (ensure you have the database file available)
conn = sqlite3.connect('titanic.db')

# Asynchronous route to return a histogram of Fare prices in percentiles
@app.get('/get_histogram')
async def get_histogram():

    fares = [float(row['Fare']) for row in data]
    percentiles = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    prices_percentiles = {percent: np.percentile(fares, percent) for percent in percentiles}
    return prices_percentiles


# Asynchronous route to return all passenger data in JSON format for a given PassengerId
@app.get('/get_passenger/{passenger_id}')
async def get_passenger(passenger_id: int):
    
    # Find the passenger by PassengerId
    passenger = next((p for p in data if int(p['PassengerId']) == passenger_id), None)

    if passenger:
        return passenger
    else:
        raise HTTPException(status_code=404, detail="Passenger not found")


# Asynchronous route to return requested attributes in JSON format for a given PassengerId
@app.get('/get_passenger_attributes/{passenger_id}')
async def get_passenger_attributes(
    passenger_id: int,
    attributes: List[str] = Query(..., description="List of attributes to retrieve")):

    passenger = next((p for p in data if int(p['PassengerId']) == passenger_id), None)
    if not passenger:
        raise HTTPException(status_code=404, detail="Passenger not found")

    selected_attributes = {attr: passenger[attr] for attr in attributes if attr in passenger}
    return selected_attributes


# Asynchronous route to return a list of all passengers in JSON format
@app.get('/get_all_passengers')
async def get_all_passengers():
    return data


if __name__ == '__main__':
    app.run(debug=True)

