import os
import openai
import firebase_admin
from firebase_admin import credentials, firestore
from read_secret_data import openai_key, firebase_project_settings
from data.users.users_id import users
#from human_description import description
import pandas as pd
from datetime import datetime

parent_directory = os.path.abspath(os.path.join('persona_output.py', '..'))
task_file = os.path.join(parent_directory, 'data', 'test_data', 'task.txt')
result_file = os.path.join(parent_directory, 'data', 'experiment_data', 'task_ai_prediction', 'result.csv')

#Firebaseからデータを読み込む
if not firebase_admin._apps:
  cred = credentials.Certificate(firebase_project_settings)
  firebase_admin.initialize_app(cred)
db = firestore.client()

openai.api_key=openai_key

#タスク判断課題の文章を一文ずつリスト化
with open(task_file, 'r', encoding='utf-8') as task_data:
  lines = [s.rstrip() for s in task_data.readlines()]


#usersの中から順番に処理
for user in users:
  #userのデータを取得
  doc_ref = db.collection("users").document(user)
  doc = doc_ref.get()
  if doc.exists:
    data = doc.to_dict()
  else:
    print("Document not found!")

  #会話履歴を取得
  temporary_conversation_data = data.get('messages')
  #会話履歴を順番にする
  conversation_data = dict(sorted(temporary_conversation_data.items(), key=lambda item: item[0]))
  for day_key in conversation_data:
    day_data = dict(sorted(conversation_data[day_key].get('messages').items(), key=lambda item: int(item[0])))
    conversation_data[day_key]['messages'] = day_data
  
  #ビッグファイブデータを取得
  bigfive = data.get('bigfive')
  # bigfiveの各値を変数として渡す
  extraversion = bigfive.get("extraversion")
  agreeableness = bigfive.get("agreeableness")
  conscientiousness = bigfive.get("conscientiousness")
  neuroticism = bigfive.get("neuroticism")
  openness = bigfive.get("openness")

  #判断タスクファイルから一行ずつ取り出して全て判断させる
  result = []

  #会話の履歴だけで予測
  for line in lines:     
    # プロンプトを基に出力させるようにする
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
          {
            "role": "system",
            "content": "For the following task, respond in a way that aligns with 'User' in this conversation history:\n"
                      f"{conversation_data}\n\n"
                      "Consider how this person would think and decide in this context, and generate a response accordingly."
          },
          {
            "role": "user",
            "content": "Please rate the following statement by selecting a number between 1 and 2.\n"
                      f"Statement: {line}\n"
                      "Please ensure that your response is a number between 1 and 2."
          },
        ],
        max_tokens=1,
    )

    #結果をリストに保存
    result.append(response.choices[0].message.content)


  #ビッグファイブデータだけで予測
  for line in lines:     
    # プロンプトを基に出力させるようにする
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
          {
            "role": "system",
            "content": "For the following task, respond in a way that matches this BIG FIVE personality questionnaire:\n"
                      f"Extraversion: {extraversion}, Agreeableness: {agreeableness}, Conscientiousness: {conscientiousness}, Neuroticism: {neuroticism}, Openness: {openness}\n\n"
                      "Consider how this person would think and decide in this context, and generate a response accordingly."
          },
          {
            "role": "user",
            "content": "Please rate the following statement by selecting a number between 1 and 2.\n"
                      f"Statement: {line}\n"
                      "Please ensure that your response is a number between 1 and 2."
          },
        ],
        max_tokens=1,
    )

    #結果をリストに保存
    result.append(response.choices[0].message.content)


  #会話の履歴とビッグファイブデータ両方で予測
  for line in lines:     
    # プロンプトを基に出力させるようにする
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
          {
            "role": "system",
            "content": "For the following task, respond in a way that matches this BIG FIVE personality questionnaire:\n"
                      f"Extraversion: {extraversion}, Agreeableness: {agreeableness}, Conscientiousness: {conscientiousness}, Neuroticism: {neuroticism}, Openness: {openness}\n\n"
                      "Additionally, respond in a way that aligns with 'User' in this conversation history:\n"
                      f"{conversation_data}\n\n"
                      "Consider how this person would think and decide in this context, and generate a response accordingly."
          },
          {
            "role": "user",
            "content": "Please rate the following statement by selecting a number between 1 and 2.\n"
                      f"Statement: {line}\n"
                      "Please ensure that your response is a number between 1 and 2."
          },
        ],
        max_tokens=1,
    )

    #結果をリストに保存
    result.append(response.choices[0].message.content)

  #結果リストをcsvファイルに出力
  timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  output_data = result + [timestamp]
  pd.DataFrame([output_data]).to_csv(result_file, index=False, header=False, mode="a")   
  print(f"Results saved to {result_file}.") 
  exit()