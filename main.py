from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash
import os
from datetime import datetime, timedelta


# Template folder is "html"
# Static folder is "files"
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'super secret key'
cookie_exp = datetime.now() + timedelta(hours=3)

date = datetime.now().strftime("%d/%m/%Y")
title = "Esame del " + date
num_ex = 6
row_size = 3
exercises = [i for i in range(1, num_ex+1)]


def is_logged_in(cookies, ip) -> bool:
    """
    Check if the user is logged in.

    Args:
        cookies (dict): Dictionary of cookies of the user.
        ip (str): IP address of the user.

    Returns:
        bool: True if the user is logged in, False otherwise.
    """
    has_cookies = "nome" in cookies and "cognome" in cookies and "matr" in cookies and "ip" in cookies
    has_folder = os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], ip))
    return has_cookies and has_folder


def allowed_file(filename: str) -> bool:
    """
    Check if the file is allowed to be uploaded.

    Args:
        filename (str): Name of the file to check.

    Returns:
        bool: True if the file is allowed, False otherwise.
    """
    ALLOWED_EXTENSIONS = {'py'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Web page for logging in.
    """
    # Get the IP address of the user
    ip = request.remote_addr.replace(".", "_")

    # Check if the user is already logged in
    if is_logged_in(request.cookies, ip):
        return redirect(url_for("exam"))

    # Check if the user is trying to log in
    if request.method == "POST":
        # Check if the user has inserted all the data
        if len(request.form["nome"]) == 0 or len(request.form["cognome"]) == 0 or len(request.form["matr"]) == 0:
            flash("ATTENZIONE: Devi inserire tutti i dati", "error")
            return redirect(url_for("login"))

        # Create a cookie with the nome, cognome and matricola
        resp = redirect(url_for("exam"))
        resp.set_cookie("nome", request.form["nome"], expires=cookie_exp)
        resp.set_cookie("cognome", request.form["cognome"], expires=cookie_exp)
        resp.set_cookie("matr", request.form["matr"], expires=cookie_exp)
        resp.set_cookie("ip", ip, expires=cookie_exp)

        # Create a folder for the user
        folder = os.path.join(app.config['UPLOAD_FOLDER'], ip)
        os.makedirs(folder, exist_ok=True)
        # Create a file for the user
        with open(os.path.join(folder, "info.txt"), "a") as f:
            time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            f.write(f"Nome: {request.form['nome']}\n")
            f.write(f"Cognome: {request.form['cognome']}\n")
            f.write(f"Matricola: {request.form['matr']}\n")
            f.write(f"IP: {ip}\n")
            f.write(f"Data: {time}\n")

        return resp

    # Show the login page
    return render_template("login.html", title="Login")


@app.route("/")
def exam():
    """
    Web page for downloading the exam.
    """
    # Get the IP address of the user
    ip = request.remote_addr.replace(".", "_")

    # Check if the user is logged in, otherwise redirect to the login page
    if not is_logged_in(request.cookies, ip):
        return redirect(url_for("login"))

    # Check if the user has already uploaded files
    folder = os.path.join(app.config['UPLOAD_FOLDER'], ip)
    rows = []  # List of (exercise number, already_uploaded)
    row = []
    for ex in exercises:
        filename = f"es{ex}.py"
        exists = os.path.isfile(os.path.join(folder, filename))
        row.append((ex, exists))
        # If the row is full, add it to the list and create a new one
        if len(row) == row_size:
            rows.append(row)
            row = []
    # If the last row is not full, add it to the list
    if len(row) > 0:
        rows.append(row)

    # Show the exam page
    return render_template("exam.html", title=title, rows=rows)


@app.route("/exercise/<n_exercise>", methods=["GET", "POST"])
def upload(n_exercise):
    """
    Web page for uploading the exercises.
    """
    # Get the exercise number
    n_exercise = int(n_exercise)

    # Get the IP address of the user
    ip = request.remote_addr.replace(".", "_")

    # Check if the user is logged in, otherwise redirect to the login page
    if not is_logged_in(request.cookies, ip):
        return redirect(url_for("login"))

    # Check if the user has already uploaded the file
    folder = os.path.join(app.config['UPLOAD_FOLDER'], ip)
    filename = f"es{n_exercise}.py"
    if os.path.isfile(os.path.join(folder, filename)):
        already_uploaded = filename
    else:
        already_uploaded = None

    # Check if the user is trying to upload a file
    if request.method == "POST":
        # Check if the user has selected a file
        if 'file' not in request.files:
            flash("ATTENZIONE: Devi selezionare un file", "error")
            return redirect(request.url)

        # Get the file
        file = request.files['file']
        # Check if the user has selected a file
        if file.filename == '':
            flash("ATTENZIONE: Devi selezionare un file", "error")
            return redirect(request.url)

        # Check if the file is allowed
        if not allowed_file(file.filename):
            flash("ATTENZIONE: Il file deve essere un file python", "error")
            return redirect(request.url)

        # Save the file
        filename = f"es{n_exercise}.py"
        file.save(os.path.join(
            app.config['UPLOAD_FOLDER'], request.cookies["ip"], filename))

        # Update the info file
        with open(os.path.join(app.config['UPLOAD_FOLDER'], request.cookies["ip"], "info.txt"), "a") as f:
            time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            f.write(f"{filename}: {time}\n")

        # Show the upload page
        flash("File caricato con successo", "success")
        return redirect(request.url)

    # Show the upload page
    return render_template(
        "exercise.html", title="Caricamento",
        n_exercise=n_exercise, already_uploaded=already_uploaded
    )


@app.route('/end', methods=['GET', 'POST'])
def end():
    # Get the IP address of the user
    ip = request.remote_addr.replace(".", "_")

    # Check if the user is logged in, otherwise redirect to the login page
    if not is_logged_in(request.cookies, ip):
        return redirect(url_for("login"))

    # Check if the user want to submit the exam
    if request.method == 'POST':
        confirm = request.form["confirm"]
        if confirm == "on":
            # Update the info file
            folder = os.path.join(app.config['UPLOAD_FOLDER'], ip)
            with open(os.path.join(folder, "info.txt"), "a") as f:
                time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                f.write(f"Consegna: {time}\n\n")

            # Remove the cookies
            resp = redirect(url_for("login"))
            resp.set_cookie("nome", "", expires=0)
            resp.set_cookie("cognome", "", expires=0)
            resp.set_cookie("matr", "", expires=0)
            resp.set_cookie("ip", "", expires=0)
            flash("Esame consegnato con successo", "success")
            return resp
        else:
            flash("ATTENZIONE: Devi confermare la consegna", "error")
            return redirect(url_for("exam"))

    return render_template("end.html", title="Consegna")

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)