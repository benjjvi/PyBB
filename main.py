from flask import Flask, render_template
import BulletinDatabaseModule

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("base.html", title="default Jinja and Flask")

@app.route("/results")
def results():
    return render_template("base.html", title="test")

if __name__ == "__main__":
    app.run(debug=True)