from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
#import hashlib
from argon2 import PasswordHasher
import os

app = Flask(__name__)
app.secret_key = os.environ.get("MY_SUPER_SECRET_HERE")  # FAILLE FIXED : clé secrète en dur et faible

DATABASE = "hackboard.db"

# ---------------------------------------------------------------------------
# BDD
# ---------------------------------------------------------------------------


def get_db():
    connexionDB = sqlite3.connect(DATABASE)
    connexionDB.row_factory = sqlite3.Row
    return connexionDB


def init_db():
    connexionDB = get_db()
    with open("schema.sql") as f:
        connexionDB.executescript(f.read())
    connexionDB.commit()
    connexionDB.close()


# ---------------------------------------------------------------------------
# ACCUEIL
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    connexionDB = get_db()
    # FAILLE : pas de limite, tous les write-ups chargés en mémoire
    writeups = connexionDB.execute(
        "SELECT w.*, u.username FROM writeups w JOIN users u ON w.user_id = u.id ORDER BY w.created_at DESC"
    ).fetchall()
    connexionDB.close()
    return render_template("index.html", writeups=writeups)


# ---------------------------------------------------------------------------
# INSCRIPTION
# ---------------------------------------------------------------------------


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        # FAILLE : MD5 sans salt
        # hashed = hashlib.md5(password.encode()).hexdigest()
        hashed = PasswordHasher(password)

        connexionDB = get_db()
        try:
            connexionDB.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, hashed, email),
            )
            connexionDB.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            error = "Ce nom d'utilisateur existe déjà."
        finally:
            connexionDB.close()

    return render_template("register.html", error=error)


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # FAILLE : MD5 sans salt pour comparer
        # hashed = hashlib.md5(password.encode()).hexdigest()
        hashed = PasswordHasher(password)

        connexionDB = get_db()
        # FAILLE : injection SQL, concaténation directe sur username
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashed}'"
        user = connexionDB.execute(query).fetchone()
        connexionDB.close()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
        else:
            error = "Identifiants incorrects."

    return render_template("login.html", error=error)


# ---------------------------------------------------------------------------
# Déconnexion
# ---------------------------------------------------------------------------


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# PROFIL
# ---------------------------------------------------------------------------


@app.route("/profile/<int:user_id>")
def profile(user_id):
    # FAILLE : IDOR, n'importe qui peut voir n'importe quel profil
    # sans vérifier si c'est bien l'utilisateur connexionDBecté
    connexionDB = get_db()
    user = connexionDB.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    writeups = connexionDB.execute(
        "SELECT * FROM writeups WHERE user_id = ?", (user_id,)
    ).fetchall()
    connexionDB.close()
    if not user:
        return "Utilisateur introuvable", 404
    return render_template("profile.html", user=user, writeups=writeups)


# ---------------------------------------------------------------------------
# NOUVEAU WRITE-UP
# ---------------------------------------------------------------------------


@app.route("/writeup/new", methods=["GET", "POST"])
def new_writeup():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        tags = request.form["tags"]

        connexionDB = get_db()
        connexionDB.execute(
            "INSERT INTO writeups (user_id, title, content, tags) VALUES (?, ?, ?, ?)",
            (session["user_id"], title, content, tags),
        )
        connexionDB.commit()
        connexionDB.close()
        return redirect(url_for("index"))

    return render_template("new_writeup.html")


# ---------------------------------------------------------------------------
# DÉTAIL WRITE-UP + COMMENTAIRES
# ---------------------------------------------------------------------------


@app.route("/writeup/<int:writeup_id>", methods=["GET", "POST"])
def writeup(writeup_id):
    connexionDB = get_db()
    wp = connexionDB.execute(
        "SELECT w.*, u.username FROM writeups w JOIN users u ON w.user_id = u.id WHERE w.id = ?",
        (writeup_id,),
    ).fetchone()

    if not wp:
        connexionDB.close()
        return "Write-up introuvable", 404

    if request.method == "POST":
        if "user_id" not in session:
            return redirect(url_for("login"))
        comment = request.form["comment"]
        # FAILLE : XSS stocké, le commentaire est sauvegardé sans échappement
        # et sera affiché avec |safe dans le template
        connexionDB.execute(
            "INSERT INTO comments (writeup_id, user_id, content) VALUES (?, ?, ?)",
            (writeup_id, session["user_id"], comment),
        )
        connexionDB.commit()

    comments = connexionDB.execute(
        "SELECT c.*, u.username FROM comments c JOIN users u ON c.user_id = u.id WHERE c.writeup_id = ?",
        (writeup_id,),
    ).fetchall()
    connexionDB.close()

    return render_template("writeup.html", writeup=wp, comments=comments)


# ---------------------------------------------------------------------------
# RECHERCHE
# ---------------------------------------------------------------------------


@app.route("/search")
def search():
    query = request.args.get("q", "")
    connexionDB = get_db()
    # FAILLE : injection SQL dans la recherche
    results = connexionDB.execute(
        f"SELECT w.*, u.username FROM writeups w JOIN users u ON w.user_id = u.id WHERE w.title LIKE '%{query}%' OR w.tags LIKE '%{query}%'"
    ).fetchall()
    connexionDB.close()
    return render_template("search.html", results=results, query=query)

# ---------------------------------------------------------------------------
# RECHERCHE
# ---------------------------------------------------------------------------


@app.route("/sante")
def health():
    return "OK", 200


# ---------------------------------------------------------------------------
# LANCEMENT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not os.path.exists(DATABASE):
        init_db()
    # FAILLE FIXED : debug=True en production
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

