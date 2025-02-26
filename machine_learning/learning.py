import os
import pandas as pd
from tabulate import tabulate
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.svm import LinearSVC

parent_directory = os.path.abspath(os.path.join('learning.py', '..'))
csv_file = os.path.join(parent_directory, 'data', 'machine_learning','zangyo.csv')
result_file = os.path.join(parent_directory, 'data', 'machine_learning', 'result.txt')

columns_name = ["extraversion", "agreeableness", "conscientiousness", "neuroticism", "openness", "zangyo"]
df = pd.read_csv(csv_file, names=columns_name, header=None)

#説明変数
X = df.drop(['zangyo'], axis=1)
#目的変数
Y = df['zangyo']

#標準化（今回はデータが同じ特徴だからいらんかも）
""" scaler = StandardScaler()
X = scaler.fit_transform(X)
 """
#普通の機械学習
""" model = LinearRegression()
model.fit(X, Y)
 """
#分類の機械学習
#SVC
""" model = LinearSVC()
model.fit(X,Y)
 """

#ロジスティック回帰
model = LogisticRegression()
model.fit(X,Y)

result = [model.coef_, model.score(X, Y)]  
# 結果書き込み
print(result)
with open(result_file, 'a') as file:
    file.write("\n" + str(result) + "\n")


