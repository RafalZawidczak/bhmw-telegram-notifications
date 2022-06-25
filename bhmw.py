import requests
from bs4 import BeautifulSoup
import re
import tabula
import telegram
import pickle
import os
import dropbox


def get_links():
  url = "https://bhmw.gov.pl/pl/warnings/current/"
 
  read = requests.get(url)
  html_content = read.content
  soup = BeautifulSoup(html_content, "html.parser")

  #get all <a href> links with filetype .pdf
  links = soup.find_all('a', href=re.compile(r'(.pdf)'))

  return links

def get_pdf(links):
  pdf_list=[]
  for el in links:
    pdf = re.sub('<a href="', "https://bhmw.gov.pl", str(el))
    pdf = re.sub('.pdf".*', ".pdf", pdf)
    pdf_list.append(pdf)
  return pdf_list

def get_new_alerts(pdf_list):
  with open("current_alerts.pkl", "wb") as f:
    metadata, res = dbx.files_download(path="/current_alerts.pkl")
    f.write(res.content)
  open_file = open('current_alerts.pkl', "rb")
  loaded_list = pickle.load(open_file)
  f.close()

  new_alerts=list(set(pdf_list) - set(loaded_list))

  open_file = open('current_alerts.pkl', "wb")
  pickle.dump(pdf_list, open_file)
  open_file.close()

  with open("current_alerts.pkl", "rb") as f:
    dbx.files_upload(f.read(), "/current_alerts.pkl", mode=dropbox.files.WriteMode.overwrite, mute=True)

  return new_alerts

def send_messages(pdf_list, telegram_token):
  
  bot = telegram.Bot(telegram_token)
  for i in range (len(pdf_list)):
    um_szczecin= re.compile ('Ostrzezenia-nawigacyjne')
    if um_szczecin.search(pdf_list[i]): #Jezeli plik z UM SZecin
      tekst='Current navigation warnings issued by Szczecin City Hall have been updated. More details in PDF file. '
      tekst+=str(pdf_list[i])
      bot.send_message(chat_id="-606939991", text=tekst, parse_mode='HTML')
    else:
      table = tabula.read_pdf(pdf_list[i],pages='all', pandas_options={'header': None})
      tabela=table[-1].fillna('')
      tabela=tabela[~tabela[0].str.contains('Category')]

      tekst=str(pdf_list[i]) + '\n ---------- \n'
      try:
        for i in range (len(tabela)):
          tabela[1].iloc[i]= re.sub('\r', '\n', tabela[1].iloc[i])
          if tabela[0].iloc[i] != ''  and i<(len(tabela))-1:
            if tabela[0].iloc[i+1] != '':
              tekst+=str(tabela[0].iloc[i]) + ': '+ str(tabela[1].iloc[i]) +'\n ---------- \n'
            else:
              tekst+=str(tabela[0].iloc[i]) + ': '+ str(tabela[1].iloc[i]) +'\n'
          else:
            tekst +=str(tabela[1].iloc[i]) +'\n \n '
        bot.send_message(chat_id="-606939991", text=tekst, parse_mode='HTML')
      except: bot.send_message(chat_id="-606939991", 
      text="An error occurred while downloading the message content, please check the pdf file. " + tekst, parse_mode='HTML')

telegram_token = os.environ['TELEGRAM_TOKEN']
print(telegram_token)
dropbox_token = os.environ['DROPBOX_TOKEN']
print(dropbox_token)
dbx = dropbox.Dropbox(dropbox_token)

links = get_links()
pdf_list=get_pdf(links)
new_alerts=get_new_alerts(pdf_list)
send_messages(new_alerts, telegram_token)
