import pandas as pd
from pymongo import MongoClient

csv_file_path = "Automobile.csv" 
df = pd.read_csv(csv_file_path)

client = MongoClient('mongodb://localhost:27017/')
db = client['carsdb'] 
collection = db['car_collection'] 
data = df.to_dict(orient='records')
collection.insert_many(data)

print("Data inserted successfully")

