import os
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from read_secret_data import firebase_project_settings


parent_directory = os.path.abspath(os.path.join('read_bigfive.py', '..'))
bigfive_directory = os.path.join(parent_directory, 'data', 'experiment_data', 'bigfive_data')
bigfive_csv_name = os.listdir(bigfive_directory)[-1] #csvファイル名を取得
bigfive_csv = os.path.join(bigfive_directory, bigfive_csv_name)

#ビッグファイブのcsvファイルを読み取りLOW・MEDIUM・HIGHでリスト化
qualtrics_data = pd.read_csv(bigfive_csv)

#すべてのユーザーのデータを処理するためループで回す
for index, data in qualtrics_data.iterrows():
  #最初のヘッダー2行はスキップ
  if index <= 1:
    continue
  user_id = data['user_id']
  #最後の10項目の数字の羅列(ビッグファイブの結果）だけ取得
  answer = data.iloc[-10:].apply(pd.to_numeric, errors='coerce')
  answer_list = answer.tolist()

  #ビッグファイブのMEDIUMの範囲を平均 ± 標準偏差として定義する。
  #外向性は7.83±2.97、協調性は9.48±2.16、勤勉性は6.14±2.41、神経症傾向は9.21±2.48、開放性は8.03±2.48
  medium_range = [[4.86, 10.8], [7.32, 11.64], [3.73, 8.55], [6.73, 11.69], [5.55, 10.51]]

  #ビッグファイブをHIGH,MEDIUM,LOWに評価
  bigfive_list = []
  #計算方法は、参考になった論文のマニュアルから
  for i in range(5):
    #外向性、協調性、勤勉性、神経症傾向、開放性の順に入れる
    bigfive_list.append(answer_list[i]+answer_list[i+5]) 

  prompt_bigfive = []
  for i in range(5):
    if bigfive_list[i] > medium_range[i][1]:
      prompt_bigfive.append('HIGH')
    elif bigfive_list[i] >= medium_range[i][0]:
      prompt_bigfive.append('MEDIUM')
    else:
      prompt_bigfive.append('LOW')

  #Firebaseにビッグファイブデータを保存
  if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_project_settings)
    firebase_admin.initialize_app(cred)

  db = firestore.client()

  data = {
    "bigfive": {
        "extraversion": prompt_bigfive[0],
        "agreeableness": prompt_bigfive[1],
        "conscientiousness": prompt_bigfive[2],
        "neuroticism": prompt_bigfive[3],
        "openness": prompt_bigfive[4]
    }
  }

  db.collection('users').document(user_id).set(data, merge=True)
