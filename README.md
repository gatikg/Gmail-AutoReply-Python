# Gmail-AutoReply-Python
Vacation Auto Responder
The "Vacation Auto Responder" application is a Flask-based web application that provides an automated email response for users on vacation. The application connects to the Gmail API to fetch unread emails, send auto-replies, and label processed emails. It allows users to specify their Gmail ID, vacation message, and time intervals for processing emails and sending auto-replies.

# Prerequisites
Before running the application, you need to set up the following:

Install the required Python packages:

flask: For creating the web application.
google-api-python-client: For interacting with the Gmail API.
google-auth: For authentication and authorization with Google APIs.
google-auth-oauthlib: For OAuth 2.0 support.
google-auth-httplib2: For handling HTTP requests.
Set up credentials:

Enable the Gmail API and create credentials by following the steps provided in the Gmail API Python Quickstart.
Download the credentials.json file containing your client ID and client secret.
Save the credentials.json file in the same directory as the application code.

# Application Structure
The application consists of the following files:

app.py: The main application code containing Flask routes and functions for connecting to the Gmail API, sending auto-replies, and handling email processing.
index.html: The HTML template for the application's homepage.

# Running the Application
To run the application, follow these steps:

Make sure you have satisfied the prerequisites mentioned above.
Save the app.py and index.html files in a directory.
Open a terminal or command prompt and navigate to the directory where the files are saved.
Install the required Python packages by running the following command:
Copy code
pip install flask google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
Run the application using the following command:
Copy code
python app.py
Open a web browser and visit http://localhost:5000 to access the application.
# Application Workflow
The user accesses the application through the web browser and provides the Gmail ID, vacation message, and time intervals for email processing.
The application connects to the Gmail API using the provided credentials and establishes a connection to the user's Gmail account.
The auto-responder is started, which continuously fetches unread emails from the user's inbox.
For each unread email, the application checks if it has been processed before by maintaining a set of processed email IDs.
If the email is new, an auto-reply is sent to the sender using the provided vacation message.
The email is marked as processed and moved to the "Vacation Auto Replied" label.
The application waits for a random interval between the specified minimum and maximum values before processing the next email.
The process continues until the application is stopped.
# Code Documentation
Here's the code documentation for the important functions in the app.py file:

# connect_to_gmail_api(gmail_id)
This function establishes a connection to the Gmail API using the provided Gmail ID and returns the Gmail service object.

# gmail_id (str): The Gmail ID (email address) of the user.
# start_auto_responder(vacation_message, interval_min, interval_max)
This function starts the auto-responder, which continuously fetches unread emails and sends auto-replies.

# vacation_message (str): The vacation message to be included in the auto-reply.
# interval_min (int): The minimum time interval (in seconds) between processing emails.
# interval_max (int): The maximum time interval (in seconds) between processing emails.

# fetch_unread_emails()
This function fetches unread emails from the user's inbox.

# has_prior_reply(email)
This function checks if an email thread has a prior reply.

email (dict): The email object.
send_auto_reply(email, vacation_message)
This function sends an auto-reply to the sender of the provided email.

email (dict): The email object to which the auto-reply is sent.
vacation_message (str): The vacation message to be included in the auto-reply.
add_label_to_email(thread_id, label_name)
This function adds a label to the email thread.

thread_id (str): The ID of the email thread.
label_name (str): The name of the label to be added.

# Conclusion
The "Vacation Auto Responder" application provides a convenient way to automate email responses during vacations. By connecting to the Gmail API, the application can fetch unread emails, send auto-replies, and label processed emails. This documentation should help you understand the application's structure, prerequisites, and workflow. Feel free to customize and enhance the application based on your specific requirements.
