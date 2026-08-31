import streamlit as st
import os
from openai import OpenAI
from openai.types.containers import file_list_response

st.set_page_config(
    page_title="ai智能伴侣",
    page_icon="🥰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

# 大标题
st.title("AI智能伴侣")

st.logo("res/1.jpg")

# 系统提示词
system_prompt = """
        你叫%s，现在是用户的真实伴侣，请完全代入伴侣角色。:
        规则:
            1.每次只回1条消息
            2.禁止任何场景或状态描述性文字
            3.匹配用户的语言
            4.回复简短，像微信聊天一样
            5.有需要的话可以用颜文字,💕等emoji表情
            6.用符合伴侣性格的方式对话
            7.回复的内容，要充分体现伴侣的性格特征伴侣性格:
            - %s
            你必须严格遵守上述规则来回复用户。
    """

# 初始化聊天信息
if 'messages' not in st.session_state:
    st.session_state.messages = []

# 伴侣昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "A彪"

# 伴侣性格
if "nature" not in st.session_state:
    st.session_state.nature = "活泼温柔的江南姑娘"

# 展示聊天信息
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# 创建ai客户端
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

# 左侧栏
with st.sidebar:
    st.subheader("伴侣信息")

    nick_name = st.text_input("伴侣名称", placeholder="请输入伴侣名称", value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name

    nature = st.text_area("伴侣性格", placeholder="请输入伴侣性格", value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature

# 聊天输入框
prompt = st.chat_input("请输入您的问题：")
if prompt:
    st.chat_message("user").write(prompt)
    print("-------->调用ai大模型,提示词:", prompt)
    # 存储用户提示词
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用ai大模型生成回复
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.nick_name, st.session_state.nature)},
            *st.session_state.messages
        ],
        stream=True,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )

    # print("<---------- 大模型返回的结果:", response.choices[0].message.content)#非流式
    # st.chat_message("assistant").write(response.choices[0].message.content)

    # 流式输出大模型的回复
    response_message = st.empty()  # 创建一个空的聊天消息
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)

    # 存储大模型的回复
    st.session_state.messages.append({"role": "assistant", "content": full_response})
