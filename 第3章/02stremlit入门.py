import streamlit as st

import streamlit as st

st.set_page_config(
    page_title="streamlit入门",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

st.title("streamlit 入门")
st.header("streamlit 一级标题")
st.subheader("streamlit 二级标题")

st.write("-------------------")
st.write("#################################################")

st.logo("res/1.jpg")

student_data = {
    "姓名": ["王琳", "张三", "罗贝", "李四"],
    "学号": ["001", "002", "003", "004"]
}
st.table(student_data)


