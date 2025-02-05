import streamlit as st
from read_secret_data import openai_key, firebase_project_settings
import firebase_admin
from firebase_admin import credentials, firestore
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from style_and_javascript.style import hide_st_style, message_style, input_style
from style_and_javascript.javascript import scroll_js
import datetime, pytz, time, random

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
if 'talk_day_data' not in st.session_state:
  st.session_state['talk_day_data'] = None
if 'messages' not in st.session_state:
  st.session_state["messages"] = [{"role": "AI", "content": "今日は何がありましたか？"}]
if "input" not in st.session_state:
    st.session_state['input'] = ""
if 'count' not in st.session_state:
  st.session_state.count = 0
if 'placeholder' not in st.session_state:
  st.session_state['placeholder'] = ""


memory = ConversationBufferMemory()


#会話パート何日間行うか
talk_days = 1
#5日間の会話パート
now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
#会話パート開始日
start_day = now #アクセスしている日
# タイムゾーンを付与
#start_day = pytz.timezone('Asia/Tokyo').localize(start_day)
#今日が会話パート何日目か計算
now_day = (now - start_day).days + 1


#Firebaseから有効な参加者IDを取得する関数
def get_valid_ids():
  valid_ids = []
  users = db.collection('users').stream()

  for user in users:
    valid_ids.append(user.id)
  
  return valid_ids

valid_ids = ['あ'] #有効なユーザーID 今は'あ'のみ
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
def read_firebase_data():
  doc_ref = db.collection("users").document(st.session_state['user_id'])
  doc = doc_ref.get()

  data = doc.to_dict()
  if data is None:
    prompt_bigfive = {}
    talk_day_data = {}
  else:
    prompt_bigfive = data.get('bigfive', {})
    talk_day_data = data.get('messages', {}).get(f'day{now_day}', {}).get('messages', {})

  return prompt_bigfive, talk_day_data


if st.session_state['prompt_bigfive'] == {}:
  prompt_bigfive, talk_day_data = read_firebase_data()
  st.session_state['prompt_bigfive'] = prompt_bigfive
  st.session_state['talk_day_data'] = talk_day_data
else:
  prompt_bigfive = st.session_state['prompt_bigfive']
  talk_day_data = st.session_state['talk_day_data']


# prompt_bigfiveの各値を変数として渡す
extraversion = prompt_bigfive.get("extraversion", "N/A")
agreeableness = prompt_bigfive.get("agreeableness", "N/A")
conscientiousness = prompt_bigfive.get("conscientiousness", "N/A")
neuroticism = prompt_bigfive.get("neuroticism", "N/A")
openness = prompt_bigfive.get("openness", "N/A")

# プロンプトテンプレートの設定
prompt_template = PromptTemplate(
  input_variables=["history", "input"],
  template=f"""
    ユーザーの性格：
    Extraversion: {extraversion}, 
    Agreeableness: {agreeableness}, 
    Conscientiousness: {conscientiousness}, 
    Neuroticism: {neuroticism}, 
    Openness: {openness}

    ユーザーの性格を参照して、ユーザーにとって最適な会話を心がけてください。
    ユーザーの性格のスコアに直接的に言及しないでください。
    ユーザーのことをユーザーと呼ばないでください。
    300文字以内で回答してください。
    以下は会話の履歴です：\n{{history}}\n\nユーザーの入力：{{input}}
  """
)

gpt = ChatOpenAI(
    model_name="gpt-4o",
    max_tokens=1024,
    temperature=0.5,
    frequency_penalty=0.02,
    openai_api_key=openai_key
)

conversation = ConversationChain(
  llm=gpt, 
  verbose=False, 
  prompt=prompt_template,
  memory=memory
)

#上記のプロンプトを用いて、ユーザーの入力に対する応答を取得する関数
def get_response(user_input):
  return conversation.predict(input=user_input)




# 会話メッセージの履歴を表示
def show_messages():
  if talk_day_data != {}:
    st.session_state["messages"] = talk_day_data

  for i, message in enumerate(st.session_state["messages"]):
    if message["role"] == "Human":
      st.markdown(f'''
      <div style="display: flex;">
        <div style="display: flex; margin-left: auto; max-width: 60%;">
          <div class="messages">{message["content"]}</div>
        </div>
      </div>
      ''', unsafe_allow_html=True)
      if i != 9 and i == len(st.session_state["messages"]) - 2:
        with st.spinner("応答を生成しています"):
          #応答の生成時間(ダミー)
          sleep_time = random.choice([1, 1.5, 2])
          time.sleep(sleep_time)
    else:
      if i != 10 and i == len(st.session_state["messages"]) - 1:
        with st.spinner("応答を生成しています"):
          with st.chat_message(message["role"]):
            st.markdown(f'<div style="max-width: 70%;" class="messages">{message["content"]}</div>', unsafe_allow_html=True)
      else:
          with st.chat_message(message["role"]):
            st.markdown(f'<div style="max-width: 70%;" class="messages">{message["content"]}</div>', unsafe_allow_html=True)
      


#送信ボタンが押されたとき
def send_message():
  input = st.session_state['input']
  if input == "":
    st.session_state['placeholder'] = "メッセージを入力してください！"
    return
  else:
    st.session_state['input'] = ""
    st.session_state['placeholder'] = ""
    st.session_state["messages"].append({"role": "Human", "content": input})
    st.session_state["messages"].append({"role": "AI", "content": get_response(input)})
    st.session_state.count += 1
    #会話が5ターンずつ終わった時ではなく、会話が終わらないようにする
    if st.session_state.count == -1:
      add_data('users', st.session_state['user_id'], {"messages": {f"day{now_day}": {"messages": st.session_state["messages"]}}})


# データの追加の関数
def add_data(collection_name, document_id, data):
  db.collection(collection_name).document(document_id).set(data, merge=True)


#会話完了後の表示
def display_after_complete():
  if now_day < talk_days:
    st.markdown('本日の会話は終了です。')
  else:
    st.markdown(
      f'{talk_days}日間の会話パートは終了です。<br><a href="https://nagoyapsychology.qualtrics.com/jfe/form/SV_5b4FQikEOMWsjAO?user_id={st.session_state["user_id"]}">こちら</a>をクリックしてアンケートに回答してください。', unsafe_allow_html=True
    )
  st.stop()



#ログイン（実験参加者のid認証）
if not st.session_state['user_id']:
  user_id = st.text_input("IDを半角で入力してエンターを押してください")
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


#ログイン後にデータを都度確認してなければ読み込む
if st.session_state['prompt_bigfive'] == {}:
  prompt_bigfive, talk_day_data = read_firebase_data()
  st.session_state['prompt_bigfive'] = prompt_bigfive
  st.session_state['talk_day_data'] = talk_day_data
else:
  prompt_bigfive = st.session_state['prompt_bigfive']
  talk_day_data = st.session_state['talk_day_data']



if st.session_state['user_id']:
  #今日の日付が開始日よりも前の場合
  if now < start_day:
    #ビッグファイブのアンケートに回答してない場合は認証させてアンケートリンクを表示する
    if prompt_bigfive == {}:
      st.markdown(f'<a href="https://nagoyapsychology.qualtrics.com/jfe/form/SV_4N1LfAYkc9TrY8u?user_id={st.session_state["user_id"]}" target="_blank">こちら</a>をクリックしてアンケートに回答してください。', unsafe_allow_html=True)
    else:
      st.write(f"会話パートは{start_day.month}月{start_day.day}日15時から開始できます。")
    st.stop()
  #5日間の後の場合
  elif now_day > talk_days:
    st.write(f"{talk_days}日間の会話パートは終了しました。")
    st.stop()
  #今の時間が午後3時よりも前の場合 今はなし
  elif now.hour < 0:
    st.write("会話は本日の15時から開始できます。")
    st.stop()
  else:
    st.title(f"会話{now_day}日目")


  #会話の履歴を常に表示
  show_messages()

  #会話終了後
  if talk_day_data != {} or st.session_state.count >= 5:
    display_after_complete()

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
