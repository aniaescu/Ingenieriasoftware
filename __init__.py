from flask import Flask, render_template

app = Flask(__name__, template_folder='../templates')

@app.route("/")
@app.route("/<name>")
def hello_world(name=None):
    return render_template('hello.html', name=name)