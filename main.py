from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from werkzeug.utils import secure_filename
import os
import datetime


# Template folder is "html"
# Static folder is "files"
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'super secret key'

date = datetime.datetime.now().strftime("%d/%m/%Y")
title = "Esame del " + date


@app.route("/")
def exam():
    """
    Web page for downloading the exam.
    """
    return render_template("exam.html", title=title)


# Upload file
def allowed_file(filename):
    """
    Check if the file is allowed to be uploaded.
    """
    # TODO: Implement this function
    return True


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # get IP address of the user
        ip = request.remote_addr.replace(".", "_")

        # check if all the fields are filled
        if 'nome' not in request.form or 'cognome' not in request.form or 'matricola' not in request.form:
            flash('ATTENZIONE: Compilare tutti i campi del form')
            return redirect(request.url)

        # get data from form
        name = request.form['nome']
        surname = request.form['cognome']
        matricola = request.form['matricola']

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('ATTENZIONE: Nessun file selezionato (Error 1)')
            return redirect(request.url)
        file = request.files['file']

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('ATTENZIONE: Nessun file selezionato (Error 2)')
            return redirect(request.url)

        # If the file is valid, save it in the server
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # Create a folder for each user
            timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            path = os.path.join(app.config['UPLOAD_FOLDER'], ip, timestamp)
            os.makedirs(path, exist_ok=True)
            file.save(os.path.join(path, filename))

            # Write info file
            with open(os.path.join(path, "info.txt"), "w") as f:
                f.write("IP: " + ip + "\n")
                f.write("Name: " + name + "\n")
                f.write("Surname: " + surname + "\n")
                f.write("Matricola: " + matricola + "\n")

            return redirect(url_for('upload_file', name=filename))
    return render_template("upload.html", title="Consegna")
