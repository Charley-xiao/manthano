import toml
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

config = None
with open('config.toml') as f:
    config = toml.load(f)

def send_email(receiver, subject, body):
    sender = config['email']['sender']
    password = config['email']['password']
    host = config['email']['host']
    port = config['email']['port']

    message = MIMEMultipart('alternative')
    message['From'] = sender
    message['To'] = receiver
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL(host, port) as server:
        server.login(sender, password)
        print(f'Sending email to {receiver}...')
        server.sendmail(sender, receiver, message.as_string())