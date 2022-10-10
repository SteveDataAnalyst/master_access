import pickle
from pathlib import Path

import json
import requests
from streamlit_lottie import st_lottie
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from database_access import fetch_db
import streamlit_authenticator as stauth


st.set_page_config(initial_sidebar_state="collapsed",
                   layout="wide",
                   page_title="Scores Board",
                   page_icon="💯")

# ___ USER AUTHENTICATION
names = ["Peter Phuah", "Steven Chow"]
usernames = ["peterphuah", "stevenchow"]


# Load hashed passwords
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

credentials = {"usernames": {}}

for uname, name, pwd in zip(usernames, names, hashed_passwords):
    user_dict = {"name": name, "password": pwd}
    credentials["usernames"].update({uname: user_dict})

authenticator = stauth.Authenticate(credentials, "masteraccess_cookie", "random_key", cookie_expiry_days=1)

name, authentication_status, username = authenticator.login("login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:

    st.markdown(""" <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: visible;}
    footer:after {content:'Copyright @2022: Steven Production';
                  display:block;
                  position:relative;
                  color:tomato;
                  padding:5px;
                  top:3px;
    }
    </style> """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    div[data-testid="metric-container"] {
       background-color: rgba(153, 179, 245, 0.1);
       border: 1px solid rgba(28, 131, 225, 0.1);
       padding: 5% 5% 5% 10%;
       border-radius: 5px;
       color: rgb(30, 103, 119);
       overflow-wrap: break-word;
    }
    
    /* breakline for metric text         */
    div[data-testid="metric-container"] > label[data-testid="stMetricLabel"] > div {
       overflow-wrap: break-word;
       white-space: break-spaces;
       font-size: large;
       color: red;
    }
    </style>
    """
    , unsafe_allow_html=True)

    st.image("https://github.com/SteveDataAnalyst/SDO/raw/main/banner.JPG")
    st.title("🎯Scores Board")
    fetch = fetch_db()
    df = pd.DataFrame(fetch)


    def load_lottieurl(url: str):
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()

    def animation():
        lottie_hello = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_cx6nva8c.json")
        st_lottie(lottie_hello, key="hello", width=200)


    def date_select():
        uniquedates_list = list(df['date'].unique())
        box_selection = st.selectbox(
            "📅 Select a Date",
            uniquedates_list
        )
        return box_selection


    def number_participants(date):
        date_df = df.loc[df['date'] == date]
        count = date_df.shape[0]
        return count


    def average_score(date):
        avg_df = df.loc[df['date'] == date]
        avg = avg_df['result'].mean(axis = 0, skipna = False)
        avg = (avg/10) * 100
        return round(avg, 2)


    def plot(date):
        plot_df = df.loc[df['date'] == date]
        df_sorted_desc = plot_df.sort_values('result', ascending=False)
        df_sorted_desc = df_sorted_desc.iloc[:10]
        df_sorted_desc = df_sorted_desc.reset_index(drop=True)
        return df_sorted_desc


    def graph(df):
        figure1= plt.figure(figsize=(7, 4))
        sns.barplot(data=df, y='result', x='name')
        plt.title('Top 10 Participants with highest scores')
        plt.xlabel("Names")
        plt.xticks(rotation=30, horizontalalignment="center")
        plt.ylabel('Scores');
        st.pyplot(figure1)


    def calculate_correct_scam(date):
        cal_df = df.loc[df['date'] == date]
        total_cal_right = 0
        total_cal_wrong = 0
        for num in range(1, 8):
            cal_string = f'Q{num}_ans'
            cal_right = cal_df[cal_df[cal_string] == "Right"].shape[0]
            cal_wrong = cal_df[cal_df[cal_string] == "Wrong"].shape[0]
            total_cal_right += cal_right
            total_cal_wrong += cal_wrong
        total = total_cal_right + total_cal_wrong
        return round((total_cal_right/total) * 100, 2)


    def calculate_correct_general(date):
        cal_df = df.loc[df['date'] == date]
        total_cal_right = 0
        total_cal_wrong = 0
        for num in range(8, 11):
            cal_string = f'Q{num}_ans'
            cal_right = cal_df[cal_df[cal_string] == "Right"].shape[0]
            cal_wrong = cal_df[cal_df[cal_string] == "Wrong"].shape[0]
            total_cal_right += cal_right
            total_cal_wrong += cal_wrong
        total = total_cal_right + total_cal_wrong
        return round((total_cal_right/total) * 100, 2)


    def main_function_run():
        head1, head2 = st.columns(2)
        with head1:
            st.info(
                "🎈The available dates for viewing will only appear if there is at least **ONE** quiz entry of that date"
            )
            chosen_date = date_select()
        with head2:
            animation()
        placeholder = st.empty()
        with placeholder.container():
                if "load_state_scoreboard" and "selected_date" not in st.session_state:
                    st.session_state["load_state_scoreboard"] = False
                    st.session_state["selected_date"] = ""
                one, two, three, four = st.columns(4)
                with one:
                    number_of_participants = number_participants(chosen_date)
                    one.metric(
                        label = "Number Of Participants",
                        value = number_of_participants,
                    )
                with two:
                    avg = average_score(chosen_date)
                    two.metric(
                        label = "Average Total Score%",
                        value = f"{avg} %",
                    )
                with three:
                    scam_correct = calculate_correct_scam(chosen_date)
                    three.metric(
                        label = "Average Scam Score%",
                        value = f"{scam_correct} %",
                    )
                with four:
                    general_correct = calculate_correct_general(chosen_date)
                    four.metric(
                        label = "Average General Score%",
                        value = f"{general_correct} %",
                    )
                plot_df = plot(chosen_date)
                graph(plot_df)



    main_function_run()