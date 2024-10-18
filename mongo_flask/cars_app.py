from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
from pydantic import BaseModel
from typing import Optional
from pydantic import ValidationError

app = Flask(__name__)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['carsdb']
collection = db['car_collection']

# Pydantic model to validate data
class CarModel(BaseModel):
    name: str
    mpg: str
    cylinders: str
    displacement: str
    horsepower: str
    weight: str
    acceleration: str
    year: str
    origin: str

# Convert MongoDB object to JSON serializable format
def car_serializer(car) -> dict:
    return {
        "_id": str(car["_id"]),
        "name": car["name"],
        "mpg": car["mpg"],
        "cylinders": car["cylinders"],
        "displacement": car["displacement"],
        "horsepower": car["horsepower"],
        "weight": car["weight"],
        "acceleration": car["acceleration"],
        "year": car["year"],
        "origin": car["origin"]
    }

# Insert a new car entry
"""
@app.route('/car', methods=['POST'])
def add_car():
    try:
        car = CarModel(**request.json)
        car_dict = car.dict()
        result = collection.insert_one(car_dict)
        return jsonify({"_id": str(result.inserted_id), "message": "Car added successfully"}), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400

"""
@app.route('/car', methods=['GET', 'POST'])
def add_car():
    if request.method == 'POST':
        car_data = request.json
        return jsonify({"message": "Car added successfully", "data": car_data})
    else:
        return jsonify({"message": "This route supports POST requests"})


# Get all car entries
@app.route('/cars', methods=['GET'])
def get_cars():
    cars = collection.find()
    cars_list = [car_serializer(car) for car in cars]
    return jsonify(cars_list)

# Search a car by ID
@app.route('/car/<car_id>', methods=['GET'])
def get_car(car_id):
    car = collection.find_one({"_id": ObjectId(car_id)})
    if car:
        return jsonify(car_serializer(car))
    else:
        return jsonify({"error": "Car not found"}), 404

# Delete a car by ID
@app.route('/car/<car_id>', methods=['DELETE'])
def delete_car(car_id):
    result = collection.delete_one({"_id": ObjectId(car_id)})
    if result.deleted_count:
        return jsonify({"message": "Car deleted successfully"}), 200
    else:
        return jsonify({"error": "Car not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5001)

