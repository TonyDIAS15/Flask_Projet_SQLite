from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
from flask import json
from urllib.request import urlopen
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Vérifie l'authentification administrateur
def est_authentifie():
    return session.get('authentifie')

# Vérifie l'authentification utilisateur
def est_authentifie_user():
    return session.get('user_authentifie')

@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        # Rediriger vers la page d'authentification admin si non authentifié
        return redirect(url_for('authentification'))
    return "<h2>Bravo, vous êtes authentifié</h2>"

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        # Authentification administrateur
        if request.form['username'] == 'admin' and request.form['password'] == 'password': 
            session['authentifie'] = True
            return redirect(url_for('lecture'))
        else:
            return render_template('formulaire_authentification.html', error=True)
    return render_template('formulaire_authentification.html', error=False)

# Nouvelle route d'authentification pour les utilisateurs (login: user / password: 12345)
@app.route('/authentification_user', methods=['GET', 'POST'])
def authentification_user():
    if request.method == 'POST':
        if request.form['username'] == 'user' and request.form['password'] == '12345':
            session['user_authentifie'] = True
            return redirect(url_for('fiche_nom'))
        else:
            return render_template('formulaire_authentification_user.html', error=True)
    return render_template('formulaire_authentification_user.html', error=False)

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/consultation/')
def ReadBDD():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients;')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/enregistrer_client', methods=['GET'])
def formulaire_client():
    return render_template('formulaire.html')  # afficher le formulaire

@app.route('/enregistrer_client', methods=['POST'])
def enregistrer_client():
    nom = request.form['nom']
    prenom = request.form['prenom']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO clients (created, nom, prenom, adresse) VALUES (?, ?, ?, ?)', (1002938, nom, prenom, "ICI"))
    conn.commit()
    conn.close()
    return redirect('/consultation/')

# Nouvelle route pour la recherche par nom
@app.route('/fiche_nom/', methods=['GET', 'POST'])
def fiche_nom():
    # Protection : vérifier que l'utilisateur est authentifié (login user/12345)
    if not est_authentifie_user():
        return redirect(url_for('authentification_user'))
    
    if request.method == 'POST':
        nom = request.form.get('nom')
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE nom = ?", (nom,))
        data = cursor.fetchall()
        conn.close()
        return render_template('read_data.html', data=data)
    
    # Affichage du formulaire de recherche
    return render_template('formulaire_fiche_nom.html')

if __name__ == "__main__":
    app.run(debug=True)
