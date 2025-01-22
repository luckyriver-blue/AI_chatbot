import streamlit as st
from read_secret_data import openai_key, firebase_project_settings
import firebase_admin
from firebase_admin import credentials, firestore
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from style_and_javascript.style import hide_st_style, message_style, input_style
from style_and_javascript.javascript import scroll_js
import datetime, pytz

#スタイリング
st.markdown(hide_st_style, unsafe_allow_html=True)
st.markdown(message_style, unsafe_allow_html=True)
st.markdown(input_style, unsafe_allow_html=True)


# Firebase Admin SDKの初期化
if not firebase_admin._apps:
  cred = credentials.Certificate(firebase_project_settings)
  firebase_admin.initialize_app(cred)

# Firestoreのインスタンスを取得
db = firestore.client()


# セッションステートの初期化
if 'user_id' not in st.session_state:
  st.session_state['user_id'] = None
if 'prompt_bigfive' not in st.session_state:
  st.session_state['prompt_bigfive'] = {}
if "input" not in st.session_state:
    st.session_state['input'] = ""
if 'placeholder' not in st.session_state:
  st.session_state['placeholder'] = ""


#会話パート何日間行うか
talk_days = 5
#5日間の会話パート
now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
#会話パート開始日
start_day = "2025-01-22" #仮
start_day_obj = datetime.datetime.strptime(start_day, "%Y-%m-%d")
# タイムゾーンを付与
start_day_obj = pytz.timezone('Asia/Tokyo').localize(start_day_obj)
#今日が会話パート何日目か計算
now_day = (now - start_day_obj).days + 1


#Firebaseから有効な参加者IDを取得する関数
def get_valid_ids():
  valid_ids = []
  users = db.collection('users').stream()

  for user in users:
    valid_ids.append(user.id)
  
  return valid_ids

valid_ids = get_valid_ids() #有効なユーザーID
#クエリパラメータからuser_idを取得（あれば）
query_params = st.experimental_get_query_params()
if "user_id" in query_params:
  query_user_id = query_params.get('user_id', [None])[0]
  if query_user_id != st.session_state['user_id']:
    if query_user_id not in valid_ids:
      st.session_state["user_id"] = None
    else:
      st.session_state["user_id"] = query_user_id
      st.rerun()
else:
  st.session_state['user_id'] = None


#firebaseからuser_idを通してビッグファイブデータと会話データを取得する
def read_firebase_bigfive_data():
  doc_ref = db.collection("users").document(st.session_state['user_id'])
  doc = doc_ref.get()
  data = doc.to_dict()
  if data is None:
    prompt_bigfive = {}
  else:
    prompt_bigfive = data.get('bigfive', {})

  return prompt_bigfive

def read_firebase_talk_data():
  doc_ref = db.collection("users").document(st.session_state['user_id'])
  doc = doc_ref.get()
  data = doc.to_dict()
  if data is None:
    talk_data = {}
  else:
    talk_day_data = data.get('messages', {}).get(f'day{now_day}', {})
    talk_data_temporary = talk_day_data.get('messages', {})
    talk_data = dict(sorted(talk_data_temporary.items(), key=lambda item: int(item[0])))

  return talk_data


if st.session_state['prompt_bigfive'] == {}:
  prompt_bigfive = read_firebase_bigfive_data()
  st.session_state['prompt_bigfive'] = prompt_bigfive
else:
  prompt_bigfive = st.session_state['prompt_bigfive']


# prompt_bigfiveの各値を変数として渡す
extraversion = prompt_bigfive.get("extraversion", "N/A")
agreeableness = prompt_bigfive.get("agreeableness", "N/A")
conscientiousness = prompt_bigfive.get("conscientiousness", "N/A")
neuroticism = prompt_bigfive.get("neuroticism", "N/A")
openness = prompt_bigfive.get("openness", "N/A")

# プロンプトテンプレートの設定
prompt_template = PromptTemplate(
  input_variables=["history"],
  template=f"""
    ユーザーの性格：
    Extraversion: {extraversion}, 
    Agreeableness: {agreeableness}, 
    Conscientiousness: {conscientiousness}, 
    Neuroticism: {neuroticism}, 
    Openness: {openness}

    ユーザーの性格を参照して、ユーザーにとって最適な会話を心がけてください。
    適度な問いかけを行って、会話を促進してください。
    ユーザーの性格のスコアに直接的に言及しないでください。
    ユーザーのことをユーザーと呼ばないでください。
    200文字以内で回答してください。
    以下は会話の履歴です：\n{{history}}
  """
)


gpt = ChatOpenAI(
    model_name="gpt-4o",
    max_tokens=1024,
    temperature=0.5,
    frequency_penalty=0.02,
    openai_api_key=openai_key
)


#上記のプロンプトを用いて、ユーザーの入力に対する応答を取得する関数
def get_response(history):
  prompt = prompt_template.format(history=history)
  response = gpt.predict(prompt)
  return response



# 会話メッセージの履歴を表示
def show_messages():
  messages = read_firebase_talk_data()
  if messages == {}:
    add_data(st.session_state['user_id'], {"messages": {f"day{now_day}": {"messages": {"0": {"role": "AI", "content": "今日は何がありましたか？"}}}}})
    messages = read_firebase_talk_data()
  for i, message in enumerate(messages.values()):
    if message["role"] == "Human":
      st.markdown(f'''
      <div style="display: flex;">
        <div style="display: flex; margin-left: auto; max-width: 65%;">
          <div class="messages">{message["content"]}</div>
        </div>
      </div>
      ''', unsafe_allow_html=True)
      #会話が人間で終わっていたら応答を生成する
      if i == len(messages) - 1:
        with st.chat_message("assistant"):
          with st.spinner("応答を生成しています"):
            response = get_response(messages)
            add_data(st.session_state['user_id'], {"messages": {f"day{now_day}": {"messages": {str(i+1): {"role": "AI", "content": response}}}}})
          st.markdown(f'<div style="max-width: 80%;" class="messages">{response}</div>', unsafe_allow_html=True)
          st.rerun()
    else:
      with st.chat_message(message["role"]):
        st.markdown(f'<div style="max-width: 80%;" class="messages">{message["content"]}</div>', unsafe_allow_html=True)
      #会話終了後
      if i >= 10:
        display_after_complete()


#送信ボタンが押されたとき
def send_message():
  input = st.session_state['input']
  if input == "":
    st.session_state['placeholder'] = "メッセージを入力してください！"
    return
  else:
    st.session_state['input'] = ""
    st.session_state['placeholder'] = ""
    messages = read_firebase_talk_data()
    next_message_id = str(len(messages))
    add_data(st.session_state['user_id'], {"messages": {f"day{now_day}": {"messages": {next_message_id: {"role": "Human", "content": input}}}}})


# データの追加の関数
def add_data(document_id, data):
  db.collection('users').document(document_id).set(data, merge=True)


#会話完了後の表示
def display_after_complete():
  if now_day < talk_days:
    st.markdown(
      f'本日の会話は終了です。<br><a href="https://nagoyapsychology.qualtrics.com/jfe/form/SV_23orSJSGkW2uu0e?user_id={st.session_state["user_id"]}&day={now_day}">こちら</a>をクリックして本日の日記を書いてください。',
      unsafe_allow_html=True
    )
  else:
    st.markdown(
      f'{talk_days}日間の会話パートは終了です。<br><a href="https://nagoyapsychology.qualtrics.com/jfe/form/SV_23orSJSGkW2uu0e?user_id={st.session_state["user_id"]}&day={now_day}">こちら</a>をクリックして本日の日記を書いてください。',
      unsafe_allow_html=True
    )
  st.stop()



#ログイン（実験参加者のid認証）
if not st.session_state['user_id']:
  user_id = st.text_input("クラウドワークスIDを入力してエンターを押してください")
  if user_id:
    if user_id in valid_ids:
      st.session_state['user_id'] = user_id
      new_query_params = query_params.copy()
      new_query_params['user_id'] = [user_id]
      st.experimental_set_query_params(**new_query_params)
      st.rerun()
    else:
      st.error("IDが間違っています")
  st.stop()



if st.session_state['user_id']:
  #今日の日付が開始日よりも前の場合
  if now < start_day_obj:
    st.write(f"会話パートは{start_day_obj.month}月{start_day_obj.day}日正午から開始できます。")
    st.stop()
  #5日間の後の場合
  elif now_day > talk_days:
    st.write(f"{talk_days}日間の会話パートは終了しました。")
    st.stop()
  #今の時間が正午よりも前の場合
  elif now.hour < 12:
    st.write("会話は本日の12時から開始できます。")
    st.stop()
  else:
    st.title(f"会話{now_day}日目")

  
  #会話の履歴を常に表示
  show_messages()

  st.components.v1.html(scroll_js)



  # フッターのように入力欄を下部に固定
  st.markdown('<div class="footer">', unsafe_allow_html=True)
  st.text_area(
    "input message", 
    key="input", 
    height=68,
    placeholder=st.session_state['placeholder'],
    label_visibility="collapsed",
  )
  st.button("送信", on_click=send_message)
