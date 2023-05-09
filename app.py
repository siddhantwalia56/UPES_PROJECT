import json
import os
from flask import Flask, render_template, request
from datetime import datetime
from major import index
from create_meeting import createMeating

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        sender_name = request.form['name']
        language = request.form['language']
        email = request.form['email'].split()
        f = request.files['file']

        filename = str(int(datetime.timestamp(datetime.now()))
                       ) + '_' + f.filename
        name = filename.split("/")[-1].split(".")[0]

        f.save('static/uploads/'+filename)

        index(filename, email, language, sender_name)
        return render_template('success.html', name=sender_name, language=language, email=email, file=name)
    return render_template('home.html')


@app.route('/create_meeting')
def create_meeting():
    return render_template('create_meet.html')


@app.route('/meetingDetails', methods=['POST'])
def meetingDetails():
    if request.method == 'POST':
        details = {
            "topic": request.form['topic'],
            "start_time": request.form['dateTime'],
            "duration": request.form['duration'],
            "agenda": request.form.get('agenda',''),
            "settings": {
                "host_video": request.form.get('host_video', False),
                "participant_video": request.form.get('participant_video', False),
                "join_before_host": request.form.get('join_before_host', True),
                "mute_upon_entry": request.form.get('mute_upon_entry', False)
            }
        }
        info = createMeating(details)
        data = json.loads(info)
        return render_template('meeting_generated.html', info=data)
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
