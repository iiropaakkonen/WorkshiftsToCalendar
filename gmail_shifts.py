import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from bs4 import BeautifulSoup
from auth import get_credentials



def strip_html(html):
   return BeautifulSoup(html, "html.parser").get_text(separator=' ').strip()

def get_shifts():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = get_credentials()
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  #if os.path.exists("token.json"):
    #creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])

    if not labels:
      print("No labels found.")
      return

    #Finds any Gmail-messages that have the name Työvuorolista and does NOT have an attachment   
    results = service.users().messages().list(
      userId="me",
      q=f'subject:"Työvuorolista" -has:attachment'
    ).execute()
    
    #All message ids get thrown into a list
    message_ids = results.get('messages', [])

    #All messages are thrown into a new list as "full" messages
    full_messages = []
    for msg in message_ids:
        message = service.users().messages().get(
          userId="me",
          id=msg["id"],
          format="full"
        ).execute()
        full_messages.append(message)


    parsed_msg = []
    for fullmsg in full_messages:
        payload = fullmsg["payload"]
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    parsed_msg.append(base64.urlsafe_b64decode(part['body']['data']).decode('utf-8'))
                    break
                elif part['mimeType'] == 'text/html':
                    raw_html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    soup = BeautifulSoup(raw_html, "html.parser")
                    table = soup.find("table")
                    if table:
                       parsed_msg.append(table)
                    break
        else:
            raw = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            soup = BeautifulSoup(raw, "html.parser")
            table = soup.find("table")
            if table:
                parsed_msg.append(table)

    days = ("Ma ", "Ti ", "Ke ", "To ", "Pe ", "La ", "Su ")
    shifts = []
    for table in parsed_msg:
      rows = table.find_all("tr")
      for row in rows:
        cells = row.find_all(["td", "th"])
        cell_texts = [cell.get_text(strip=True) for cell in cells]
        if (len(cell_texts) >= 2 
                and cell_texts[1].strip() 
                and cell_texts[0].startswith(days)):
            shifts.append(cell_texts)

    shift_data_needed = []
    for shift in shifts:
      if "Työ" in shift[-1]:
        shift_data_needed.append([shift[0], shift[2], shift[-1]])

    return shift_data_needed


    #print("Labels:")
    #for label in labels:
    #  print(label["name"])


  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


#if __name__ == "__main__":
  #main()