from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import render_template
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

#--------------------------------------------
# Fonctions utilitaires pour gérer les sessions
#--------------------------------------------
def est_authentifie_admin():
    """Vérifie si l'utilisateur est authentifié en tant qu'administrateur."""
    return session.get('authentifie_admin')

def est_authentifie_user():
    """Vérifie si l'utilisateur est authentifié avec le compte user."""
    return session.get('authentifie_user')
#--------------------------------------------

@app.route('/')
def hello_world():
    return render_template('hello.html')

#--------------------------------------------
# Authentification administrateur
#--------------------------------------------
@app.route('/lecture')
def lecture():
    if not est_authentifie_admin():
        # Rediriger vers la page d'authentification admin si l'utilisateur n'est pas authentifié
        return redirect(url_for('authentification_admin'))
    # Si l'utilisateur est authentifié en tant qu'admin
    return "<h2>Bravo, vous êtes authentifié en tant qu'administrateur</h2>"

@app.route('/authentification', methods=['GET', 'POST'])
def authentification_admin():
    """
    Route d'authentification pour l'administrateur.
    Identifiants : admin/password
    """
    if request.method == 'POST':
        # Vérifier les identifiants
        if request.form['username'] == 'admin' and request.form['password'] == 'password':  # password à cacher par la suite
            session['authentifie_admin'] = True
            # Rediriger vers la route lecture après une authentification réussie
            return redirect(url_for('lecture'))
        else:
            # Afficher un message d'erreur si les identifiants sont incorrects
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

#--------------------------------------------
# Authentification User (nouvelle)
#--------------------------------------------
@app.route('/authentification_user', methods=['GET', 'POST'])
def authentification_user():
    """
    Route d'authentification pour l'utilisateur simple.
    Identifiants : user/12345
    """
    if request.method == 'POST':
        if request.form['username'] == 'user' and request.form['password'] == '12345':
            session['authentifie_user'] = True
            # Redirection vers /fiche_nom/ après authentification
            return redirect(url_for('fiche_nom'))
        else:
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)
#--------------------------------------------

#--------------------------------------------
# Consultation de la BDD
#--------------------------------------------
@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    # Rendre le template HTML et transmettre les données
    return render_template('read_data.html', data=data)

@app.route('/consultation/')
def ReadBDD():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

#--------------------------------------------
# Nouvelle route pour la recherche par nom
#--------------------------------------------
@app.route('/fiche_nom/', methods=['GET', 'POST'])
def fiche_nom():
    """
    Recherche par le nom d'un client.
    Nécessite une authentification user (user/12345).
    """
    # Vérifier si l'utilisateur est authentifié (compte user)
    if not est_authentifie_user():
        return redirect(url_for('authentification_user'))

    data = []
    if request.method == 'POST':
        nom_recherche = request.form.get('nom')
        if nom_recherche:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            # Requête simplifiée : on cherche tous les enregistrements dont "nom" correspond
            # Ici on utilise un LIKE pour la souplesse de recherche
            cursor.execute("SELECT * FROM clients WHERE nom LIKE ?", ('%' + nom_recherche + '%',))
            data = cursor.fetchall()
            conn.close()

    # Dans tous les cas, on rend un template (ou on peut faire un simple retour)
    return render_template('fiche_nom.html', data=data)

#--------------------------------------------
# Formulaire et insertion de client
#--------------------------------------------
@app.route('/enregistrer_client', methods=['GET'])
def formulaire_client():
    return render_template('formulaire.html')  # afficher le formulaire

@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    nom = request.form['nom']
    prenom = request.form['prenom']

    # Connexion à la base de données
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Exécution de la requête SQL pour insérer un nouveau client
    cursor.execute(
        'INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)',
        (1002938, nom, prenom, "ICI")
    )
    conn.commit()
    conn.close()

    # Rediriger vers la page consultation après l'enregistrement
    return redirect('/consultation/')

if __name__ == "__main__":
    app.run(debug=True)
