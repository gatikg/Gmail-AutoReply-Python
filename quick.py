from __future__ import print_function
import os.path
import random
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

# Global variables
replied_label_name = "Vacation Auto Responder Replied"
response_subject = "Re: "  # Prefix to add to the subject line of the response email


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r"credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)

        # Check for new emails and send auto responses
        while True:
            check_and_send_auto_responses(service)
            wait_for_random_interval()

    except HttpError as error:
        # TODO(developer) - Handle errors from Gmail API.
        print(f"An error occurred: {error}")


def check_and_send_auto_responses(service):
    try:
        query = "is:unread -from:me"  # Query to fetch unread emails excluding self-sent emails
        response_subject_prefix_length = len(response_subject)

        results = service.users().messages().list(userId="me", q=query).execute()
        messages = results.get("messages", [])

        for message in messages:
            msg = (
                service.users().messages().get(userId="me", id=message["id"]).execute()
            )
            headers = msg["payload"]["headers"]
            subject = get_header_value(headers, "Subject")
            replied = has_replied(headers)

            if not replied:
                # Prepare auto response email
                reply_body = (
                    f"Thank you for your email. I am currently on vacation and will not be able to respond immediately. "
                    f"I will get back to you as soon as I return. \n\nBest Regards, \nYour Name"
                )
                reply_subject = (
                    response_subject + subject[response_subject_prefix_length:]
                )

                # Send auto response
                send_email(service, msg["threadId"], reply_subject, reply_body)

    except HttpError as error:
        print(f"Error occurred while checking and sending auto responses: {error}")


def send_email(service, thread_id, subject, body):
    try:
        message = create_message("me", "me", subject, body)
        sent_message = (
            service.users().messages().send(userId="me", body=message).execute()
        )

        # Add label to replied email and move it to the label
        label_id = get_or_create_label(service, replied_label_name)
        service.users().messages().modify(
            userId="me", id=sent_message["id"], body={"addLabelIds": [label_id]}
        ).execute()
        service.users().threads().modify(
            userId="me", id=thread_id, body={"addLabelIds": [label_id]}
        ).execute()

    except HttpError as error:
        print(f"Error occurred while sending email: {error}")


def create_message(sender, recipient, subject, message_text):
    message = {
        "raw": "",
        "message": {
            "snippet": "",
            "payload": {
                "headers": [
                    {"name": "From", "value": sender},
                    {"name": "To", "value": recipient},
                    {"name": "Subject", "value": subject},
                ],
                "body": {
                    "data": "",
                },
            },
        },
    }

    message["message"]["payload"]["headers"][-1]["value"] = subject
    message["message"]["payload"]["body"]["data"] = base64.urlsafe_b64encode(
        message_text.encode("utf-8")
    ).decode("utf-8")

    return message


def get_or_create_label(service, label_name):
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])

    for label in labels:
        if label["name"] == label_name:
            return label["id"]

    # Label doesn't exist, create a new one
    label = (
        service.users()
        .labels()
        .create(userId="me", body={"name": label_name})
        .execute()
    )
    return label["id"]


def get_header_value(headers, header_name):
    for header in headers:
        if header["name"] == header_name:
            return header["value"]
    return ""


def has_replied(headers):
    for header in headers:
        if header["name"] == "In-Reply-To":
            return True
    return False


def wait_for_random_interval():
    interval = random.randint(45, 120)
    time.sleep(interval)


if __name__ == "__main__":
    main()
