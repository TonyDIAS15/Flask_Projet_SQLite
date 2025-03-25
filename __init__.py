from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'  # Clé secrète pour les sessions

# Fonction pour vérifier l'authentification
def est_authentifie():
    return session.get('authentifie')

def est_utilisateur_authentifie():
    return session.get('utilisateur_authentifie')

# Page d'accueil
@app.route('/')
def hello_world():
    return render_template('hello.html')

# Route pour afficher tous les livres disponibles
@app.route('/livres', methods=['GET'])
def afficher_livres():
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Livres WHERE Quantite > 0;')
    livres = cursor.fetchall()
    conn.close()
    return jsonify(livres)

# Route pour ajouter un livre
@app.route('/livres/ajouter', methods=['POST'])
def ajouter_livre():
    data = request.get_json()
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Livres (ID_livre, Titre, Auteur, Annee_publication, Quantite) VALUES (?, ?, ?, ?, ?)',
                   (data['ID_livre'], data['Titre'], data['Auteur'], data['Annee_publication'], data['Quantite']))
    conn.commit()
    conn.close()
    return jsonify({"message": "Livre ajouté avec succès."})

# Route pour supprimer un livre
@app.route('/livres/supprimer/<int:id_livre>', methods=['DELETE'])
def supprimer_livre(id_livre):
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Livres WHERE ID_livre = ?', (id_livre,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Livre supprimé avec succès."})

# Route pour enregistrer un emprunt
@app.route('/emprunts/ajouter', methods=['POST'])
def ajouter_emprunt():
    data = request.get_json()
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()

    # Vérification de la disponibilité du livre
    cursor.execute('SELECT Quantite FROM Livres WHERE ID_livre = ?', (data['ID_livre'],))
    livre = cursor.fetchone()

    if livre and livre[0] > 0:
        cursor.execute('INSERT INTO Emprunts (ID_emprunt, ID_utilisateur, ID_livre, Date_emprunt, Date_retour_prevue) VALUES (?, ?, ?, ?, ?)',
                       (data['ID_emprunt'], data['ID_utilisateur'], data['ID_livre'], data['Date_emprunt'], data['Date_retour_prevue']))
        cursor.execute('UPDATE Livres SET Quantite = Quantite - 1 WHERE ID_livre = ?', (data['ID_livre'],))
        conn.commit()
        conn.close()
        return jsonify({"message": "Emprunt enregistré avec succès."})
    else:
        conn.close()
        return jsonify({"error": "Le livre demandé n'est pas disponible."}), 400

# Route pour enregistrer le retour d'un livre
@app.route('/emprunts/retour/<int:id_livre>', methods=['POST'])
def retour_livre(id_livre):
    conn = sqlite3.connect('database2.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE Livres SET Quantite = Quantite + 1 WHERE ID_livre = ?', (id_livre,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Retour du livre enregistré avec succès."})

if __name__ == "__main__":
    app.run(debug=True)
