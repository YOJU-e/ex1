import sys
import os
import pandas as pd
import streamlit as st
from pymongo import MongoClient
from datetime import datetime, date
import time
 

'''
#uri = "mongodb+srv://@cluster0.egiqw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri)

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
'''

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

    # Goto_option_file_path = "./data/option_list.xlsx" #'./data/option_list.xlsx'
    # ckCat_csv_path = "./data/ck_PC1.csv" #"./data/ck_PC1.csv" # to get name of programs
    # Programs_csv_path = "./data/Category_s1.csv" # "./data/Category_s1.csv" # to get Programme(unique value)
    # programs_file_path = "./data/program_list.xlsx"
    # df_programs = pd.read_excel(programs_file_path, engine='openpyxl')
    programs = df_programs.iloc[:, 0].tolist()
    # chrome_driver_path = "chromedriver-win64/chromedriver.exe" # "./chromedriver-win64/chromedriver.exe"

    today_date = datetime.now()
    e_month = today_date.strftime('%B') #July
    t_month = today_date.month
    t_year = today_date.year

    # Session initialization
    if 'updated' not in st.session_state:
        st.session_state.updated = False
    # if 'daily_row_sum_df' not in st.session_state:
    #     st.session_state.daily_row_displayed = False
    if 'daily_col_sum_df' not in st.session_state:
        st.session_state.daily_col_displayed = False
    if 'daily_displayed' not in st.session_state:
        st.session_state.daily_displayed = False
    if 'weekly_displayed' not in st.session_state:
        st.session_state.weekly_displayed = False
    if 'w_cpl_df' not in st.session_state:
        st.session_state.w_cpl_df = False
    if 't_cpl_df' not in st.session_state:
        st.session_state.t_cpl_df = False

    # 옵션 파일 경로, 나머지 2개 파일 경로, 다운 디렉토리
    # 주소 입력 창
    if 'download_dir' not in st.session_state:
        st.session_state['download_dir'] = ''

    download_dir = st.text_input('Download Dir: ',"C:/Users/your_username/Downloads")
    if download_dir:
        st.session_state['download_dir'] = download_dir

    # 초기 설정 버튼!!!!!!!!!!!!!!!!!!!!!!!!!이거 처음 화면 열자마자 테이블 없으면 실행<- exe만들어본 이후에 한번 더 해보기
    if st.button('Initialization'):
        initialize_setup(Goto_option_file_path, download_dir,ckCat_csv_path,Programs_csv_path)

    # 업데이트 버튼
    years = list(range(2022, t_year + 1))  # From 2022 to now
    months = list(range(1, 13))  # From January to December

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        selected_year = st.selectbox('Select Year', years, index=years.index(t_year), key='year_select_for_update')
    with col2:
        selected_month = st.selectbox('Select Month', months, index=t_month-1, key='month_select_for_update')
    st.markdown("""
    <style>
    .stButton button {
        margin-top: 28px;  
    }
    </style>
    """, unsafe_allow_html=True)
    with col3:
        update_btn = st.button('Update')

    if update_btn:
        # 선택된 값을 변수에 저장
        i_year = selected_year
        i_month = selected_month
        e_month = number_to_month(i_month)
        db_name = f'EXDB_{i_year}.db'   # t_year, t_month
        table_name = f"{e_month}_{i_year}"
        update_records(Goto_option_file_path,i_year,i_month,download_dir,ckCat_csv_path,Programs_csv_path)
        st.write('Updated!')

    st.markdown('---')

    #데일리 리트 체크 화면
    st.subheader('Leads')
    # st.markdown('---')
    years = list(range(2022, t_year + 1))
    months = list(range(1, 13))

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        selected_year = st.selectbox('Select Year', years, index=years.index(t_year), key='year_select_for_d_check')
    with col2:
        selected_month = st.selectbox('Select Month', months, index=t_month-1, key='month_select_for_d_check')
    with col3:
        submit_btn = st.button('Submit')

    if submit_btn:
        i_year = selected_year
        i_month = selected_month
        e_month = number_to_month(i_month)
        db_name = f'EXDB_{i_year}.db'   # t_year, t_month
        table_name = f"{e_month}_{i_year}"
        print(i_month,i_year,e_month)
        daily_df = display_dataframe(db_name,table_name)
        # daily_row_sum_df = daily_row_sum_dataframe(db_name,table_name)
        daily_col_sum_df = daily_col_sum_dataframe(db_name,table_name)
        daily_df2 = daily_dataframe(db_name,table_name)
        # daily_df2.columns = pd.to_datetime(daily_df2.columns)
        # daily_df2.columns = [col.date() for col in daily_df2.columns]
        numeric_cols = daily_df2.select_dtypes(include=['number']).columns # 열 선택
        daily_df2['Total'] = daily_df2[numeric_cols].sum(axis=1)

        weekly_df = display_weekly_dataframe(daily_df,i_year)
        yearly_df = calculate_total_leads(t_year, t_month)
        yearly_df.set_index(yearly_df.columns[0], inplace=True)

        st.session_state.daily_df = daily_df
        st.session_state.daily_df2 = daily_df2
        st.session_state.daily_col_sum_df = daily_col_sum_df
        # st.session_state.daily_row_sum_df = daily_row_sum_df
        st.session_state.weekly_df = weekly_df
        st.session_state.yearly_df = yearly_df

    if st.session_state.weekly_displayed and 'daily_df2' in st.session_state:
        st.write(f'Daily Report')
        st.dataframe(st.session_state.daily_df2.style.set_sticky())
        st.dataframe(st.session_state.daily_col_sum_df)
        # st.dataframe(st.session_state.daily_row_sum_df)

        st.write("Weekly Report")
        st.dataframe(st.session_state.weekly_df)

        st.write('Yearly Report')
        st.dataframe(st.session_state.yearly_df)

    #CPL 체크 화면
    st.markdown('---')
    st.subheader('CPLs')    #Have 37 categories, default = 1
    # st.markdown('---')
    years = list(range(2022, t_year + 1))
    months = list(range(1, 13))

    col1, col2, col3, col4 = st.columns([1,2,2,1])
    with col1:
        st.write('From')
    with col2:
        selected_f_year = st.selectbox('Select Year', years, index=years.index(t_year), key='f_year_select_for_CPL')
    with col3:
        selected_f_month = st.selectbox('Select Month', months, index=t_month-1, key='f_month_select_for_CPL')
    with col4:
        cal_btn = st.button('Calculate')

    col1, col2, col3, col4 = st.columns([1,2,2,1])
    with col1:
        st.write('To')
    with col2:
        selected_t_year = st.selectbox('Select Year', years, index=years.index(t_year), key='t_year_select_for_CPL')
    with col3:
        selected_t_month = st.selectbox('Select Month', months, index=t_month-1, key='t_month_select_for_CPL')
    with col4:
        st.write(' ')

    program_list_df = pd.DataFrame([programs[i:i+6] for i in range(0, len(programs), 6)])
    if 'costs' not in st.session_state:
        st.session_state.costs = [''] * 37
    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
    with col1:
        cost_AcS_PG = st.text_input(f'{program_list_df.iloc[0,0]}', value='1', key=f'cost_{program_list_df.iloc[0,0]}')
        st.session_state.costs[0] = cost_AcS_PG
    with col2:
        cost_AcS_UG = st.text_input(f'{program_list_df.iloc[0,1]}', value='1', key=f'cost_{program_list_df.iloc[0,1]}')
        st.session_state.costs[1] = cost_AcS_UG
    with col3:
        cost_ApS_PG = st.text_input(f'{program_list_df.iloc[0,2]}', value='1', key=f'cost_{program_list_df.iloc[0,2]}')
        st.session_state.costs[2] = cost_ApS_PG
    with col4:
        cost_ApS_UG = st.text_input(f'{program_list_df.iloc[0,3]}', value='1', key=f'cost_{program_list_df.iloc[0,3]}')
        st.session_state.costs[3] = cost_ApS_UG
    with col5:
        cost_A_PG = st.text_input(f'{program_list_df.iloc[0,4]}', value='1', key=f'cost_{program_list_df.iloc[0,4]}')
        st.session_state.costs[4] = cost_A_PG
    with col6:
        cost_A_UG = st.text_input(f'{program_list_df.iloc[0,5]}', value='1', key=f'cost_{program_list_df.iloc[0,5]}')
        st.session_state.costs[5] = cost_A_UG

    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
    with col1:
        cost_B_PG = st.text_input(f'{program_list_df.iloc[1,0]}', value='1', key=f'cost_{program_list_df.iloc[1,0]}')
        st.session_state.costs[6] = cost_B_PG
    with col2:
        cost_B_UG = st.text_input(f'{program_list_df.iloc[1,1]}', value='1', key=f'cost_{program_list_df.iloc[1,1]}')
        st.session_state.costs[7] = cost_B_UG
    with col3:
        cost_E_PG = st.text_input(f'{program_list_df.iloc[1,2]}', value='1', key=f'cost_{program_list_df.iloc[1,2]}')
        st.session_state.costs[8] = cost_E_PG
    with col4:
        cost_E_UG = st.text_input(f'{program_list_df.iloc[1,3]}', value='1', key=f'cost_{program_list_df.iloc[1,3]}')
        st.session_state.costs[9] = cost_E_UG
    with col5:
        cost_FMHS_PG = st.text_input(f'{program_list_df.iloc[1,4]}', value='1', key=f'cost_{program_list_df.iloc[1,4]}')
        st.session_state.costs[10] = cost_FMHS_PG
    with col6:
        cost_FMHS_UG = st.text_input(f'{program_list_df.iloc[1,5]}', value='1', key=f'cost_{program_list_df.iloc[1,5]}')
        st.session_state.costs[11] = cost_FMHS_UG

    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
    with col1:
        cost_FMHS_UG_N = st.text_input(f'{program_list_df.iloc[2,0]}', value='1', key=f'cost_{program_list_df.iloc[2,0]}')
        st.session_state.costs[12] = cost_FMHS_UG_N
    with col2:
        cost_FOSSLA_PG = st.text_input(f'{program_list_df.iloc[2,1]}', value='1', key=f'cost_{program_list_df.iloc[2,1]}')
        st.session_state.costs[13] = cost_FOSSLA_PG
    with col3:
        cost_FOSSLA_UG = st.text_input(f'{program_list_df.iloc[2,2]}', value='1', key=f'cost_{program_list_df.iloc[2,2]}')
        st.session_state.costs[14] = cost_FOSSLA_UG
    with col4:
        cost_F_art = st.text_input(f'{program_list_df.iloc[2,3]}', value='1', key=f'cost_{program_list_df.iloc[2,3]}')
        st.session_state.costs[15] = cost_F_art
    with col5:
        cost_F_sci = st.text_input(f'{program_list_df.iloc[2,4]}', value='1', key=f'cost_{program_list_df.iloc[2,4]}')
        st.session_state.costs[16] = cost_F_sci
    with col6:
        cost_FPS_PG = st.text_input(f'{program_list_df.iloc[2,5]}', value='1', key=f'cost_{program_list_df.iloc[2,5]}')
        st.session_state.costs[17] = cost_FPS_PG

    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
    with col1:
        cost_FPS_UG = st.text_input(f'{program_list_df.iloc[3,0]}', value='1', key=f'cost_{program_list_df.iloc[3,0]}')
        st.session_state.costs[18] = cost_FPS_UG
    with col2:
        cost_GBS_PG = st.text_input(f'{program_list_df.iloc[3,1]}', value='1', key=f'cost_{program_list_df.iloc[3,1]}')
        st.session_state.costs[19] = cost_GBS_PG
    with col3:
        cost_H_PG = st.text_input(f'{program_list_df.iloc[3,2]}', value='1', key=f'cost_{program_list_df.iloc[3,2]}')
        st.session_state.costs[20] = cost_H_PG
    with col4:
        cost_H_UG = st.text_input(f'{program_list_df.iloc[3,3]}', value='1', key=f'cost_{program_list_df.iloc[3,3]}')
        st.session_state.costs[21] = cost_H_UG
    with col5:
        cost_IASDA_PG = st.text_input(f'{program_list_df.iloc[3,4]}', value='1', key=f'cost_{program_list_df.iloc[3,4]}')
        st.session_state.costs[22] = cost_IASDA_PG
    with col6:
        cost_IASDA_UG = st.text_input(f'{program_list_df.iloc[3,5]}', value='1', key=f'cost_{program_list_df.iloc[3,5]}')
        st.session_state.costs[23] = cost_IASDA_UG

    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
    with col1:
        cost_ICAD_PG = st.text_input(f'{program_list_df.iloc[4,0]}', value='1', key=f'cost_{program_list_df.iloc[4,0]}')
        st.session_state.costs[24] = cost_ICAD_PG
    with col2:
        cost_ICAD_UG = st.text_input(f'{program_list_df.iloc[4,1]}', value='1', key=f'cost_{program_list_df.iloc[4,1]}')
        st.session_state.costs[25] = cost_ICAD_UG
    with col3:
        cost_IMUS_PG = st.text_input(f'{program_list_df.iloc[4,2]}', value='1', key=f'cost_{program_list_df.iloc[4,2]}')
        st.session_state.costs[26] = cost_IMUS_PG
    with col4:
        cost_IMUS_UG = st.text_input(f'{program_list_df.iloc[4,3]}', value='1', key=f'cost_{program_list_df.iloc[4,3]}')
        st.session_state.costs[27] = cost_IMUS_UG
    with col5:
        cost_IT_PG = st.text_input(f'{program_list_df.iloc[4,4]}', value='1', key=f'cost_{program_list_df.iloc[4,4]}')
        st.session_state.costs[28] = cost_IT_PG
    with col6:
        cost_IT_UG = st.text_input(f'{program_list_df.iloc[4,5]}', value='1', key=f'cost_{program_list_df.iloc[4,5]}')
        st.session_state.costs[29] = cost_IT_UG

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        cost_MPhD = st.text_input(f'{program_list_df.iloc[5,0]}', value='1', key=f'cost_{program_list_df.iloc[5,0]}')
        st.session_state.costs[30] = cost_MPhD
    with col2:
        cost_SEC_GS = st.text_input(f'{program_list_df.iloc[5,1]}', value='1', key=f'cost_{program_list_df.iloc[5,1]}')
        st.session_state.costs[31] = cost_SEC_GS
    with col3:
        cost_SEC_F = st.text_input(f'{program_list_df.iloc[5,2]}', value='1', key=f'cost_{program_list_df.iloc[5,2]}')
        st.session_state.costs[32] = cost_SEC_F
    with col4:
        cost_SEC_DF = st.text_input(f'{program_list_df.iloc[5,3]}', value='1', key=f'cost_{program_list_df.iloc[5,3]}')
        st.session_state.costs[33] = cost_SEC_DF

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        cost_SEC_MS = st.text_input(f'{program_list_df.iloc[5,4]}', value='1', key=f'cost_{program_list_df.iloc[5,4]}')
        st.session_state.costs[34] = cost_SEC_MS
    with col2:
        cost_SEC_OEI = st.text_input(f'{program_list_df.iloc[5,5]}', value='1', key=f'cost_{program_list_df.iloc[5,5]}')
        st.session_state.costs[35] = cost_SEC_OEI
    with col3:
        cost_SEC_UEC = st.text_input(f'{program_list_df.iloc[6,0]}', value='1', key=f'cost_{program_list_df.iloc[6,0]}')
        st.session_state.costs[36] = cost_SEC_UEC

    if cal_btn:
        f_year = selected_f_year
        f_month = selected_f_month
        t_year = selected_t_year
        t_month = selected_t_month

        # weekly cpl 계산
        w_df = concat_d_df(programs, f_year, f_month, t_year, t_month)
        # st.write(w_df)
        # w_df = display_weekly_df2(d_df,i_year)
        column_names = w_df.columns.tolist()
        index_values = w_df.index.tolist()

        for p in index_values:
            if p == 'Actuarial Science (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Actuarial Science (PG)')
                    cost = float(cost_AcS_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Actuarial Science (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Actuarial Science (UG)')
                    cost = float(cost_AcS_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Applied Sciences (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Applied Sciences (PG)')
                    cost = float(cost_ApS_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Applied Sciences (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Applied Sciences (UG)')
                    cost = float(cost_ApS_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Architecture (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Architecture (PG)')
                    cost = float(cost_A_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Architecture (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Architecture (UG)')
                    cost = float(cost_A_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Business (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Business (PG)')
                    cost = float(cost_B_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Business (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Business (UG)')
                    cost = float(cost_B_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Engineering (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Engineering (PG)')
                    cost = float(cost_E_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Engineering (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Engineering (UG)')
                    cost = float(cost_E_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'FMHS (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('FMHS (PG)')
                    cost = float(cost_FMHS_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'FMHS (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('FMHS (UG)')
                    cost = float(cost_FMHS_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'FMHS (UG) - Nursing':
                for c in range(0, len(column_names)):
                    i = index_values.index('FMHS (UG) - Nursing')
                    cost = float(cost_FMHS_UG_N)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'FOSSLA (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('FOSSLA (PG)')
                    cost = float(cost_FOSSLA_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'FOSSLA (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('FOSSLA (UG)')
                    cost = float(cost_FOSSLA_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Foundation in Arts':
                for c in range(0, len(column_names)):
                    i = index_values.index('Foundation in Arts')
                    cost = float(cost_F_art)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Foundation in Science':
                for c in range(0, len(column_names)):
                    i = index_values.index('Foundation in Science')
                    cost = float(cost_F_sci)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'FPS (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('FPS (PG)')
                    cost = float(cost_FPS_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'FPS (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('FPS (UG)')
                    cost = float(cost_FPS_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'GBS (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('GBS (PG)')
                    cost = float(cost_GBS_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Hospitality (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Hospitality (PG)')
                    cost = float(cost_H_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Hospitality (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('Hospitality (UG)')
                    cost = float(cost_H_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'IASDA (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('IASDA (PG)')
                    cost = float(cost_IASDA_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'IASDA (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('IASDA (UG)')
                    cost = float(cost_IASDA_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'ICAD (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('ICAD (PG)')
                    cost = float(cost_ICAD_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'ICAD (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('ICAD (UG)')
                    cost = float(cost_ICAD_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'IMUS (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('IMUS (PG)')
                    cost = float(cost_IMUS_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'IMUS (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('IMUS (UG)')
                    cost = float(cost_IMUS_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'IT (PG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('IT (PG)')
                    cost = float(cost_IT_PG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'IT (UG)':
                for c in range(0, len(column_names)):
                    i = index_values.index('IT (UG)')
                    cost = float(cost_IT_UG)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'Master & PhD Programme':
                for c in range(0, len(column_names)):
                    i = index_values.index('Master & PhD Programme')
                    cost = float(cost_MPhD)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'SEC-General Scholarship':
                for c in range(0, len(column_names)):
                    i = index_values.index('SEC-General Scholarship')
                    cost = float(cost_SEC_GS)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'SEC-Foundation':
                for c in range(0, len(column_names)):
                    i = index_values.index('SEC-Foundation')
                    cost = float(cost_SEC_F)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'SEC-Diploma & Foundation':
                for c in range(0, len(column_names)):
                    i = index_values.index('SEC-Diploma & Foundation')
                    cost = float(cost_SEC_DF)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'SEC-MARA Scholarship':
                for c in range(0, len(column_names)):
                    i = index_values.index('SEC-MARA Scholarship')
                    cost = float(cost_SEC_MS)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'SEC-Open Day/Enrolment Day/Info Day':
                for c in range(0, len(column_names)):
                    i = index_values.index('SEC-Open Day/Enrolment Day/Info Day')
                    cost = float(cost_SEC_OEI)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value
            if p == 'SEC-UEC':
                for c in range(0, len(column_names)):
                    i = index_values.index('SEC-UEC')
                    cost = float(cost_SEC_UEC)
                    value = cost/w_df.iloc[i, c]
                    w_df.iloc[i, c] = value

        st.write(f'{f_month}/{f_year}_{t_month}/{t_year}')
        if st.session_state.w_cpl_df in st.session_state:
            st.session_state.t_cpl_df = True
        d_df = concat_d_df(programs, f_year, f_month, t_year, t_month)
        numeric_cols = d_df.select_dtypes(include=['number']).columns # 열 선택
        d_df['Total_Leads'] = d_df[numeric_cols].sum(axis=1)
        # st.write(d_df)
        #cost
        cost_dic = {}
        for p in index_values:
            if p == 'Actuarial Science (PG)':
                i = index_values.index('Actuarial Science (PG)')
                cost = float(cost_AcS_PG)
                cost_dic[p]=cost
            if p == 'Actuarial Science (UG)':
                    i = index_values.index('Actuarial Science (UG)')
                    cost = float(cost_AcS_UG)
                    cost_dic[p]=cost
            if p == 'Applied Sciences (PG)':
                    i = index_values.index('Applied Sciences (PG)')
                    cost = float(cost_ApS_PG)
                    cost_dic[p]=cost
            if p == 'Applied Sciences (UG)':
                    i = index_values.index('Applied Sciences (UG)')
                    cost = float(cost_ApS_UG)
                    cost_dic[p]=cost
            if p == 'Architecture (PG)':
                    i = index_values.index('Architecture (PG)')
                    cost = float(cost_A_PG)
                    cost_dic[p]=cost
            if p == 'Architecture (UG)':
                    i = index_values.index('Architecture (UG)')
                    cost = float(cost_A_UG)
                    cost_dic[p]=cost
            if p == 'Business (PG)':
                    cost_dic[p]=cost
                    i = index_values.index('Business (PG)')
                    cost = float(cost_B_PG)
                    cost_dic[p]=cost
            if p == 'Business (UG)':
                    i = index_values.index('Business (UG)')
                    cost = float(cost_B_UG)
                    cost_dic[p]=cost
            if p == 'Engineering (PG)':
                    i = index_values.index('Engineering (PG)')
                    cost = float(cost_E_PG)
                    cost_dic[p]=cost
            if p == 'Engineering (UG)':
                    i = index_values.index('Engineering (UG)')
                    cost = float(cost_E_UG)
                    cost_dic[p]=cost
            if p == 'FMHS (PG)':
                    i = index_values.index('FMHS (PG)')
                    cost = float(cost_FMHS_PG)
                    cost_dic[p]=cost
            if p == 'FMHS (UG)':
                    i = index_values.index('FMHS (UG)')
                    cost = float(cost_FMHS_UG)
                    cost_dic[p]=cost
            if p == 'FMHS (UG) - Nursing':
                    i = index_values.index('FMHS (UG) - Nursing')
                    cost = float(cost_FMHS_UG_N)
                    cost_dic[p]=cost
            if p == 'FOSSLA (PG)':
                    i = index_values.index('FOSSLA (PG)')
                    cost = float(cost_FOSSLA_PG)
                    cost_dic[p]=cost
            if p == 'FOSSLA (UG)':
                    i = index_values.index('FOSSLA (UG)')
                    cost = float(cost_FOSSLA_UG)
                    cost_dic[p]=cost
            if p == 'Foundation in Arts':
                    i = index_values.index('Foundation in Arts')
                    cost = float(cost_F_art)
                    cost_dic[p]=cost
            if p == 'Foundation in Science':
                    i = index_values.index('Foundation in Science')
                    cost = float(cost_F_sci)
                    cost_dic[p]=cost
            if p == 'FPS (PG)':
                    i = index_values.index('FPS (PG)')
                    cost = float(cost_FPS_PG)
                    cost_dic[p]=cost
            if p == 'FPS (UG)':
                    i = index_values.index('FPS (UG)')
                    cost = float(cost_FPS_UG)
                    cost_dic[p]=cost
            if p == 'GBS (PG)':
                    i = index_values.index('GBS (PG)')
                    cost = float(cost_GBS_PG)
                    cost_dic[p]=cost
            if p == 'Hospitality (PG)':
                    i = index_values.index('Hospitality (PG)')
                    cost = float(cost_H_PG)
                    cost_dic[p]=cost
            if p == 'Hospitality (UG)':
                    i = index_values.index('Hospitality (UG)')
                    cost = float(cost_H_UG)
                    cost_dic[p]=cost
            if p == 'IASDA (PG)':
                    i = index_values.index('IASDA (PG)')
                    cost = float(cost_IASDA_PG)
                    cost_dic[p]=cost
            if p == 'IASDA (UG)':
                    i = index_values.index('IASDA (UG)')
                    cost = float(cost_IASDA_UG)
                    cost_dic[p]=cost
            if p == 'ICAD (PG)':
                    i = index_values.index('ICAD (PG)')
                    cost = float(cost_ICAD_PG)
                    cost_dic[p]=cost
            if p == 'ICAD (UG)':
                    i = index_values.index('ICAD (UG)')
                    cost = float(cost_ICAD_UG)
                    cost_dic[p]=cost
            if p == 'IMUS (PG)':
                    i = index_values.index('IMUS (PG)')
                    cost = float(cost_IMUS_PG)
                    cost_dic[p]=cost
            if p == 'IMUS (UG)':
                    i = index_values.index('IMUS (UG)')
                    cost = float(cost_IMUS_UG)
                    cost_dic[p]=cost
            if p == 'IT (PG)':
                    i = index_values.index('IT (PG)')
                    cost = float(cost_IT_PG)
                    cost_dic[p]=cost
            if p == 'IT (UG)':
                    i = index_values.index('IT (UG)')
                    cost = float(cost_IT_UG)
                    cost_dic[p]=cost
            if p == 'Master & PhD Programme':
                    i = index_values.index('Master & PhD Programme')
                    cost = float(cost_MPhD)
                    cost_dic[p]=cost
            if p == 'SEC-General Scholarship':
                    i = index_values.index('SEC-General Scholarship')
                    cost = float(cost_SEC_GS)
                    cost_dic[p]=cost
            if p == 'SEC-Foundation':
                    i = index_values.index('SEC-Foundation')
                    cost = float(cost_SEC_F)
                    cost_dic[p]=cost
            if p == 'SEC-Diploma & Foundation':
                    i = index_values.index('SEC-Diploma & Foundation')
                    cost = float(cost_SEC_DF)
                    cost_dic[p]=cost
            if p == 'SEC-MARA Scholarship':
                    i = index_values.index('SEC-MARA Scholarship')
                    cost = float(cost_SEC_MS)
                    cost_dic[p]=cost
            if p == 'SEC-Open Day/Enrolment Day/Info Day':
                    i = index_values.index('SEC-Open Day/Enrolment Day/Info Day')
                    cost = float(cost_SEC_OEI)
                    cost_dic[p]=cost
            if p == 'SEC-UEC':
                    i = index_values.index('SEC-UEC')
                    cost = float(cost_SEC_UEC)
                    cost_dic[p]=cost
        d_df['Cost'] = d_df.index.map(cost_dic)

        #(Total) CPL
        d_df['CPL'] = d_df['Cost'] / d_df['Total_Leads']
        t_df = pd.DataFrame()
        t_df = d_df[['Cost','Total_Leads','CPL']]
        st.session_state.w_cpl_df = w_df
        st.session_state.t_cpl_df = t_df

    if st.session_state.w_cpl_df is not False:
        st.write(st.session_state.w_cpl_df)
        st.write(st.session_state.t_cpl_df)

if __name__ == "__main__":
    main()