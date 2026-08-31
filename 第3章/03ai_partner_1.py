import streamlit as st
import os
from openai import OpenAI


st.set_page_config(
    page_title="ai智能伴侣",
    page_icon="🦢",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

#大标题
st.title("AI智能伴侣")

st.logo("res/1.jpg")

#系统提示词
system_prompt = "你是一个言语恶毒的助手,回答问题的时候言语犀利一点"

#初始化聊天信息
if 'messages' not in st.session_state:
    st.session_state.messages = []

#展示聊天信息
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

#创建ai客户端
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),base_url="https://api.deepseek.com")

#聊天输入框
prompt = st.chat_input("请输入您的问题：")
if prompt:
    st.chat_message("user").write(prompt)
    print("-------->调用ai大模型,提示词:",prompt)
    #存储用户提示词
    st.session_state.messages.append({"role": "user", "content": prompt})

    #调用ai大模型生成回复
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )

    print("<---------- 大模型返回的结果:", response.choices[0].message.content)
    st.chat_message("assistant").write(response.choices[0].message.content)
    #存储大模型的回复
    st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})



