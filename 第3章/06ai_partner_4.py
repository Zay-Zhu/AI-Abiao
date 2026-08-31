import streamlit as st
import os
from openai import OpenAI
from openai.types.containers import file_list_response
from datetime import datetime
import json

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


#生成会话标识
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# 保存会话信息
def save_session():
    # 1.保存当前会话信息
    if st.session_state.current_session:
        # 构建新的会话对象
        st.session_data = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }

        # 如果sessions 目录不存在,则创建
        if not os.path.exists("sessions"):
            os.makedirs("sessions")

        # 保存会话数据
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(st.session_data, f, ensure_ascii=False, indent=2)

#加载会话列表
def load_sessions():
    session_list = []
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    return session_list

# 加载指定会话信息
def load_session(session_name):
        if os.path.exists(f"sessions/{session_name}.json"):
            #读取数据
            try:
                with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
                    session_data = json.load(f)
                    st.session_state.nick_name = session_data["nick_name"]
                    st.session_state.nature = session_data["nature"]
                    st.session_state.current_session = session_name
                    st.session_state.messages = session_data["messages"]
            except Exception as e:
                st.error(f"加载会话{session_name}失败!")


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

# 会话标识
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()

# 展示聊天信息
st.text(f"会话名称:{st.session_state.current_session}")
for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# 创建ai客户端
client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

# 左侧栏
with st.sidebar:
    st.subheader("AI控制面板")

    # 新建会话
    if st.button("新建会话", width="stretch", icon="✏️"):
        # 1.保存当前会话信息
        save_session()

        # 2.新建会话
        if st.session_state.messages:#如果当前会话非空True 否则False
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()
            st.rerun()


    #会话历史
    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1, col2 = st.columns([4,1])
        with col1:
            #加载会话信息

            if st.button(session, width="stretch", icon="📃", key=f"load_{session}",type = "primary" if session == st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun()
        with col2:
            #删除会话
            if st.button("", width="stretch", icon="❌", key=f"delete_{session}"):
                pass


# 伴侣信息
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

    # 保存当前会话信息
    save_session()

