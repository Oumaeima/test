from flask import Flask, redirect, request, url_for, session, render_template, flash
from flask_mysqldb import MySQL, MySQLdb
import bcrypt
import mysql.connector
from functools import wraps

### connection avec la base de donnees
connection = mysql.connector.connect(host='localhost',port='3306',database='my-app',user='root',password='')
cursor = connection.cursor()
cursor2 = connection.cursor(buffered=True)
siteidCursor = connection.cursor(buffered=True)
delegationCursor = connection.cursor(buffered=True)


app = Flask(__name__)


### login_required
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'loggedin' in session:
            return test(*args, **kwargs)    
        else:
            return redirect(url_for('login'))
    return wrap


### index page
@app.route('/')
@login_required
def index():
    return render_template("index.html")

### configuration mobile page
@app.route('/configuration')
@login_required
def configMobile():
    siteCursor = connection.cursor(buffered=True)
    siteCursor.execute("SELECT * FROM site_radio")
    allData = siteCursor.fetchall()
    siteCursor.close()
    return render_template("ConfigMobile.html" ,allData=allData)


### ajouter utilisateur
@app.route('/users')
@login_required
def users():
    return render_template("js-grid.html")

### ajouter site radio
@app.route('/ajout', methods=['GET','POST'])
@login_required
def addSiteRadio():

    if request.method == 'POST':
        sitename = request.form['Nom_Site']
        acces = request.form['Accés']
        dates = request.form['Date_Service']
        types = request.form['Type_Station']
        hba = request.form['HBA']
        surfaceS = request.form['Surface_Site']
        locataire = request.form['Locataire']
        surfaceU = request.form['Surface_Utilise']
        loyer = request.form['Loyer_Actuel']
        surfaceD = request.form['Surface_Disponible']
        region = request.form['Region']
        deligation = request.form['Deligation']
        fournisseur = request.form['Fournisseur']
        
        if  sitename == "" or acces == "" or  dates == "" or types == "" or hba == "" or surfaceS == "" or locataire == "" or surfaceU == "" or loyer == "" or surfaceD == "" or region == "" or deligation == "" or fournisseur == "":
            flash("Vérifier les champs obligatoire")

        else:
            cursor.execute("INSERT INTO site_radio(Nom_Site, Accés, Date_Service, Type_Station, HBA, Surface_Site, Locataire, Surface_Utilise, Loyer_Actuel, Surface_Disponible, Region, Deligation, Fournisseur) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(sitename, acces, dates, types, hba, surfaceS, locataire, surfaceU, loyer, surfaceD, region, deligation, fournisseur))
        
            connection.commit()
            cursor.close()
        

    return render_template("Site.html")


### ajouter cellule
@app.route('/ajout-cellule', methods=['GET','POST'])
@login_required
def addCellule():
   
    cursor2.execute("SELECT * FROM region")
    Region = cursor2.fetchall()

    siteidCursor.execute("SELECT * FROM site_radio")
    sitename = siteidCursor.fetchall()

    delegationCursor.execute("SELECT * FROM delegation, region WHERE region_id=id_r".format(Region[0]))
    listDelegation = delegationCursor.fetchall()
  
    if request.method == 'POST':
        site_name = request.form['site_Name']
        Azimuth = request.form['Azimuth']
        Power = request.form['Power']
        Technologie = request.form['Technologie']
        RNC = request.form['RNC']
        ICH = request.form['ICH']
        Delegation = request.form['Delegation']
        cel_name = request.form['Name']
        Antene = request.form['Antene']
        BSC = request.form['BSC']
        RCCH = request.form['RCCH']
        LAC = request.form['LAC']
        region = request.form['Region']
        
        if  sitename == "" or Azimuth == "" or  Power == "" or Technologie == "" or RNC == "" or ICH == "" or Delegation == "" or Region == "" or cel_name == "" or Antene == "" or BSC == "" or RCCH == "" or LAC == "":
            flash("Vérifier les champs obligatoire")

        else:
            cursor.execute("INSERT INTO cellule (site_Name, Azimuth, Power, Technologie, RNC, ICH, Delegation, Region, Name, Antene, BSC, RCCH, LAC) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(site_name, Azimuth, Power, Technologie, RNC, ICH, Delegation, region, cel_name, Antene, BSC, RCCH, LAC))
        
            connection.commit()
            cursor.close()
        

    return render_template("Cellule.html", Region=Region, sitename=sitename, listDelegation=listDelegation) 

## login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM admin WHERE email=%s AND password=%s", (email, password))
        record = cursor.fetchone()

        if record:
            session['loggedin'] = True
            session['email'] = record[4]
            return redirect(url_for('index'))
        else:
            return flash("error")
    return render_template("Login.html")
    
### logout    
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    return redirect(url_for('login'))

### documentation
@app.route('/documentation', methods=['GET','POST'])
@login_required
def docMobile():
    
    return render_template("DocMobile.html")

### visite guidé
@app.route('/visite-guidé', methods=['GET','POST'])
@login_required
def visiteMobile():
    
    return render_template("VisiteMobile.html")

if __name__ == '__main__':
    app.secret_key = "(amani)@###"
    app.run(debug=True)
