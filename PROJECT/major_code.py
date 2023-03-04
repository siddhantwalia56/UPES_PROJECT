import pypyodbc as odbc

# Create your views here.
from translate import Translator
from gtts import gTTS
import os
import torch
import json
from translate import Translator
from transformers import T5ForConditionalGeneration, T5Tokenizer
from fpdf import FPDF
import requests, http
import smtplib
import os
from datetime import datetime

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

db = {"siddhantwalia56@gmail.com":"Spanish"
}

language_sel = {"English" : "en", 
                "Portuguese": "pt", 
                "Spanish" : "es",
                "Swedish": "sv",
                "French":"fr"
                }




def index(file_path, participants):
    with open(file_path, "r") as file:
        file_data = file.read()
    summary = get_summary(file_data)
    for participant in participants:
        translated_text = translate_text(summary, db[participant])
        convert_text_to_speech(translated_text, file_path, db[participant])
        str_to_pdf(translated_text, file_path)

        send_mail(file_path, participant)
        print("Mail sent to", participant)
    return 'Summary Send'




def get_summary(str_input):
    model = T5ForConditionalGeneration.from_pretrained('t5-small')
    tokenizer = T5Tokenizer.from_pretrained('t5-small')
    device = torch.device('cpu')

    preprocess_text = str_input.strip().replace("\n","")
    t5_prepared_text = "summarize: "+preprocess_text

    tokenized_text = tokenizer.encode(t5_prepared_text, return_tensors="pt").to(device)

    summary = ""
    for i in range(0,len(tokenized_text),512):
        text_inp = tokenized_text[i:i+512]
        summary_ids = model.generate(text_inp,
                                        num_beams=4,
                                        no_repeat_ngram_size=3,
                                        min_length=min(30, len(text_inp)),
                                        max_length=2000,
                                        early_stopping=True)

        output = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        summary += " "+output
    #print(summary)
    return(summary)


def translate_text(text , selected_lang):
    lang = language_sel[selected_lang]
    translator= Translator(to_lang=lang)
    translation = translator.translate(text)
    return (translation)
def convert_text_to_speech(text, file_path, selected_lang):
    language = language_sel[selected_lang]
    file_name = file_path.split("/")[-1].split(".")[0]
    myobj = gTTS(text , lang = language , slow = False )
    myobj.save(file_name+'.mp3')
    #os.system(file_name+'.mp3')



def str_to_pdf(txt, file_path):
    file_name = file_path.split("/")[-1].split(".")[0]
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size = 15)
    pdf.cell(190, 12, ln=1, txt = "SUMMARY", align = 'C')
    pdf.cell(190, 12, ln=2, txt = str(datetime.now()), align = 'L')
    pdf.multi_cell(190, 8, txt, align = 'J')
    pdf.output(file_name + ".pdf")


def send_mail(file_path, receiver):
    Sender = os.environ.get("email_id")
    Sender_pass = os.environ.get("email_pass")
    Receivers = [receiver]

    msg = MIMEMultipart()
    msg["Subject"] = "Meet summary"
    body = "Summary of the meet is attached with the mail."
    msg["From"] = Sender
    msg["To"] = ",".join(Receivers)

    msg.attach(MIMEText(body, "plain"))

    file_name = file_path.split("/")[-1].split(".")[0]+".pdf"
    with open(file_name, "rb") as file:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={file_name}")
        msg.attach(part)

        file_name = file_path.split("/")[-1].split(".")[0]+".mp3"
        part = MIMEApplication(open(file_name, "rb").read())
        part.add_header("Content-Disposition", "attachment", filename = file_name)
        msg.attach(part)

        text_msg = msg.as_string()

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(Sender, Sender_pass)
        smtp.sendmail(Sender, Receivers, text_msg)
        
def main():
    fpath=input('Enter the path of the file ')
    participants=input('Enter the email id of the participants (space as a seprator) ').split()
    index(fpath, participants)

main()
