from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Fonctions d'authentification
def est_authentifie_admin():
    return session.get('authentifie_admin')

def est_authentifie_user():
    return session.get('authentifie_user')

@app.route('/')
def accueil():
    return render_template('accueil.html')

# Authentification Admin
@app.route('/authentification_admin', methods=['GET', 'POST'])
def authentification_admin():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['authentifie_admin'] = True
            return redirect(url_for('gestion_bibliotheque'))
        return render_template('formulaire_authentification.html', error=True)
    return render_template('formulaire_authentification.html', error=False)

# Authentification Utilisateur
@app.route('/authentification_user', methods=['GET', 'POST'])
def authentification_user():
    if request.method == 'POST':
        if request.form['username'] == 'user' and request.form['password'] == '12345':
            session['authentifie_user'] = True
            return redirect(url_for('recherche_livre'))
        return render_template('formulaire_authentification.html', error=True)
    return render_template('formulaire_authentification.html', error=False)

# Gestion des livres
@app.route('/ajouter_livre', methods=['POST'])
def ajouter_livre():
    if not est_authentifie_admin():
        return redirect(url_for('authentification_admin'))

    titre = request.form['titre']
    auteur = request.form['auteur']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO livres (titre, auteur, disponible) VALUES (?, ?, ?)', (titre, auteur, True))
    conn.commit()
    conn.close()

    return redirect(url_for('gestion_bibliotheque'))

@app.route('/supprimer_livre/<int:livre_id>', methods=['POST'])
def supprimer_livre(livre_id):
    if not est_authentifie_admin():
        return redirect(url_for('authentification_admin'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM livres WHERE id = ?', (livre_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('gestion_bibliotheque'))

@app.route('/recherche_livre/', methods=['GET', 'POST'])
def recherche_livre():
    if not est_authentifie_user():
        return redirect(url_for('authentification_user'))

    if request.method == 'POST':
        titre_recherche = request.form['titre']
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM livres WHERE titre = ? AND disponible = 1', (titre_recherche,))
        data = cursor.fetchall()
        conn.close()
        return render_template('resultats_recherche.html', data=data)

    return render_template('recherche_livre.html')

@app.route('/emprunt_livre/<int:livre_id>', methods=['POST'])
def emprunt_livre(livre_id):
    if not est_authentifie_user():
        return redirect(url_for('authentification_user'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE livres SET disponible = 0 WHERE id = ?', (livre_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('recherche_livre'))

@app.route('/gestion_bibliotheque')
def gestion_bibliotheque():
    if not est_authentifie_admin():
        return redirect(url_for('authentification_admin'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM livres;')
    data = cursor.fetchall()
    conn.close()

    return render_template('gestion_bibliotheque.html', data=data)

if __name__ == "__main__":
    app.run(debug=True)
