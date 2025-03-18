from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour vérifier les sessions
def est_authentifie():
    return session.get('authentifie')

def est_utilisateur_authentifie():
    return session.get('utilisateur_authentifie')

# Page d'accueil
@app.route('/')
def hello_world():
    return render_template('hello.html')

# Authentification utilisateur/administrateur
@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['authentifie'] = True
            return redirect(url_for('gestion_livres'))
        elif request.form['username'] == 'user' and request.form['password'] == '12345':
            session['utilisateur_authentifie'] = True
            return redirect(url_for('rechercher_livre'))
        else:
            return render_template('formulaire_authentification.html', error=True)
    
    return render_template('formulaire_authentification.html', error=False)

# Enregistrement de livres
@app.route('/enregistrer_livre', methods=['GET', 'POST'])
def enregistrer_livre():
    if not est_authentifie():
        return redirect(url_for('authentification'))

    if request.method == 'POST':
        titre = request.form['titre']
        auteur = request.form['auteur']
        stock = int(request.form['stock'])

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO livres (titre, auteur, stock) VALUES (?, ?, ?)', (titre, auteur, stock))
        conn.commit()
        conn.close()
        return redirect('/gestion_livres')

    return render_template('formulaire_livre.html')

# Suppression de livres
@app.route('/supprimer_livre/<int:livre_id>', methods=['POST'])
def supprimer_livre(livre_id):
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM livres WHERE id = ?', (livre_id,))
    conn.commit()
    conn.close()
    return redirect('/gestion_livres')

# Recherche de livres disponibles
@app.route('/rechercher_livre', methods=['GET'])
def rechercher_livre():
    if not est_utilisateur_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livres WHERE stock > 0')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

# Emprunt de livres
@app.route('/emprunter_livre/<int:livre_id>', methods=['POST'])
def emprunter_livre(livre_id):
    if not est_utilisateur_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE livres SET stock = stock - 1 WHERE id = ? AND stock > 0', (livre_id,))
    conn.commit()
    conn.close()
    return redirect('/rechercher_livre')

# Gestion des utilisateurs
@app.route('/ajouter_utilisateur', methods=['GET', 'POST'])
def ajouter_utilisateur():
    if not est_authentifie():
        return redirect(url_for('authentification'))

    if request.method == 'POST':
        nom = request.form['nom']
        email = request.form['email']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO utilisateurs (nom, email) VALUES (?, ?)', (nom, email))
        conn.commit()
        conn.close()
        return redirect('/gestion_utilisateurs')

    return render_template('formulaire_utilisateur.html')

# Gestion des livres
@app.route('/gestion_livres')
def gestion_livres():
    if not est_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livres')
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

if __name__ == "__main__":
    app.run(debug=True)
