from flask import Flask
import libtorrent as lt


# TODO once we the app is created, i want to create a lt sesion
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/home")
def home():
    return "<h1>Home</h1>"
