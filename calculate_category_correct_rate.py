import os
import pandas as pd
from datetime import datetime
from data.users.users_id import users

parent_directory = os.path.abspath(os.path.join('calculate_correct_rate.py', '..'))
ai_prediction_file = os.path.join(parent_directory, 'data', 'experiment_data', 'task_ai_prediction', 'result.csv')
human_result_directory = os.path.join(parent_directory, 'data', 'experiment_data', 'task_human_result')
human_csv_name = os.listdir(human_result_directory)[-1] #csvファイル名を取得
human_result_file = os.path.join(human_result_directory, human_csv_name)
result_file = os.path.join(parent_directory, 'data', 'analysis_data', 'correct_answer_rate.csv')

#AIの正答率を計算
def calculate_correct_rate(ai_data):
    correct_count = [0, 0] #0番目は行動？で1番目は性格？
    for i in range(20):
      if ai_data[i] == test_human_data[i]:
        if i < 9 or i == 19:
          correct_count[0] += 1
        else:
          correct_count[1] += 1
    correct_rate.extend([round(c/10*100, 2) for c in correct_count])


for user in users:
  #ai_predictionデータを読み込み
  with open(ai_prediction_file, 'r', encoding='utf-8') as ai_data:
    lines = ai_data.readlines()
    #csvデータから、該当のuserの行だけ取り出す
    for line in lines:
      if user in line:
        user_line = line
        break
    test_ai_data = list(map(int, user_line.strip().split(',')[1:61]))
    ai_data1 = test_ai_data[:20] #会話の履歴だけ条件
    ai_data2 = test_ai_data[20:40] #ビッグファイブデータだけ条件
    ai_data3 = test_ai_data[40:] #両方条件

  #human_resultデータを読み込み
  with open(human_result_file, 'r', encoding='utf-8') as human_data:
    lines = human_data.readlines()
    #csvデータから、該当のuserの行だけ取り出す
    for line in lines:
      if user in line:
        user_line = line
        break
    test_human_data = list(map(int, user_line.strip().split(',')[1:21]))

  correct_rate = []
  
  calculate_correct_rate(ai_data1)
  calculate_correct_rate(ai_data2)
  calculate_correct_rate(ai_data3)

  #結果リストをcsvファイルに出力
  timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  output_data = correct_rate + [timestamp]
  pd.DataFrame([output_data]).to_csv(result_file, index=False, header=False, mode="a")   
print(f"Results saved to {result_file}.")