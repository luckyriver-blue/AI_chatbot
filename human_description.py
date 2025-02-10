from read_secret_data import openai_key
import openai

openai.api_key=openai_key

def generate_description(conversation_history):
#会話内容からその人物の特徴を抽出
  response = openai.chat.completions.create(
      model="gpt-4o",  
      messages=[
        {
          "role": "system",
          "content": "Based on the following data, please extract and list the personal traits, profession, social roles, and any other relevant information of the User in bullet points."
        },
        {
          "role": "user",
          "content": f"Conversation History: {conversation_history}"
        },
      ],
      max_tokens=400,  
  )
  if response.choices[0].finish_reason == 'length':
    print(f'{conversation_history}で、tokenが足りないです。')
    exit()
  description = response.choices[0].message.content.strip()  

  #説明が生成されたことを表示
  print("The description was generated through the conversation history.")
  print(description) 
  return description