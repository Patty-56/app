import streamlit as st
import os
import json
import pandas as pd

# 初始化資料夾與檔案
os.makedirs("data", exist_ok=True)
os.makedirs("story", exist_ok=True)
progress_path = "data/progress.json"
if not os.path.exists(progress_path):
    with open(progress_path, "w") as f:
        json.dump({
            "current_day": 1,
            "max_day": 1,
            "story_unlocked": [],
            "last_result": "none",
            "user_data": {}
        }, f, indent=4)

# 載入故事 Excel 檔
@st.cache_data
def load_story_data():
    path = "燈下謎影_完整21天.xlsx"
    if os.path.exists(path):
        return pd.read_excel(path)
    return None

def load_progress():
    with open(progress_path, "r") as f:
        return json.load(f)

def save_progress(data):
    with open(progress_path, "w") as f:
        json.dump(data, f, indent=4)

story_df = load_story_data()

st.set_page_config(page_title="水色之夜：整合版", layout="centered")
st.sidebar.title("🎭 選擇角色")
role = st.sidebar.radio("請選擇要扮演的角色：", ["甯（設計組）", "逸晨（程式組）", "芊芊（音效組）"])

st.title("🌌 水色之夜：健康解謎專題整合版")
st.markdown(f"#### 🎮 目前角色：**{role}**")
st.markdown("---")

progress = load_progress()
current_day = progress["current_day"]
st.markdown(f"### 📅 今天是第 {current_day} 天")

user_data = progress.get("user_data", {})
height = st.number_input("請輸入你的身高 (cm)：", value=user_data.get("height", 160))
weight = st.number_input("請輸入你的體重 (kg)：", value=user_data.get("weight", 50))
location = st.text_input("請輸入你所在的地區：", value=user_data.get("location", "台北"))

if st.button("📌 儲存個人資料"):
    progress["user_data"] = {"height": height, "weight": weight, "location": location}
    save_progress(progress)
    st.success("已儲存！")

suggested_water = weight * 30
suggested_steps = 8000
st.markdown(f"### 今日建議：\n- 建議喝水量：{suggested_water} cc\n- 建議步數：{suggested_steps} 步")

real_water = st.number_input("實際喝水量（cc）：", min_value=0)
real_steps = st.number_input("實際步數：", min_value=0)

if st.button("✅ 提交打卡"):
    if real_water >= suggested_water and real_steps >= suggested_steps:
        st.success("🎉 打卡成功，解鎖今日故事任務！")

        if story_df is not None:
            day_str = f"第{current_day}天"
            result = story_df[story_df["Day"] == day_str]

            if not result.empty:
                row = result.iloc[0]
                st.markdown(f"### 📖 【劇情內容】\n{row['LongStory']}")
                st.markdown(f"### 🔍 【線索提示】\n{row['ClueDetail']}")
                st.markdown(f"### 🎯 【推理解釋】\n{row['Explanation']}")
            else:
                st.warning(f"找不到 {day_str} 的故事內容。")
        else:
            st.error("⚠️ 無法載入故事檔案，請確認燈下謎影_完整21天.xlsx 是否存在於專案目錄下。")

        if current_day < 21:
            progress["current_day"] += 1
        progress["story_unlocked"].append(current_day)
        progress["last_result"] = "success"
        save_progress(progress)
    else:
        st.error("喝水或步數未達標，進度已重置！")
        progress["current_day"] = 1
        progress["story_unlocked"] = []
        progress["last_result"] = "fail"
        save_progress(progress)

st.markdown("---")
if st.checkbox("📖 顯示當前日劇情（開發用）"):
    if story_df is not None:
        day_str = f"第{current_day}天"
        result = story_df[story_df["Day"] == day_str]
        if not result.empty:
            st.text(result.iloc[0]["LongStory"])
        else:
            st.info("今天的劇情尚未建立。")
    else:
        st.warning("請先放入完整的故事 Excel 檔。")
