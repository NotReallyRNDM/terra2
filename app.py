from flask import Flask, render_template, request, redirect, url_for, flash
from database import init_db, get_db
import secrets
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import(
    generate_password_hash, check_password_hash
)
 
app = Flask(__name__)
#temp
app.config["SECRET_KEY"] = "ahh?" 

init_db()

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash


@login_manager.user_loader
def load_user(user_id):
    with get_db() as db:
        user = db.execute(
             "SELECT * FROM users WHERE id = ?",
             (user_id,)
        ).fetchone()

    if user is None:
        return None

    return User(
        user["id"],
        user["username"],
        user["password_hash"],
    )

@app.route("/register", methods = ["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if len(username) < 1:
            flash("username need be longer")
            return redirect(url_for("register"))

        if len(password) < 2:
            flash("password need be longer")
            return redirect(url_for("register"))


        password_hash = generate_password_hash(password)

        try:
            with get_db() as db:
                db.execute(
                    """
                    INSERT INTO users (username, password_hash)
                    VALUES (?, ?)
                    """,
                    (username, password_hash)
                )            

        except Exception as error:
            import sqlite3
            if isinstance(error, sqlite3.IntegrityError):
                flash("Account already exists")
                return redirect(url_for("register"))
            raise

        flash("account made, me~ now try login")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with get_db() as db:
            user = db.execute(
                "SELECT * FROM users WHERE username = ? COLLATE NOCASE",
                (username,)
            ).fetchone()

        if user and check_password_hash(
            user["password_hash"], password
        ):

            login_user(User(
                user["id"],
                user["username"],
                user["password_hash"]
            ))
            return redirect(url_for("index"))

        flash("Username or password is not valid try again~")

    return render_template("login.html")

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/")
def index():
    return render_template("index.html")



@app.route("/create", methods=["GET", "POST"])
@login_required 
def create_poll():
    if request.method == "POST":
        question = request.form.get("question", "").strip()

        options = [
            option.strip()
            for option in request.form.getlist("options")
            if option.strip()
        ]        

        if not question or len(options) < 2:
            return "Enter a quesstion and three options", 400

        public_id = secrets.token_urlsafe(16)

        with get_db() as db:
            cursor = db.execute(
                """
                INSERT INTO polls (public_id, creator_id, question)
                VALUES (?, ?, ?)
                """,
                (public_id, current_user.id, question)
            )

            poll_id = cursor.lastrowid

            for option in options:
                db.execute(
                    """
                    INSERT INTO options (poll_id, option_text)
                    VALUES (?, ?)
                    """,
                    (poll_id, option)
                )

        return redirect(url_for("view_poll", public_id=public_id))
    return render_template("create_poll.html")

@app.route("/poll/<public_id>")

def view_poll(public_id):
    with get_db() as db:
        poll = db.execute(
            "SELECT * FROM polls WHERE public_id = ?",
            (public_id,)

        ).fetchone()

        if poll is None:
            return "poll not found try again", 404

        options = db.execute(
            "SELECT * FROM options WHERE poll_id = ?",
            (poll["id"],)
        ).fetchall()

    return render_template("poll.html", poll=poll,options=options)   

            



if __name__ == "__main__":
    app.run(debug=True)


    




