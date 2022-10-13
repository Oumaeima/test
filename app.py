from flask import Flask, redirect, request, url_for, session, render_template, flash
from flask_mysqldb import MySQL, MySQLdb
import bcrypt
import mysql.connector
from functools import wraps
from flask_paginate import Pagination, get_page_parameter

### connection avec la base de donnees
connection = mysql.connector.connect(host='localhost',port='3306',database='my-app',user='root',password='')
cursor = connection.cursor()
cursor2 = connection.cursor(buffered=True)
cursor3 = connection.cursor(buffered=True)
cursor4 = connection.cursor(buffered=True)
cursor5 = connection.cursor(buffered=True)
cursor6 = connection.cursor(buffered=True)
siteidCursor = connection.cursor(buffered=True)
delegationCursor = connection.cursor(buffered=True)
RGidCursor = connection.cursor(buffered=True)
cursorSite = connection.cursor(buffered=True)
cursorCell = connection.cursor(buffered=True)
docCursor = connection.cursor(buffered=True)
intCursor = connection.cursor(buffered=True)
visiteCursor = connection.cursor(buffered=True)

cursor2.execute("SELECT * FROM region")
Region = cursor2.fetchall()

siteidCursor.execute("SELECT * FROM site_radio")
sitename = siteidCursor.fetchall()

delegationCursor.execute("SELECT * FROM delegation, region WHERE region_id=id_r".format(Region[0]))
listDelegation = delegationCursor.fetchall()

RGidCursor.execute("SELECT * FROM repartition")
rg_id = RGidCursor.fetchall()


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
        

@app.route('/search', methods=['GET', 'POST'])
def search2():
    if request.method == "POST":
        res = request.form['q']
        cursor.execute("SELECT * FROM site_radio WHERE Nom_Site = %s", (res,))
         
        data = cursor.fetchall()
        print(data)
        return redirect(url_for('search2', data=data))
    return redirect(url_for('search2'))
   

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
    return render_template("ConfigMobile.html" ,allData=allData, sitename=sitename, Region=Region, listDelegation=listDelegation)


### ajouter utilisateur
@app.route('/user', methods=['GET','POST'])
@login_required
def addUsers():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        cursor.execute("SELECT email FROM admin WHERE nom=%s",(email,))
        name = cursor.fetchone()

        if  nom == "" or prenom == "" or  email == "" or role == "" or password == "" :
            flash("Vérifier les champs obligatoire")
        elif name:
            flash("nom de l'utilisateur existe déja")  

        else:
            cursor.execute("INSERT INTO admin(nom, prenom, email, password, role) VALUES (%s,%s,%s,%s,%s)",(nom, prenom, email, password, role))
        
            connection.commit()

        return redirect(url_for('ListUsers'))    


### ajouter utilisateur
@app.route('/edit_user/<string:user_id>', methods=['GET','POST'])
@login_required
def editUsers(user_id):
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        cursor.execute("SELECT email FROM admin WHERE nom=%s",(email,))
        name = cursor.fetchone()

        if  nom == "" or prenom == "" or  email == "" or role == "" or password == "" :
            flash("Vérifier les champs obligatoire")
        elif name:
            flash("nom de l'utilisateur existe déja")  

        else:
            cursor.execute("UPDATE admin SET nom=%s, prenom=%s, email=%s, password=%s, role=%s WHERE id=%s",(nom, prenom, email, password, role, user_id,))
        
            connection.commit()
            return redirect(url_for('ListUsers')) 
        return render_template("GereUsers.html", user_id = user_id)

        

## Delete User
@app.route('/delete_user/<string:user_id>', methods=['GET','POST'])
@login_required
def deleteUser(user_id):

    cursor.execute("DELETE FROM admin WHERE id=%s", (user_id,))
    connection.commit()
    
    return redirect(url_for('ListUsers'))        
    

### ajouter utilisateur
@app.route('/users', methods=['GET','POST'])
@login_required
def ListUsers():
    cursor.execute("SELECT * FROM admin")
    listeUsers = cursor.fetchall()

    return render_template("GereUsers.html", users = listeUsers)

### generale Acces Mobile
@app.route('/details_mobile', methods=['GET','POST'])
@login_required
def generaleMobile():
    cursorSite.execute("SELECT * FROM site_radio ORDER BY Site_id ASC")
    total = cursorSite.fetchall()

    page = request.args.get(get_page_parameter(), type=int, default=1)  
    per_page = 5
    offset = (page - 1) * per_page
    pagination = Pagination(page=page, per_page=per_page,total=len(total))   
    numrows = int(cursorSite.rowcount)

    cursorSite.execute("SELECT * FROM site_radio LIMIT %s OFFSET %s", (per_page, offset,))
    site = cursorSite.fetchall()

    cursorCell.execute("SELECT * FROM cellule")
    cellule = cursorCell.fetchall()

    return render_template("GeneraleMobile.html", site=site, cellule=cellule, Region=Region, listDelegation=listDelegation, sitename=sitename, pagination=pagination, numrows=numrows, total=total)


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
        delegation = request.form['Delegation']
        fournisseur = request.form['Fournisseur']
        
        siteidCursor.execute("SELECT Nom_Site FROM site_radio WHERE Nom_Site=%s",(sitename,))
        name = siteidCursor.fetchone()

        if  sitename == "" or acces == "" or  dates == "" or types == "" or hba == "" or surfaceS == "" or locataire == "" or surfaceU == "" or loyer == "" or surfaceD == "" or region == "" or delegation == "" or fournisseur == "":
            flash("Vérifier les champs obligatoire")
        elif name:
            flash("nom du site existe déja")  

        else:
            cursor.execute("INSERT INTO site_radio(Nom_Site, Accés, Date_Service, Type_Station, HBA, Surface_Site, Locataire, Surface_Utilise, Loyer_Actuel, Surface_Disponible, Region, Deligation, Fournisseur) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(sitename, acces, dates, types, hba, surfaceS, locataire, surfaceU, loyer, surfaceD, region, delegation, fournisseur))
        
            connection.commit()
            siteidCursor.execute("SELECT Site_id FROM site_radio WHERE Nom_Site=%s",(sitename,))
            id = siteidCursor.fetchone()
            
           ## return redirect(url_for("addCellule"))
            return render_template("Cellule.html", Region=Region, listDelegation=listDelegation, id=id)
    return render_template("ConfigMobile.html", Region=Region, listDelegation=listDelegation)    

    



## Detail Site
@app.route('/detail_site/<int:site_id>', methods=['GET','POST'])
@login_required
def siteDetail(site_id):
    
    cursor.execute("SELECT * FROM cellule WHERE site_id=%s", (site_id,))
    cellule = cursor.fetchall()

    docCursor.execute("SELECT * FROM document_mobile WHERE site_id=%s ORDER BY site_id ASC", (site_id,))
    doc = docCursor.fetchall()

    visiteCursor.execute("SELECT * FROM visite_mobile WHERE site_id=%s ORDER BY site_id ASC", (site_id,))
    visite = cursor.fetchall()

    intCursor.execute("SELECT * FROM intervention WHERE site_id=%s ORDER BY site_id ASC", (site_id,))
    intervention = cursor.fetchall()
    
    return render_template("DetailSite.html",cellule=cellule, doc=doc, visite=visite, intervention=intervention, Region=Region, listDelegation=listDelegation) 


''' ## Detail Documentation
@app.route('/edit_doc/<int:doc_id>', methods=['GET','POST'])
@login_required
def documentationEdit(doc_id):

    if request.method == "POST":
        Site_id = request.form['Site_id']
        Delegation = request.form['Delegation']
        region = request.form['Region']
        Type = request.form['type']
        document = request.form['documentation']
    
        cursor.execute("UPDATE document_mobile SET region=%s, delegation=%s, type_d=%s, documentation=%s WHERE id_d=%s ORDER BY site_id ASC", (region, Delegation, Type, document, doc_id,))
        
        docCursor.execute("SELECT * FROM document_mobile WHERE site_id=%s ORDER BY site_id ASC", (Site_id,))
        doc = docCursor.fetchall()
        
        return render_template("DetailSite.html", doc_id=doc_id, doc=doc, Region=Region, listDelegation=listDelegation) 
    return redirect(url_for('detail_site',doc_id=doc_id)) '''

## Detail Intervention
@app.route('/detail_int/<int:site_id>', methods=['GET','POST'])
@login_required
def interventionDetail(site_id):
    
    cursor.execute("SELECT * FROM intervention WHERE site_id=%s ORDER BY site_id ASC", (site_id,))
    id = cursor.fetchall()

    page = request.args.get(get_page_parameter(), type=int, default=1)  
    per_page = 1
    offset = (page - 1) * per_page
    pagination = Pagination(page=page, per_page=per_page,total=len(id))   
    numrows = int(cursor.rowcount)

    cursor.execute("SELECT * FROM intervention WHERE site_id=%s ORDER BY site_id ASC LIMIT %s OFFSET %s", (site_id, per_page, offset,))
    site = cursor.fetchall()
    
    return render_template("DetailSite.html",int=site, id=id, Region=Region, listDelegation=listDelegation, pagination=pagination, numrows=numrows,total=id) 


## Detail visite guider
@app.route('/detail_visite/<int:site_id>', methods=['GET','POST'])
@login_required
def visiteDetail(site_id):
    
    cursor.execute("SELECT * FROM visite_mobile WHERE site_id=%s ORDER BY site_id ASC", (site_id,))
    id = cursor.fetchall()

    page = request.args.get(get_page_parameter(), type=int, default=1)  
    per_page = 1
    offset = (page - 1) * per_page
    pagination = Pagination(page=page, per_page=per_page,total=len(id))   
    numrows = int(cursor.rowcount)

    cursor.execute("SELECT * FROM visite_mobile WHERE site_id=%s ORDER BY site_id ASC LIMIT %s OFFSET %s", (site_id, per_page, offset,))
    site = cursor.fetchall()
    
    return render_template("DetailSite.html",visite=site, id=id, Region=Region, listDelegation=listDelegation, pagination=pagination, numrows=numrows,total=id) 


### Edit Site
@app.route('/edit_site/<int:site_id>', methods=['GET','POST'])
@login_required
def editSite(site_id):

    if request.method == "POST":
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
        delegation = request.form['Delegation']
        fournisseur = request.form['Fournisseur']
        
        cursor.execute("""
              UPDATE site_radio SET Nom_Site=%s, Accés=%s, Date_Service=%s, Type_Station=%s, HBA=%s, Surface_Site=%s, Locataire=%s, Surface_Utilise=%s, Loyer_Actuel=%s, Surface_Disponible=%s, Region=%s, Deligation=%s, Fournisseur=%s WHERE Site_id=%s
            """, (sitename, acces, dates, types, hba, surfaceS, locataire, surfaceU, loyer, surfaceD, region, delegation, fournisseur, site_id))
        connection.commit()
        
        return redirect(url_for('generaleMobile'))




## Delete Site
@app.route('/delete_site/<int:site_id>', methods=['GET','POST'])
@login_required
def deleteSite(site_id):
    
    cursor.execute("DELETE FROM site_radio WHERE Site_id=%s", (site_id,))
    connection.commit()
    
    return redirect(url_for('generaleMobile')) 



### ajouter cellule
@app.route('/ajout-cellule', methods=['GET','POST'])
@login_required
def addCellule():
    
    if request.method == 'POST':
        site_id = request.form['Site_id']
        Azimuth = request.form['Azimuth']
        Bande = request.form['Bande']
        Technologie = request.form['Technologie']
        RNC = request.form['RNC']
        TCH = request.form['TCH']
        Delegation = request.form['Delegation']
        cel_name = request.form['Name']
        Antene = request.form['Antene']
        BSC = request.form['BSC']
        BCH = request.form['BCH']
        LAC = request.form['LAC']
        region = request.form['Region']

        siteidCursor.execute("SELECT Site_id FROM site_radio WHERE Site_id=%s",(site_id,))
        id_site = siteidCursor.fetchone()

        cursor.execute("SELECT Name FROM cellule WHERE Name=%s",(cel_name,))
        name = cursor.fetchone()
        
        if  Azimuth == "" or  Bande == "" or Technologie == "Select Technologie" or Delegation == "Select Delegation" or Region == "Select Region" or cel_name == "" or Antene == "":
            flash("Vérifier les champs obligatoire")

        elif name:
            flash("nom du cellule existe déja") 

        else:
            cursor.execute("INSERT INTO cellule (site_id, Azimuth, Bande, Technologie, RNC, TCH, Delegation, Region, Name, Antene, BSC, BCH, LAC) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(site_id, Azimuth, Bande, Technologie, RNC, TCH, Delegation, region, cel_name, Antene, BSC, BCH, LAC))
            connection.commit()
            
            return redirect(url_for('generaleMobile'))
    


### Edit Cellule
@app.route('/edit/<string:cel_id>', methods=['GET','POST'])
@login_required
def edit(cel_id):
    
    cursorCell.execute("SELECT * FROM cellule WHERE id=%s",(cel_id,))
    cellule = cursorCell.fetchall()
    return render_template("EditCellule.html", cellule=cellule, Region=Region, listDelegation=listDelegation,)


### Edit Cellule
@app.route('/edit_cel/<string:cel_id>', methods=['GET','POST'])
@login_required
def editCellule(cel_id): 
    
    if request.method == "POST":
        Site_id = request.form['site_id']
        Azimuth = request.form['Azimuth']
        Bande = request.form['Bande']
        Delegation = request.form['Delegation']
        cel_name = request.form['Name']
        Antene = request.form['Antene']
        region = request.form['Region']
        
        cursor.execute("""
              UPDATE cellule SET Azimuth=%s, Bande=%s,  Delegation=%s, Region=%s, Name=%s, Antene=%s WHERE id=%s
              """,(Azimuth, Bande, Delegation, region, cel_name, Antene, cel_id))
        
        connection.commit()
        siteidCursor.execute("SELECT Site_id FROM site_radio WHERE Site_id=%s", (Site_id,))
        site = siteidCursor.fetchone()

        

        return redirect(url_for('siteDetail', site_id=site))
        
    return redirect(url_for('siteDetail', site_id=site))
        
       


## Delete Cellule
@app.route('/delete_cel/<string:cel_id>', methods=['GET','POST'])
@login_required
def deleteCellule(cel_id):
    
    cursor.execute("DELETE FROM cellule WHERE id=%s", (cel_id,))
    connection.commit()
    
    return redirect(url_for('generaleMobile')) 



### documentation
@app.route('/documentation', methods=['GET','POST'])
@login_required
def docMobile():

    if request.method == "POST":
        site_id = request.form['Site_id']
        region = request.form['Region']
        Delegation = request.form['Delegation']       
        typeDoc = request.form['type']
        Doc = request.form['documentation']
        
        if  Delegation == "Select Delegation" or region == "Select Region" or Doc == "":
            flash("Vérifier les champs obligatoire")
        else:
            cursor.execute("INSERT INTO document_mobile (region, delegation, site_id, type_d, documentation) VALUES (%s,%s,%s,%s,%s)", (region, Delegation, site_id, typeDoc, Doc) )
            connection.commit()
         
            return redirect(url_for('generaleMobile'))

    return render_template("DocMobile.html", Region=Region, sitename=sitename, listDelegation=listDelegation)


## Delete documentation
@app.route('/delete_doc/<string:doc_id>', methods=['GET','POST'])
@login_required
def deleteDoc(doc_id):
    
    cursor.execute("DELETE FROM document_mobile WHERE id_d=%s", (doc_id,))
    connection.commit()
    
    return redirect(url_for('generaleMobile'))


### edit documentation
@app.route('/edit_doc/<string:doc_id>', methods=['GET','POST'])
@login_required
def editDoc(doc_id):

    if request.method == "POST":
        site_id = request.form['Site_id']
        region = request.form['Region']
        Delegation = request.form['Delegation']       
        typeDoc = request.form['type']
        
        
        if  region == "" or Delegation == "" or  typeDoc == "":
            flash("Vérifier les champs obligatoire")
        

        else:
       
            cursor.execute("""
                UPDATE document_mobile SET region=%s, delegation=%s, type_d=%s WHERE id_d=%s
                """,(region, Delegation, typeDoc, doc_id))
            
            return redirect(url_for('generaleMobile'))

        return render_template("DocMobile.html", Region=Region, sitename=sitename, listDelegation=listDelegation, doc_id=doc_id)



### visite guidé
@app.route('/visite-guidé', methods=['GET','POST'])
@login_required
def visiteMobile():

    if request.method == "POST":
        region = request.form['Region']
        Delegation = request.form['Délegation']
        Doc = request.form['URL']
        
        if  Delegation == "Select Delegation" or region == "Select Region" or Doc == "":
            flash("Vérifier les champs obligatoire")
        else:
            cursor.execute("INSERT INTO visite_mobile (region, delegation, url) VALUES (%s,%s,%s)", (region, Delegation, Doc) )
            connection.commit()
            cursor.close()
    
    return render_template("VisiteMobile.html", Region=Region, listDelegation=listDelegation)


### generale Acces fixe
@app.route('/details', methods=['GET','POST'])
@login_required
def generaleAF():
    cursor3.execute("SELECT * FROM repartition")
    listRG = cursor3.fetchall()

    cursor4.execute("SELECT * FROM sousrepartition")
    listSR = cursor4.fetchall()

    cursor5.execute("SELECT * FROM msan")
    listMSAN = cursor5.fetchall()

    cursor6.execute("SELECT * FROM pc")
    listPC = cursor6.fetchall()

    return render_template("GeneraleAF.html", listRG=listRG, listSR=listSR, listMSAN=listMSAN, listPC=listPC, Region=Region, listDelegation=listDelegation)

### Acces fixe
@app.route('/config_acces', methods=['GET','POST'])
@login_required
def configAF():
    return render_template("ConfigAcces.html", Region=Region, listDelegation=listDelegation, rg_id=rg_id)

### Add Repartition
@app.route('/add_repartition', methods=['GET','POST'])
@login_required
def addRepartition():

    if request.method == "POST":
        name = request.form['name']
        x = request.form['x']
        y = request.form['y']
        region = request.form['Region']
        Delegation = request.form['Delegation']
        
        if  name == "" or x == "" or y == "" or Delegation == "Select Delegation" or region == "Select Region":
            flash("Vérifier les champs obligatoire")
        else:
            cursor.execute("INSERT INTO repartition (nom, x, y, region, delegation) VALUES (%s,%s,%s,%s,%s)", (name, x, y, region, Delegation) )
            connection.commit()
            
            return redirect(url_for("generaleAF"))

    return render_template("ConfigAcces.html", Region=Region, listDelegation=listDelegation)


## Edite Repartition
@app.route('/edit_repartition/<int:rep_id>', methods=['GET','POST'])
@login_required
def editRepartition(rep_id):
    if request.method == 'POST':
        name = request.form['name']
        x = request.form['x']
        y = request.form['y']
        region = request.form['Region']
        Delegation = request.form['Delegation']

        cursor.execute("""
              UPDATE repartition 
              SET nom=%s, x=%s, y=%s , region=%s , delegation=%s WHERE id=%s
            """, (name, x, y, region, Delegation, rep_id))
        connection.commit()
        
        return redirect(url_for('generaleAF'))


## Delete Repartition
@app.route('/delete_repartition/<int:rep_id>', methods=['GET','POST'])
@login_required
def deleteRepartition(rep_id):
    
    cursor.execute("DELETE FROM repartition WHERE id=%s", (rep_id,))
    connection.commit()
    cursor.close()
    return redirect(url_for('generaleAF'))   



### Add Sous Repartition
@app.route('/add_SR', methods=['GET','POST'])
@login_required
def addSR():

    if request.method == "POST":
        RG_ID = request.form['rg_id']
        name = request.form['name']
        x = request.form['x']
        y = request.form['y']
        Capacité = request.form['Capacité']
        paireO = request.form['paireO']
        paireL = request.form['paireL']
        
        if RG_ID == "Select RG_ID" or name == "" or x == "" or y == "" or Capacité == "" or paireO == "" or paireL == "":
            flash("Vérifier les champs obligatoire")
        else:
            cursor.execute("INSERT INTO sousrepartition (id_rg, nom, x, y, capacite, paire_occupe, paire_libre) VALUES (%s,%s,%s,%s,%s,%s,%s)", (RG_ID,name, x, y, Capacité, paireO, paireL) )
            connection.commit()
            return redirect(url_for("generaleAF"))
            

### Redirect to edit msan
@app.route('/edit_SR/<string:id_sr>', methods=['GET','POST'])
@login_required
def redirectEditSR(id_sr):
    
    cursor.execute("SELECT * FROM sousrepartition WHERE id_sr=%s",(id_sr,))
    msan = cursor.fetchall()
    return render_template("EditSR.html", msan=msan)
  

## Edite Sous Repartition
@app.route('/edit_sr/<int:sr_id>', methods=['GET','POST'])
@login_required
def editSR(sr_id):
    if request.method == 'POST':
        RG_ID = request.form['rg_id']
        name = request.form['name']
        x = request.form['x']
        y = request.form['y']
        Capacité = request.form['Capacité']
        paireO = request.form['paireO']
        paireL = request.form['paireL']

        cursor.execute("""
              UPDATE sousrepartition SET id_rg=%s, nom=%s, x=%s, y=%s, capacite=%s, paire_occupe=%s, paire_libre=%s WHERE id_sr=%s
            """, (RG_ID, name, x, y, Capacité, paireO, paireL, sr_id))
        connection.commit()
        
        return redirect(url_for('generaleAF'))


## Delete Sous Repartition
@app.route('/delete_sr/<int:sr_id>', methods=['GET','POST'])
@login_required
def deleteSR(sr_id):
    
    cursor.execute("DELETE FROM sousrepartition WHERE id_sr=%s", (sr_id,))
    connection.commit()
    
    return redirect(url_for('generaleAF'))   


### Add MSAN
@app.route('/add_MSAN', methods=['GET','POST'])
@login_required
def addMSAN():

    if request.method == "POST":
        RG_ID = request.form['rg_id']
        name = request.form['name']
        x = request.form['x']
        y = request.form['y']
        NB_ports = request.form['NB_ports']
        paireO = request.form['paireO']
        paireL = request.form['paireL']
        
        if name == "" or x == "" or y == "" or NB_ports == "" or paireO == "" or paireL == "":
            flash("Vérifier les champs obligatoire")
        else:
            cursor.execute("INSERT INTO msan (id_rg, nom, x, y, nb_ports, paire_occupe, paire_libre) VALUES (%s,%s,%s,%s,%s,%s,%s)", (RG_ID,name, x, y, NB_ports, paireO, paireL) )
            connection.commit()
            return redirect(url_for("generaleAF"))


### Redirect to edit msan
@app.route('/edit_msan/<string:msan_id>', methods=['GET','POST'])
@login_required
def redirectEdit(msan_id):
    
    cursor.execute("SELECT * FROM msan WHERE id_m=%s",(msan_id,))
    msan = cursor.fetchall()
    return render_template("EditeMSAN.html", msan=msan)



### Edit MSAN
@app.route('/edit_MSAN/<string:msan_id>', methods=['GET','POST'])
@login_required
def editMSAN(msan_id):

    if request.method == "POST":
        RG_ID = request.form['rg_id']
        name = request.form['name']
        x = request.form['x']
        y = request.form['y']
        NB_ports = request.form['NB_ports']
        paireO = request.form['paireO']
        paireL = request.form['paireL']
        
        cursor.execute("""
              UPDATE msan SET id_rg=%s, nom=%s, x=%s, y=%s, nb_ports=%s, paire_occupe=%s, paire_libre=%s WHERE id_m=%s
            """, (RG_ID, name, x, y, NB_ports, paireO, paireL, msan_id))
        connection.commit()
        
        return redirect(url_for('generaleAF'))
            


## Delete MASN
@app.route('/delete_msan/<int:msan_id>', methods=['GET','POST'])
@login_required
def deleteMSAN(msan_id):
    
    cursor.execute("DELETE FROM msan WHERE id_m=%s", (msan_id,))
    connection.commit()
    
    return redirect(url_for('generaleAF')) 


## Detail PC
@app.route('/detail_pc', methods=['GET','POST'])
@login_required
def detailPC():
    
    cursor.execute("SELECT * FROM pc")
    pc = cursor.fetchall()
    
    return render_template("GestionPC.html", pc=pc)


### Add PC
@app.route('/add_PC', methods=['GET','POST'])
@login_required
def addPC():

    if request.method == "POST":
        name = request.form['name']
        x = request.form['x']
        y = request.form['y']
        Type = request.form['Type']
        paireO = request.form['paireO']
        paireL = request.form['paireL']
        
        if  name == "" or x == "" or y == "" or Type == "Select Type" or paireO == "" or paireL == "":
            flash("Vérifier les champs obligatoire")
        else:
            cursor.execute("INSERT INTO pc (nom, x, y, paire_occupe, paire_libre, type) VALUES (%s,%s,%s,%s,%s,%s)", (name, x, y, paireO, paireL, Type) )
            connection.commit()
            return redirect(url_for("generaleAF"))
            

    return render_template("ConfigAcces.html", rg_id=rg_id)


### Edit PC
@app.route('/edit_pc/<int:pc_id>', methods=['GET','POST'])
@login_required
def editPC(pc_id):

    if request.method == "POST":
        name = request.form['name']
        x = request.form['x']
        y = request.form['y']
        Type = request.form['Type']
        paireO = request.form['paireO']
        paireL = request.form['paireL']
        
        cursor.execute("""
              UPDATE pc SET nom=%s, x=%s, y=%s, paire_occupe=%s, paire_libre=%s, type=%s WHERE id_pc=%s
            """, (name, x, y, paireO, paireL, Type, pc_id))
        connection.commit()
        
        return redirect(url_for('generaleAF'))


## Delete PC
@app.route('/delete_pc/<int:pc_id>', methods=['GET','POST'])
@login_required
def deletePC(pc_id):
    
    cursor.execute("DELETE FROM pc WHERE id_pc=%s", (pc_id,))
    connection.commit()
    
    return redirect(url_for('generaleAF')) 


## Detail Site
@app.route('/detail_repartition/<string:rg_id>', methods=['GET','POST'])
@login_required
def RGDetail(rg_id):
    
    cursor.execute("SELECT * FROM msan WHERE id_rg=%s", (rg_id,))
    msan = cursor.fetchall()
    cursor2.execute("SELECT * FROM sousrepartition WHERE id_rg=%s", (rg_id,))
    sr = cursor2.fetchall()
    
    return render_template("DetailRG.html",msan=msan, sr=sr, Region=Region, listDelegation=listDelegation) 




## edit profile
@app.route('/profile/<int:id>', methods=['GET','POST'])
@login_required
def profile(id):
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']

        cursor.execute("""
              UPDATE admin SET nom=%s, prenom=%s, email=%s WHERE id=%s
              """, (nom, prenom, email,id))
        connection.commit()
        return redirect(url_for('index'))
    return render_template('Profile.html', idUser=id)


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
            session['id'] = record[0]
            session['nom'] = record[1]
            session['prenom'] = record[2]
            session['email'] = record[3]
            session['password'] = record[4]
            
            return redirect(url_for('index'))
        else:
            return flash("error")
    return render_template("Login.html")
    
### logout    
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.secret_key = "(amani)@###"
    app.run(debug=True)
