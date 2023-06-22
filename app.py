import random
import time
import base64
import os
from flask import Flask, render_template, request
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

app = Flask(__name__)
gmail_service = None
email_labels = {"replied": "Vacation Auto Replied"}
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]


@app.route("/", methods=["GET", "POST"])
def vacation_auto_responder():
    if request.method == "POST":
        gmail_id = request.form.get("gmail_id")
        vacation_message = request.form.get("vacation_message")
        interval_min = int(request.form.get("interval_min"))
        interval_max = int(request.form.get("interval_max"))

        global gmail_service
        gmail_service = connect_to_gmail_api(gmail_id)

        start_auto_responder(vacation_message, interval_min, interval_max)

    return render_template("index.html")


def connect_to_gmail_api(gmail_id):
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])
        return service

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


processed_emails = set()


def start_auto_responder(vacation_message, interval_min, interval_max):
    while True:
        unread_emails = fetch_unread_emails()

        for email in unread_emails:
            email_id = email["id"]

            if email_id not in processed_emails:
                send_auto_reply(email, vacation_message)
                processed_emails.add(email_id)

                time.sleep(random.randint(interval_min, interval_max))

        interval = random.randint(interval_min, interval_max)
        time.sleep(interval)


def fetch_unread_emails():
    results = (
        gmail_service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], q="is:unread")
        .execute()
    )
    messages = results.get("messages", [])
    unread_emails = []

    for message in messages:
        email = (
            gmail_service.users()
            .messages()
            .get(userId="me", id=message["id"])
            .execute()
        )
        unread_emails.append(email)
    return unread_emails


def has_prior_reply(email):
    thread_id = email["threadId"]
    thread = gmail_service.users().threads().get(userId="me", id=thread_id).execute()
    messages = thread["messages"]
    if len(messages) > 1:
        return True
    return False


def send_auto_reply(email, vacation_message):
    thread_id = email["threadId"]

    reply_subject = "RE: NO-REPLY AUTOMATED MESSAGE"
    reply_body = (
        f"Dear {email['payload']['headers'][10]['value']},\n\n{vacation_message}"
    )

    message = MIMEMultipart()

    to_address = None
    for header in email["payload"]["headers"]:
        if header["name"].lower() == "from":
            to_address = header["value"]
            break

    if to_address:
        message["to"] = to_address

    message["subject"] = reply_subject
    message.attach(MIMEText(reply_body, "plain"))

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

    reply_payload = {"raw": raw_message}
    gmail_service.users().messages().send(userId="me", body=reply_payload).execute()

    add_label_to_email(thread_id, email_labels["replied"])


def generate_auto_reply(vacation_message, email):
    sender = email["payload"]["headers"][0]["value"]

    #    for header in email["payload"]["headers"]:
    #        print(header)

    reply_subject = "RE: "
    reply_body = f"Dear {sender},\n\n{vacation_message}"

    mime_message = (
        f"Subject: {reply_subject}\nFrom: {sender}\nTo: {sender}\n\n{reply_body}"
    )

    return base64.urlsafe_b64encode(mime_message.encode("utf-8")).decode("utf-8")


def add_label_to_email(thread_id, label_name):
    thread = gmail_service.users().threads().get(userId="me", id=thread_id).execute()
    existing_labels = thread.get("labels", [])

    label_id = None
    for label in existing_labels:
        if label["name"] == label_name:
            label_id = label["id"]
            break

    if label_id:
        gmail_service.users().threads().modify(
            userId="me", id=thread_id, body={"addLabelIds": [label_id]}
        ).execute()


def get_label_id(label_name):
    labels = gmail_service.users().labels().list(userId="me").execute()
    label_list = labels.get("labels", [])

    for label in label_list:
        if label["name"] == label_name:
            return label["id"]

    return None


if __name__ == "__main__":
    app.run(debug=False)
