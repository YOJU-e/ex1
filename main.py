import sys
import os
import pandas as pd
import numpy as np
import streamlit as st
from pymongo import MongoClient
from datetime import datetime, date
import time
import json
import math
import matplotlib.pyplot as plt

def number_to_month(month):
    months = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }
    for key, value in months.items():
        if value == month:
            return key
    return "Invalid month name"

def month_to_number(month_name):
    months = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }
    return months.get(month_name, "Invalid month name")


def convert_to_date(date_str, i_year):
    # 예시: 'July1st' 같은 문자열을 '2024-07-01' 같은 형식으로 변환
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    if date_str is None:
        return None

    if date_str == "Total":
        return None
    try:    # 예를 들어 'July1st'에서 'July'와 '1'을 추출
        for month in month_map:
            if date_str.startswith(month):
                day_str = date_str[len(month):]
                day = ''.join(filter(str.isdigit, day_str))
                if day:
                    month_number = month_map[month]
                    return datetime(year= i_year, month=month_number, day=int(day))
                break
        return None
    except ValueError as e:
        print(f"Error converting {date_str}: {e}")
        return None

def calculate_total_leads(client, t_year, t_month):
    st.session_state.yearly_df = True
    df_total = pd.DataFrame()
    for y in range(2022,t_year+1):
        db_name = f'db_leads_{y}'
        db = client[db_name]
        if y == t_year:
            monthly_total = [0] * 12
            for m in range(1,t_month+1):
                e_month = number_to_month(m)
                collection_name = f'{e_month}_{y}'
                collection = db[collection_name]
                data = list(collection.find())
                df_table = pd.DataFrame(data)
                # st.write(df_table)
                df_table = df_table.drop('_id', axis=1)
                df_table = df_table.fillna(0)
                month_total = df_table.drop('program',axis=1).values.sum()
                monthly_total[m-1] = month_total
            df_total[f'{y}'] = monthly_total

        else:
            monthly_total = [0] * 12
            for m in range(1,13):
                e_month = number_to_month(m)
                collection_name = f'{e_month}_{y}'
                collection = db[collection_name]
                data = list(collection.find())
                df_table = pd.DataFrame(data)
                df_table = df_table.drop('_id', axis=1)
                df_table = df_table.fillna(0)
                month_total = df_table.drop('program',axis=1).values.sum()
                monthly_total[m-1] = month_total
            df_total[f'{y}'] = monthly_total

    months = ['January', 'February', 'March', 'April','May','June','July','August','September', 'October', 'November', 'December']
    df_total.insert(0, 'month', months)
    sum_row = df_total.iloc[:, 1:].sum()
    sum_row['month'] = 'Total'
    df_total = pd.concat([df_total, pd.DataFrame(sum_row).T], ignore_index=True)

    return df_total

def concat_d_df(client, programs, f_year, f_month, t_year, t_month):
    st.session_state.w_cpl_df = True
    df = pd.DataFrame({'program':programs})
    df.set_index(df.columns[0], inplace=True)

    for y in range(f_year,t_year+1):
        db_name = f'db_leads_{y}'
        db = client[db_name]
        if t_year - f_year == 0:
            for m in range(f_month,t_month+1):
                e_month = number_to_month(m)
                collection_name = f'{e_month}_{y}'
                collection = db[collection_name]
                data = list(collection.find())
                df_table = pd.DataFrame(data)
                df_table = df_table.drop('_id', axis=1)
                df_table.rename(columns={df_table.columns[0]: 'program'}, inplace=True)
                df_table.set_index(df_table.columns[0], inplace=True)
                new_columns = [convert_to_date(col,y) for col in df_table.columns]
                df_table.columns = new_columns
                df = pd.concat([df, df_table], axis=1)
        else:
            if t_year - y == 0:
                for m in range(1,t_month+1):
                    e_month = number_to_month(m)
                    collection_name = f'{e_month}_{y}'
                    collection = db[collection_name]
                    data = list(collection.find())
                    df_table = pd.DataFrame(data)
                    df_table = df_table.drop('_id', axis=1)
                    df_table.rename(columns={df_table.columns[0]: 'program'}, inplace=True)
                    df_table.set_index(df_table.columns[0], inplace=True)
                    new_columns = [convert_to_date(col,y) for col in df_table.columns]
                    df_table.columns = new_columns
                    df = pd.concat([df, df_table], axis=1)
            else:
                if f_year - y == 0:
                    for m in range(f_month,13):
                        e_month = number_to_month(m)
                        collection_name = f'{e_month}_{y}'
                        collection = db[collection_name]
                        data = list(collection.find())
                        df_table = pd.DataFrame(data)
                        df_table = df_table.drop('_id', axis=1)
                        df_table.rename(columns={df_table.columns[0]: 'program'}, inplace=True)
                        df_table.set_index(df_table.columns[0], inplace=True)
                        new_columns = [convert_to_date(col,y) for col in df_table.columns]
                        df_table.columns = new_columns
                        df = pd.concat([df, df_table], axis=1)

                else:
                    for m in range(1,13):
                        e_month = number_to_month(m)
                        collection_name = f'{e_month}_{y}'
                        collection = db[collection_name]
                        data = list(collection.find())
                        df_table = pd.DataFrame(data)
                        df_table = df_table.drop('_id', axis=1)
                        df_table.rename(columns={df_table.columns[0]: 'program'}, inplace=True)
                        df_table.set_index(df_table.columns[0], inplace=True)
                        new_columns = [convert_to_date(col,y) for col in df_table.columns]
                        df_table.columns = new_columns
                        df = pd.concat([df, df_table], axis=1)
    df = df.T
    df.index.name = 'Date'

    # 주별로 그룹화하여 합계를 구함
    weekly_df = df.resample('W').sum()

    # 다시 원래 형태로 전치
    weekly_df = weekly_df.T
    weekly_df.columns = pd.to_datetime(weekly_df.columns)
    weekly_df.columns = [col.date() for col in weekly_df.columns]
    # weekly_df.columns = pd.to_datetime(weekly_df.columns)
    # weekly_df.columns = weekly_df.columns.strftime('%Y-%m-%d')
    # weekly_df.columns = [pd.to_datetime(col).strftime('%Y-%m-%d') for col in weekly_df.columns]

    return weekly_df

def resource_path(relative_path):
    try:
        # PyInstaller에서 실행 중인 경우
        base_path = sys._MEIPASS
    except Exception:
        # PyInstaller에서 실행 중이지 않은 경우
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    st.title('LeadDataAutoReturn')
    st.markdown('---') 
    Goto_option_file_path = resource_path("data/option_list.xlsx") #'./data/option_list.xlsx'
    ckCat_csv_path = resource_path("data/ck_PC1.csv") #"./data/ck_PC1.csv" # to get name of programs
    Programs_csv_path = resource_path("data/Category_s1.csv") # "./data/Category_s1.csv" # to get Programme(unique value)
    programs_file_path = resource_path("data/program_list.xlsx")
    df_programs = pd.read_excel(programs_file_path, engine='openpyxl')
    programs = df_programs.iloc[:, 0].tolist()

    today_date = datetime.now()
    e_month = today_date.strftime('%B') #July
    t_month = today_date.month
    t_year = today_date.year

    # Session initialization
    if 'updated' not in st.session_state:
        st.session_state.updated = ''
    if 'daily_df_with_total' not in st.session_state:
        st.session_state.daily_df_with_total = False
    if 'daily_col_sum_df' not in st.session_state:
        st.session_state.daily_col_sum_df = False
    if 'weekly_df' not in st.session_state:
        st.session_state.weekly_df = False
    if 'yearly_df' not in st.session_state:
        st.session_state.yearly_df = False
    if 'yearly_df_' not in st.session_state:
        st.session_state.yearly_df_ = False
    if 'w_cpl_df' not in st.session_state:
        st.session_state.w_cpl_df = False
    if 't_cpl_df' not in st.session_state:
        st.session_state.t_cpl_df = False

    
    # mongoDB를 이용해서 데이터 주고받기        
    with open('config.json') as config_file:
        config = json.load(config_file)
        mongo_user = config['mongo_user']
        mongo_password = config['mongo_password']
    
    uri = f"mongodb+srv://{mongo_user}:{mongo_password}@cluster0.egiqw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    # Create a new client and connect to the server
    client = MongoClient(uri)
    
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        st.write("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        st.write(e)
    
    st.markdown('---')
    #데일리 리트 체크 화면
    st.subheader('Leads')
    # st.markdown('---') 
    years = list(range(2022, t_year + 1))
    # months = list(range(1, 13))
    months = ['January', 'February', 'March', 'April','May','June','July','August','September', 'October', 'November', 'December']
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        selected_year = st.selectbox('Select Year', years, index=years.index(t_year), key='year_select_for_d_check')
    with col2:
        selected_month = st.selectbox('Select Month', months, index=t_month-1, key='month_select_for_d_check')
    st.markdown("""
    <style>
    .stButton button {
        margin-top: 28px;  
    }
    </style>
    """, unsafe_allow_html=True)
    with col3:
        submit_btn = st.button('Submit')

    if submit_btn:
        i_year = selected_year
        i_month = selected_month
        #e_month = number_to_month(i_month)
        db_name= f'db_leads_{i_year}'   # t_year, t_month
        db = client[db_name]
        collection_name = f'{i_month}_{i_year}'
        collection = db[collection_name]
        data = list(collection.find())

        def reports(data,i_year,i_month,client):
            # Daily report
            daily_df = pd.DataFrame(data)
            daily_df = daily_df.drop('_id', axis=1, errors='ignore')    # daily_df = daily_df.drop('_id', axis=1)
            
            def daily_df_with_total (daily_df):    # 각 행의 합계 계산하여 'Row_Total' 열 추가
                st.session_state.daily_df_with_total = True
                daily_df.set_index(daily_df.columns[0], inplace=True)
                numeric_cols = daily_df.select_dtypes(include=['number']).columns 
                daily_df['Total'] = daily_df[numeric_cols].sum(axis=1)
                return daily_df
            
            daily_df_with_total = daily_df_with_total(daily_df)
            st.session_state.daily_df_with_total = daily_df_with_total
            
            def daily_col_sum_dataframe(daily_df):
                st.session_state.daily_col_sum_df = True
                column_sums = daily_df.sum(axis=0)
                column_sums_df = pd.DataFrame(column_sums, columns=['Total Leads']).transpose()
                return column_sums_df
    
            daily_col_sum_df = daily_col_sum_dataframe(daily_df)
            st.session_state.daily_col_sum_df = daily_col_sum_df
    
            # Weekly report
            df = pd.DataFrame(data)
            df = df.drop('_id', axis=1)
            def display_weekly_df(df,i_year):
                st.session_state.weekly_df = True
                def convert_to_date_wrapped(date_str):
                    return convert_to_date(date_str, i_year)
                df_melted = df.melt(id_vars=['program'], var_name='Date', value_name='Value')
                df_melted['Date'] = df_melted['Date'].apply(convert_to_date_wrapped)
                df_melted['Week'] = df_melted['Date'].dt.to_period('W').apply(lambda r: r.start_time)    # 날짜를 포함하는 주 식별 (각 날짜를 해당 주의 월요일로 변환)
                weekly_df = df_melted.groupby(['program', 'Week']).agg({'Value': 'sum'}).reset_index()    # 주별 데이터 집계 (예: 값의 합계)
                weekly_pivot_df = weekly_df.pivot(index='program', columns='Week', values='Value').fillna(0)    # 주(week) 기반 데이터프레임으로 Pivot
                weekly_pivot_df.loc['Total'] = weekly_pivot_df.sum()    # 각 열의 값을 합
                weekly_pivot_df['Total'] = weekly_pivot_df.sum(axis=1)  # 각 행의 값을 합
                return weekly_pivot_df
                
            weekly_df = display_weekly_df(df,i_year)
            st.session_state.weekly_df = weekly_df
            # Yearly report 
            yearly_df = calculate_total_leads(client, t_year, t_month)
            st.session_state.yearly_df = yearly_df
            
            yearly_df_ = yearly_df[yearly_df['month'] != 'Total']
            st.session_state.yearly_df_ = yearly_df_
            

        if selected_year<=t_year:
            en_month = int(month_to_number(selected_month))
            if selected_year == t_year:
                if en_month <= t_month:
                    reports(data,i_year,i_month,client)
                else:
                    st.session_state.daily_df_with_total = False
                    st.session_state.daily_col_sum_df = False
                    st.session_state.weekly_df = False
                    st.session_state.yearly_df = False   
                    st.session_state.yearly_df_ = False 
                    st.write("You have selected a date beyond today. \nThe data has not been updated yet and cannot be retrieved.")
            else:
                reports(data,i_year,i_month,client)
        else:
            st.session_state.daily_df_with_total = False
            st.session_state.daily_col_sum_df = False
            st.session_state.weekly_df = False
            st.session_state.yearly_df = False   
            st.session_state.yearly_df_ = False 
            st.write("You have selected a date beyond today. \nThe data has not been updated yet and cannot be retrieved.")
            
        
    if st.session_state.daily_df_with_total is not False:
        def highlight_non_zero(val):
            color = '#ACE5EE' if val != 0 else 'white'
            return f'background-color: {color}'
            
        st.write('Daily Report')
        st.dataframe(st.session_state.daily_df_with_total.style.applymap(highlight_non_zero))
        st.dataframe(st.session_state.daily_col_sum_df)
        st.write("Weekly Report")
        st.dataframe(st.session_state.weekly_df)
        st.write('Yearly Report')
        plt.figure(figsize=(15, 7))
        for y in range(2022,t_year+1):
            plt.plot(st.session_state.yearly_df_['month'], st.session_state.yearly_df_[f'{y}'], label=f'{y}', marker='o')
        plt.title('Monthly Data Over Years')
        plt.xlabel('Month')
        plt.ylabel('Values')
        plt.legend()
        
        tab1, tab2= st.tabs(['Table' , 'Graph'])
        with tab1:
          st.dataframe(st.session_state.yearly_df) 
        with tab2: 
          st.pyplot(plt)

    # #CPL 체크 화면
    st.markdown('---')
    st.subheader('CPLs')  # Have 37 categories, default = 1
    # st.markdown('---')
    years = list(range(2022, t_year + 1))
    # months = list(range(1, 13))
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
              'November', 'December']

    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
    with col1:
        st.write('From')
    with col2:
        selected_f_year = st.selectbox('Select Year', years, index=years.index(t_year), key='f_year_select_for_CPL')
    with col3:
        selected_f_month = st.selectbox('Select Month', months, index=t_month - 1, key='f_month_select_for_CPL')
    with col4:
        cal_btn = st.button('Calculate')

    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
    with col1:
        st.write('To')
    with col2:
        selected_t_year = st.selectbox('Select Year', years, index=years.index(t_year), key='t_year_select_for_CPL')
    with col3:
        selected_t_month = st.selectbox('Select Month', months, index=t_month - 1, key='t_month_select_for_CPL')
    with col4:
        st.write(' ')

    st.text("")    # 한줄 띄우기
    
    # 프로그램 라벨
    obj = st.session_state.get('daily_df_with_total', None)

    if 'daily_df_with_total' in st.session_state:
        daily_df_with_total = st.session_state['daily_df_with_total']
    else:
        daily_df_with_total = None  # 또는 pd.DataFrame()

    programs = daily_df_with_total.index.tolist()  # 전체 인덱스 리스트

    # 세션 상태 초기화
    if 'costs' not in st.session_state:
        st.session_state.costs = {}

    # 6열 그리드로 동적 text_input 생성
    N_COLS = 6
    n = len(programs)
    rows = math.ceil(n / N_COLS)

    idx_global = 0
    for r in range(rows):
        cols = st.columns([1, 1, 1, 1, 1, 1])
        start = r * N_COLS
        end = min(start + N_COLS, n)
        for c, label in enumerate(programs[start:end]):
            with cols[c]:
                key = f"cost::{label}"  # 유니크 키
                default = st.session_state.get(key, "1")
                val = st.text_input(label, value=str(default), key=key)
                st.session_state.costs[idx_global] = val
                idx_global += 1

    # 버튼 클릭 시 계산
    if cal_btn:
        f_year = selected_f_year
        f_month = month_to_number(selected_f_month)
        t_year = selected_t_year
        t_month = month_to_number(selected_t_month)

        # 주차별 리드 집계
        w_df = concat_d_df(client, programs, f_year, f_month, t_year, t_month)

        # 비용 딕셔너리 구성(입력값을 float로 변환, 실패 시 0.0)
        def to_float(x):
            try:
                return float(str(x).strip())
            except Exception:
                return 0.0

        cost_dic = {p: to_float(st.session_state.get(f"cost::{p}", "1")) for p in programs}

        # 6) w_df의 각 행을 해당 비용으로 나눠 CPL 유사 값을 계산
        #    w_df는 index가 프로그램 라벨, 열은 각 기간/주차 리드 수라고 가정
        w_df = w_df.copy()
        # 0 나눗셈 방지: 리드가 0이면 np.inf가 될 수 있으므로 후처리에서 np.nan으로 치환
        for p in w_df.index:
            cost = cost_dic.get(p, 0.0)
            if cost is not None:
                w_df.loc[p] = cost / w_df.loc[p].replace(0, np.nan)

        # 일자 합계 및 총 CPL 요약 d_df
        d_df = concat_d_df(client, programs, f_year, f_month, t_year, t_month)  # 원본 리드 재사용
        numeric_cols = d_df.select_dtypes(include='number').columns
        d_df['Total_Leads'] = d_df[numeric_cols].sum(axis=1)
        d_df['Cost'] = d_df.index.map(cost_dic)
        d_df['CPL'] = d_df['Cost'] / d_df['Total_Leads'].replace(0, np.nan)

        # 세션 저장
        st.session_state.w_cpl_df = w_df
        st.session_state.t_cpl_df = d_df[['Cost', 'Total_Leads', 'CPL']]

    if st.session_state.w_cpl_df is not False:
        st.write(f"{f_month}/{f_year}_{t_month}/{t_year}")
        st.write('weekly_cpl')
        st.write(st.session_state.w_cpl_df)
        st.write('Total_cpl')
        st.write(st.session_state.t_cpl_df)

    client.close()

if __name__ == "__main__":
    main()
