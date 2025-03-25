from flask import Flask, render_template_string, render_template, jsonify, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour vérifier l'authentification
def est_authentifie():
    return session.get('authentifie')

def est_utilisateur_authentifie():
    return session.get('utilisateur_authentifie')

@app.route('/')
def hello_world():
    return render_template('hello.html')

@app.route('/lecture')
def lecture():
    if not est_authentifie():
        return redirect(url_for('authentification'))
    return "<h2>Bravo, vous êtes authentifié</h2>"

@app.route('/authentification', methods=['GET', 'POST'])
def authentification():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['authentifie'] = True
            return redirect(url_for('lecture'))
        elif request.form['username'] == 'user' and request.form['password'] == '12345':
            session['utilisateur_authentifie'] = True
            return redirect(url_for('hello_world'))
        else:
            return render_template('formulaire_authentification.html', error=True)

    return render_template('formulaire_authentification.html', error=False)

@app.route('/fiche_client/<int:post_id>')
def Readfiche(post_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE id = ?', (post_id,))
    data = cursor.fetchall()
    conn.close()
    return render_template('read_data.html', data=data)

@app.route('/fiche_nom/<nom>')
def search_by_name(nom):
    if not est_utilisateur_authentifie():
        return redirect(url_for('authentification'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clients WHERE UPPER(nom) = UPPER(?)', (nom,))
    data = cursor.fetchall()
    conn.close()
    if data:
        return render_template('read_data.html', data=data)
    else:
        return "<h2>Aucun client trouvé avec ce nom.</h2>"

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
    return render_template('formulaire.html')

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

# Nouvelles routes pour la gestion de bibliothèque
@app.route('/livres', methods=['GET'])
def afficher_livres():
    try:
        conn = sqlite3.connect('database2.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Livres WHERE Quantite > 0;')
        livres = cursor.fetchall()
        conn.close()

        # Vérification si des livres sont trouvés
        if livres:
            return render_template('livres.html', livres=livres)
        else:
            return render_template('livres.html', message="Aucun livre disponible.")

    except Exception as e:
        return jsonify({"error": f"Erreur lors de la récupération des livres : {str(e)}"}), 500


@app.route('/livres/ajouter', methods=['GET'])
def page_ajouter_livre():
    return render_template('ajouter_livre.html')

@app.route('/livres/ajouter', methods=['POST'])
def ajouter_livre():
    try:
        data = request.form
        conn = sqlite3.connect('database2.db')
        cursor = conn.cursor()

        cursor.execute('INSERT INTO Livres (ID_livre, Titre, Auteur, Annee_publication, Quantite) VALUES (?, ?, ?, ?, ?)',
                       (data['ID_livre'], data['Titre'], data['Auteur'], data['Annee_publication'], data['Quantite']))

        conn.commit()
        conn.close()
        return redirect('/livres')
    
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/livres/supprimer/<int:id_livre>', methods=['POST'])
def supprimer_livre(id_livre):
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Livres WHERE ID_livre = ?', (id_livre,))
    conn.commit()
    conn.close()
    return redirect('/livres')

if __name__ == "__main__":
    app.run(debug=True)
