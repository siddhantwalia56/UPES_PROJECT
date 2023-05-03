import os
from flask import Flask, render_template, request
from datetime import datetime
from major import index

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
        
        filename = str(int(datetime.timestamp(datetime.now()))) + '_' + f.filename
        name = filename.split("/")[-1].split(".")[0]

        f.save('static/uploads/'+filename)

        index(filename, email, language, sender_name)
        return render_template('success.html', name=sender_name, language=language, email=email, file=name)
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
