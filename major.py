import pypyodbc as odbc
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
from mail import send_mail

language_sel = {"English" : "en", 
                "Portuguese": "pt", 
                "Spanish" : "es",
                "Swedish": "sv",
                "French":"fr"
                }

directory = 'static/uploads'
dir_summary = 'static/summary'
dir_audio = 'static/audio'

def index(filename, participants, flang, sender_name):
    file_path = os.path.join(directory, filename)
    with open(file_path, "r") as file:
        file_data = file.read()
    summary = get_summary(file_data)
    for participant in participants:
        translated_text = translate_text(summary, flang)
        convert_text_to_speech(translated_text, filename, flang)
        str_to_pdf(translated_text, filename)

        send_mail(filename, participant, sender_name)
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
    myobj.save("static/audio/" + file_name+'.mp3')

def str_to_pdf(txt, file_path):
    file_name = file_path.split("/")[-1].split(".")[0]
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size = 15)
    pdf.cell(190, 12, ln=1, txt = "SUMMARY", align = 'C')
    pdf.cell(190, 12, ln=2, txt = str(datetime.now()), align = 'L')
    pdf.multi_cell(190, 8, txt, align = 'J')
    pdf.output("static/summary/" + file_name + ".pdf")
