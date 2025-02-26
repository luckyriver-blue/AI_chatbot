import os
import pandas as pd

parent_directory = os.path.abspath(os.path.join('read_bigfive.py', '..'))
bigfive_directory = os.path.join(parent_directory, 'data', 'experiment_data', 'bigfive_data')
bigfive_csv_name = os.listdir(bigfive_directory)[-1] #csvファイル名を取得
bigfive_csv = os.path.join(bigfive_directory, bigfive_csv_name)
human_result_directory = os.path.join(parent_directory, 'data', 'experiment_data', 'task_human_result')
human_csv_name = os.listdir(human_result_directory)[-1] #csvファイル名を取得
human_result_file = os.path.join(human_result_directory, human_csv_name)


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

  data = []
  #high=3,medium=2,low=1
  for i in range(5):
    if bigfive_list[i] > medium_range[i][1]:
      data.append(3)
    elif bigfive_list[i] >= medium_range[i][0]:
      data.append(2)
    else:
      data.append(1)


  #残業の回答も従属変数としてデータにいれる
  #human_resultデータを読み込み
  with open(human_result_file, 'r', encoding='utf-8') as human_data:
    lines = human_data.readlines()
    #csvデータから、該当のuserの行だけ取り出す
    for line in lines:
      if user_id in line:
        user_line = line
        break
    task_data = user_line.strip().split(',')[9]
  data.append(int(task_data))

  pd.DataFrame([data]).to_csv('data/machine_learning/zangyo.csv', index=False, header=False, mode="a")   
  