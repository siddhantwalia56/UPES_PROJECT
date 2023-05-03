import datetime
import os
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email import encoders

dir_summary = 'static/summary/'
dir_audio = 'static/audio/'


def send_mail(filename, participants, sender_name):

    # Set up email details
    sender_email = 'msg.meeting.summary@gmail.com'
    sender_password = 'ocydjfyhwcsreovv'
    recipient_emails = participants
    subject = 'Meeting Summary'

    # Create message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = COMMASPACE.join(recipient_emails)
    msg['Subject'] = subject

    file_name = filename.split("/")[-1].split(".")[0]
    # Add PDF attachment
    pdf_file_path = dir_summary + file_name + ".pdf"
    with open(pdf_file_path, 'rb') as pdf_file:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(pdf_file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        f'attachment; filename="{pdf_file_path.split("/")[-1]}"')
        msg.attach(part)

    # Add audio attachment
    audio_file_path = dir_audio + file_name + ".mp3"
    with open(audio_file_path, 'rb') as audio_file:
        part = MIMEBase('audio', 'mp3')
        part.set_payload(audio_file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        f'attachment; filename="{audio_file_path.split("/")[-1]}"')
        msg.attach(part)

    # Add email body
    body = "Dear Sir,\n\nI am writing to provide you with a summary of our meeting that was held on "+ datetime.date.today().strftime('%B %d, %Y') + "\n\nPlease find attached the minutes of the meeting for your reference.\n\nThank you for attending the meeting and I look forward to our next meeting.\n\nBest regards,\n\n" + sender_name

    msg.attach(MIMEText(body, 'plain'))

    # Send email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.sendmail(sender_email, recipient_emails, msg.as_string())
