import os
import pickle
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import base64

# カレンダーAPIとGmail APIのスコープ
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/gmail.send']

# 認証情報を読み込む
def load_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# Google Calendar API で予定を取得
def get_calendar_events():
    creds = load_credentials()
    service = build('calendar', 'v3', credentials=creds)
    
    # 現在の時刻と1週間後の時刻を設定
    now = datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(
        calendarId='primary', timeMin=now,
        maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    
    events = events_result.get('items', [])
    
    if not events:
        return "No upcoming events found."
    
    # 直近の10件の予定を取得
    event_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        event_list.append(f"Event: {event['summary']}\nStart: {start}\n")
    
    return "\n\n".join(event_list)

# Gmail API でメールを送信
def send_email(subject, body, to):
    creds = load_credentials()
    service = build('gmail', 'v1', credentials=creds)
    
    message = MIMEText(body)
    message['to'] = to
    message['from'] = "sasaki09lime01@gmail.com"  # 自分のGmailアドレスに変更
    message['subject'] = subject
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    try:
        message = service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
        print(f'Message sent successfully to {to}')
    except Exception as error:
        print(f'An error occurred: {error}')

# メインの実行部分
if __name__ == '__main__':
    # Googleカレンダーから予定を取得
    event_details = get_calendar_events()
    
    # 取得した予定をメールで送信
    recipient_email = "sasaki09lime01@gmail.com"  # 宛先メールアドレスを指定
    email_subject = "Your Upcoming Calendar Events"
    send_email(email_subject, event_details, recipient_email)

