import pandas as pd
import streamlit as st
from pymongo import MongoClient 

uri = "mongodb+srv://red23:dm123@cluster0.egiqw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri,tlsCAFile=ca)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['test']
collection = db['students']

def fetch_data():
    students = list(collection.find())
    return students

st.title('Student Records from MongoDB')
    
# 데이터 불러오기
data = fetch_data()

# 데이터 표시
if data:
    for student in data:
        st.write(student)
else:
    st.write("No data found.")
    
