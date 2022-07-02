from flask import Blueprint, render_template

app_blueprint = Blueprint('app_blueprint', __name__)


@app_blueprint.route('/')
def index():
    return render_template("index.html")

@app_blueprint.route('/users')
def users():
    return render_template("js-grid.html")

@app_blueprint.route('/ajout')
def addSiteRadio():
    return render_template("Acces_Mobile.html")

@app_blueprint.route('/login', methods=['GET','POST'])
def login():
    return render_template("Login.html")