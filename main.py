import mysql.connector
import pandas as pd
import streamlit as st
from mysql.connector import Error

# MySQL 서버에 연결하는 함수
def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL 서버에 성공적으로 연결되었습니다.")
    except Error as err:
        print(f"Error: '{err}'")
    return connection

# 데이터 가져오는 함수
def fetch_data(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    return pd.DataFrame(rows, columns=columns)

# MySQL 서버에 연결
connection = create_connection("localhost", "your_username", "your_password", "ex1")

# 데이터베이스에서 데이터 가져오기
query = "SELECT * FROM your_table_name;"
df = fetch_data(connection, query)

# 연결 종료
connection.close()

# Streamlit을 통해 데이터프레임 표시
st.title("MySQL 테이블 데이터")
st.write("아래는 'your_table_name' 테이블의 데이터입니다:")
st.dataframe(df)
