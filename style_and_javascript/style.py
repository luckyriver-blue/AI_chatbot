#streamlitのデフォルトのヘッダーなどを非表示
hide_st_style = '''
<style>
  div[data-testid="stToolbar"] {
  visibility: hidden;
  height: 0%;
  position: fixed;
  }
  div[data-testid="stDecoration"] {
  visibility: hidden;
  height: 0%;
  position: fixed;
  }
  #MainMenu {
  visibility: hidden;
  height: 0%;
  }
  header {
  visibility: hidden;
  height: 0%;
  }
  footer {
  visibility: hidden;
  height: 0%;
  }
  .appview-container .main .block-container{
      padding-top: 1rem;
      padding-right: 3rem;
      padding-left: 3rem;
      padding-bottom: 1rem;
  }  
  .reportview-container {
      padding-top: 0rem;
      padding-right: 3rem;
      padding-left: 3rem;
      padding-bottom: 0rem;
  }
  header[data-testid="stHeader"] {
      z-index: -1;
  }
</style>
'''

#会話のスタイリング
message_style = '''
<style>
  .messages {
    display: inline-block;
    word-wrap: break-word;
    background-color: #f0f0f0;
    padding: 10px;
    border-radius: 10px;
  }
</style>
'''
  
#送信欄のスタイリング
input_style = '''
<style>
  .footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    background-color: #ffffff;
    padding: 5rem;
  }
  .stTextArea {
    position: fixed;
    bottom: 6rem;
  }
  .stButton {
    position: fixed;
    bottom: 3rem;
    left: calc(98px + 58.5%);
  }
</style>
'''