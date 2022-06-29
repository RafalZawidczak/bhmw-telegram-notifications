import requests
from bs4 import BeautifulSoup
import re
import tabula
import telegram
import pickle
import os
import dropbox

def dropbox_connect(dropbox_app_key, dropbox_app_secret, dropbox_refresh_token):
    """Create a connection to Dropbox."""

    try:
        dbx = dropbox.Dropbox(
          app_key = dropbox_app_key, 
          app_secret = dropbox_app_secret, 
          oauth2_refresh_token = dropbox_refresh_token
        )
    except AuthError as e:
        print('Error connecting to Dropbox with access token: ' + str(e))
        
    return dbx
  
def get_links():
  """Get all links scraped from bhmw website
    Returns:
      links: list of all '<a href' scraped from bhmw website
  """
  url = "https://bhmw.gov.pl/pl/warnings/current/"
 
  read = requests.get(url)
  html_content = read.content
  soup = BeautifulSoup(html_content, "html.parser")

  #get all <a href> links with filetype .pdf
  links = soup.find_all('a', href=re.compile(r'(.pdf)'))

  return links

def get_pdf(links):
  """Get all pdf files from list of links
    Args:
      links: list of all '<a href' scraped from bhmw website
    Returns:
      pdf_list: list of all pdf files scraped from bhmw website
  """
  pdf_list=[]
  for el in links:
    pdf = re.sub('<a href="', "https://bhmw.gov.pl", str(el))
    pdf = re.sub('.pdf".*', ".pdf", pdf)
    pdf_list.append(pdf)
    
  return pdf_list

def get_new_alerts(pdf_list):
  """Download all alerts from last run and compare with current list of alerts
    Args: 
      pdf_list: list of all pdf files scraped from bhmw website
    Returns:
      new_alerts: list of new pdf files compared to last run
  """

  try:
    with open("current_alerts.pkl", "wb") as f:
      metadata, res = dbx.files_download(path="/current_alerts.pkl")
      f.write(res.content)
    open_file = open('current_alerts.pkl', "rb")
    loaded_list = pickle.load(open_file)
    f.close()
  except Exception as e:
    print("Error during downloading file from dropbox" + str(e))

  #compare current list with old list to get new alerts
  new_alerts=list(set(pdf_list) - set(loaded_list))

  try:
    open_file = open('current_alerts.pkl', "wb")
    pickle.dump(pdf_list, open_file)
    open_file.close()

    with open("current_alerts.pkl", "rb") as f:
      dbx.files_upload(f.read(), "/current_alerts.pkl", mode=dropbox.files.WriteMode.overwrite, mute=True)
  except Exception as e:
    print("Error during uploading file to dropbox" + str(e))
  return new_alerts

def send_messages(new_alerts, chat_id, telegram_token):
  """Send messages to telegram channel.
    Args:
        new_alerts: list of new pdf files compared to last run
        chat_id: id of telegram channel
    """
  bot = telegram.Bot(telegram_token)
  for i in range (len(new_alerts)):
    um_szczecin= re.compile ('Ostrzezenia-nawigacyjne')
    if um_szczecin.search(new_alerts[i]): #Check if file contains 'Ostrzezenia-nawigacyjne' in its name
      tekst='Current navigation warnings issued by Szczecin City Hall have been updated. More details in PDF file. '
      tekst+=str(new_alerts[i])
      bot.send_message(chat_id=chat_id, text=tekst, parse_mode='HTML')
    else:
      table = tabula.read_pdf(new_alerts[i],pages='all', pandas_options={'header': None}) #read table from pdf
      tabela=table[-1].fillna('')
      tabela=tabela[~tabela[0].str.contains('Category')]

      tekst=str(new_alerts[i]) + '\n ---------- \n'
      try:
        for i in range (len(tabela)):
          tabela[1].iloc[i]= re.sub('\r', '\n', tabela[1].iloc[i]) #Change \r from pdf to \n to better display result
          if tabela[0].iloc[i] != ''  and i<(len(tabela))-1:
            if tabela[0].iloc[i+1] != '':
              tekst+=str(tabela[0].iloc[i]) + ': '+ str(tabela[1].iloc[i]) +'\n ---------- \n'
            else:
              tekst+=str(tabela[0].iloc[i]) + ': '+ str(tabela[1].iloc[i]) +'\n'
          else:
            tekst +=str(tabela[1].iloc[i]) +'\n \n '
        bot.send_message(chat_id=chat_id, text=tekst, parse_mode='HTML')
      except: 
        bot.send_message(chat_id=chat_id, 
        text="An error occurred while downloading the message content, please check the pdf file. " + tekst, parse_mode='HTML')


telegram_token = os.environ['TELEGRAM_TOKEN']
dropbox_app_key = os.environ['DROPBOX_APP_KEY']
dropbox_app_secret = os.environ['DROPBOX_APP_SECRET']
dropbox_refresh_token = os.environ['DROPBOX_REFRESH_TOKEN']
chat_id="@bhmw_warnings"

links = get_links()
pdf_list=get_pdf(links)
dbx = dropbox_connect(dropbox_app_key, dropbox_app_secret, dropbox_refresh_token)
new_alerts = get_new_alerts(pdf_list)
send_messages(new_alerts, chat_id, telegram_token)
