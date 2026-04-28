import  streamlit as st
import os
from openai import OpenAI
import  datetime
import json
from dotenv import load_dotenv
# 从环境变量里读取 API Key
api_key = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com")
#生成会话名字函数
def create_session_name():
    return datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
#保存会话信息的函数
def save_session():
    # stretch填满整个容器
    # 如果新建会话，则保存当前会话--整理好保存的数据用data存储，创建datas目录保存名字为对应时间的json文件
        # 1.保存当前会话
        if st.session_state.current_session:
            data = {
                "nick_name": st.session_state.nick_name,
                "character": st.session_state.character,
                "current_session": st.session_state.current_session,
                "message": st.session_state.message
            }
        # 创建一个文件保存json格式的信息
        # os.path.exists先看看当前文件夹里，有没有一个叫 “datas” 的文件夹。
        if not os.path.exists("datas"):
            os.mkdir("datas")
        with open(f"datas/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
#加载对话列表
def load_sessions():
    session_list=[]
    if os.path.exists("datas"):
        file_list=os.listdir("datas")
        for file in file_list:
            if file.endswith(".json"):
                session_list.append(file[:-5])
    session_list.sort(reverse=True)
    return session_list
#删除对应会话
def delete_session(session_name):
    try:
        if os.path.exists(f"datas/{session_name}.json"):
            #删除文件操作
            os.remove(f"datas/{session_name}.json")
    except Exception as e:
        print("删除会话失败❌")
#渲染指定对话列表
def load_session(session_name):
    try:
        if os.path.exists(f"datas/{session_name}.json"):
            with open(f"datas/{session_name}.json","r",encoding="utf-8") as f:
                session_data=json.load(f)
                st.session_state.message=session_data["message"]
                st.session_state.nick_name=session_data["nick_name"]
                st.session_state.character=session_data["character"]
                st.session_state.current_session=session_name
    except Exception as e:
        st.error(e)
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)
#初始化聊天消息
#如果message不在session_state（用于存储多个对象）中，则创建一个
if "message"  not in st.session_state:
    st.session_state.message=[]
if "nick_name" not in st.session_state:
    st.session_state.nick_name="小甜甜"
if  "character" not in st.session_state:
    st.session_state.character="活泼开朗的南方姑娘"
if "current_session" not  in st.session_state:
    #strftime格式化
    #Y: 年,m:月,d:日,H:时,M:分,S:秒
    st.session_state.current_session=create_session_name()

#大标题
st.title("AI智能伴侣")
#左侧侧边栏
#with st.sidebar:上下文管理器，在这个缩进丽写段代码，左侧的侧边栏就会生效，不用一行一行加sidebar
with st.sidebar:
    st.subheader("AI控制面板")
    if st.button("📔新建会话", width="stretch"):
        save_session()
        #   2.创建新的对话
        #如果有内容，不再创建新的文件
        if st.session_state.message:
            st.session_state.message=[]
            st.session_state.current_session=create_session_name()
            save_session()
            st.rerun()
    #会话历史
    st.text("历史会话")
    #布局
    co1,co2 = st.columns([4,1])
    session_list=load_sessions()
    for session in session_list:
        with co1:
            #加载
            if st.button(session,icon="🗒️", width="stretch",key=f"load_{session}",type="primary" if st.session_state.current_session==session else "secondary"):
                if st.session_state.message:
                    save_session()
                load_session(session)
                st.rerun()
        with co2:
            #删除

            if st.button("", icon="❌", width="stretch",key=f"delete_{session}"):
                pass
                #如果删除当前会话，建立新对话，如果删除其他会话，界面不变
                delete_session(session)
                if st.session_state.current_session==session:
                    st.session_state.message=[]
                    st.session_state.current_session=create_session_name()
                st.rerun()
#分割线
    st.divider()

    st.subheader("伴侣信息")
    nick_name=st.text_input("昵称",placeholder="请输入昵称",value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name=nick_name
    character=st.text_area("性格",placeholder="请输入性格",value=st.session_state.character)
    if character:
        st.session_state.character=character
#系统提示词
system_prompt = f"""
你叫{st.session_state.nick_name}，现在是用户的真实伴侣，请完全代入伴侣角色。

规则：
1. 每次只回1条消息
2. 禁止任何场景或状态描述性文字
3. 匹配用户的语言
5. 有需要的话可以用❤️🌸等emoji表情
6. 用符合伴侣性格的方式对话
7. 回复的内容，要充分体现伴侣的性格特征

伴侣性格：
- {st.session_state.character}

你必须严格遵守上述规则来回复用户。
"""
#展示聊天信息
for i in st.session_state.message:
    if i["role"]=="user":
       st.chat_message("user").write(i["content"])
    else:
        st.chat_message("assistant").write(i["content"])

#消息输入框
prompt=st.chat_input("请输入您的问题")
if prompt :
    st.chat_message("user").write(prompt)
    print(f"调试词:{prompt}")
    st.session_state.message.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            *st.session_state.message
        ],
        stream=True
    )

    #非流式输出的结果
    # print(f"调试结果:{response.choices[0].message.content}")
    # st.chat_message("assistant").write(response.choices[0].message.content)
    # st.session_state.message.append({"role":"assistant","content":response.choices[0].message.content})


#流式输出
    #利用response_messge先进行空位占位，然后用full_content进行填充，最后将full_content写入response_messge
    response_messge=st.empty()
    full_content=""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content=chunk.choices[0].delta.content
            full_content+=content
            response_messge.chat_message("assistant").write(full_content)
    st.session_state.message.append({"role":"assistant","content":full_content})

