import os
import csv
import base64
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient import errors
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from googleapiclient import errors
import google_auth_oauthlib.flow


# Replace with the path to your credentials file
CREDENTIALS_FILE = './credentials.json'
# Replace with the path to your CSV file
CSV_FILE = './recipient.csv'
# Replace with the path to your attachments folder
ATTACHMENT_DIR = './attachment'

# Replace with the subject line of your email
SUBJECT = 'First Test Run'

# Load credentials from file
creds = None
if os.path.exists('token.json'):
    creds = google.oauth.oauthlib.Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.send'])
else:
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    CREDENTIALS_FILE, ['https://www.googleapis.com/auth/gmail.send'])
    creds = flow.run_local_server(port=0)

    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

# Create the Gmail API client
service = build('gmail', 'v1', credentials=creds)

# Define the message to be sent
message = MIMEMultipart()

# Load the CSV file
with open(CSV_FILE) as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row
    for name, email in reader:
        # Load the attachment file for this person
        attachment_file = os.path.join(ATTACHMENT_DIR, name + '.png')
        with open(attachment_file, 'rb') as f:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(f.read())
            base64_attachment = base64.urlsafe_b64encode(attachment.as_bytes()).decode()
            attachment.add_header('Content-Disposition', 'attachment', filename=name + '.png')
            message.attach(attachment)

        # Add the name to the body of the email
        body = f"Dear {name},\n\nThis is the first test of my fully automated email system.\n\nBest regards,\nSiddhartha Bhattacharjee"

        # Set up the message headers
        message['to'] = email
        message['subject'] = SUBJECT
        message.attach(MIMEText(body, 'plain'))

        try:
            # Send the email
            create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
            send_message = (service.users().messages().send(userId="me", body=create_message).execute())
            print(F'sent message to {email} Message Id: {send_message["id"]}')
        except HttpError as error:
            print(F'An error occurred: {error}')
            send_message = None

