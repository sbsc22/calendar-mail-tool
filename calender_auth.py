import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# スコープの設定（Gmail送信に必要）
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    creds = None
    if os.path.exists('token_gmail.json'):
        creds = Credentials.from_authorized_user_file('token_gmail.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '/Users/daichi/Desktop/calender_tool/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token_gmail.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def create_message(sender, to, subject, body):
    message = MIMEText(body, 'plain', 'utf-8')
    message['To'] = to  # 'To' ヘッダーを文字列で
    message['From'] = sender  # 'From' ヘッダーを文字列で
    message['Subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_email(service, user_id, message):
    try:
        sent_message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f'メールが送信されました！ Message ID: {sent_message["id"]}')
    except Exception as error:
        print(f'メール送信エラー: {error}')

if __name__ == '__main__':
    service = authenticate_gmail()
    message = create_message(
        sender='sasaki09lime01@gmail.com',  # 送信者のメールアドレス
        to='sasaki09lime01@gmail.com',      # 宛先のメールアドレス（自分宛でもOK）
        subject='テストメール',
        body='これはGmail APIから送信されたテストメールです。'
    )
    send_email(service, 'me', message)
