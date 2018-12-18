import logging
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

try:
    from django.conf import settings

    EMAIL_HOST = settings.EMAIL_HOST
    EMAIL_HOST_USER = settings.EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD = settings.EMAIL_HOST_PASSWORD
    EMAIL_PORT = settings.EMAIL_PORT
    EMAIL_USE_TLS = settings.EMAIL_USE_TLS
except ImportError:
    try:
        import os
        from dotenv import load_dotenv

        load_dotenv(verbose=True)
        EMAIL_HOST = os.getenv("EMAIL_HOST")
        EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
        EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
        EMAIL_PORT = os.getenv("EMAIL_PORT")
        EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS").lower() == "true"
    except ImportError:
        EMAIL_HOST = None
        EMAIL_HOST_USER = None
        EMAIL_HOST_PASSWORD = None
        EMAIL_PORT = None
        EMAIL_USE_TLS = None

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


subject = "An email with attachment from Python"
body = "This is an email with attachment sent from Python"
sender_email = "jason@jjk.io"
receiver_email = "jkuosion@gmail.com"

# Create a multipart message and set headers
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject
message["Bcc"] = receiver_email  # Recommended for mass emails

# Add body to email
message.attach(MIMEText(body, "plain"))

filename = "requirements.txt"  # In same directory as script

# Open PDF file in binary mode
with open(filename, "rb") as attachment:
    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())

# Encode file in ASCII characters to send by email
encoders.encode_base64(part)

# Add header as key/value pair to attachment part
part.add_header(
    "Content-Disposition",
    f"attachment; filename= {filename}",
)

# Add attachment to message and convert message to string
message.attach(part)
text = message.as_string()

# Log in to server using secure context and send email
context = None
if EMAIL_USE_TLS:
    logging.debug("Using TLS")
    context = ssl.create_default_context()

with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
    if EMAIL_USE_TLS:
        server.starttls(context=context)
    server.ehlo()
    server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    server.sendmail(sender_email, receiver_email, text)
