import firebase_admin
from firebase_admin import credentials, firestore
from read_secret_data import openai_key, firebase_project_settings
import openai

openai.api_key=openai_key

#Firebaseからデータを読み取り、会話内容のデータを作成
cred = credentials.Certificate(firebase_project_settings)
firebase_admin.initialize_app(cred)

db = firestore.client()



doc_ref = db.collection("users").document("user1")
doc = doc_ref.get()
if doc.exists:
  data = doc.to_dict()
else:
  print("Document not found!")

#会話内容からその人物の特徴を抽出
response = openai.chat.completions.create(
    model="gpt-4o",  
    messages=[
      {
        "role": "system",
        "content": "Based on the following data, please extract and list the personal traits, profession, social roles, and any other relevant information of the HUMAN in bullet points."
      },
      {
        "role": "user",
        "content": f"Conversation History: {data}"
      },
    ],
    max_tokens=100,  
)
    
description = response.choices[0].message.content.strip()  

#説明が生成されたことを表示
print("The description was generated through the conversation history.")
print(description) #今だけ