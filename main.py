from flask import Flask, render_template
import BulletinDatabaseModule

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("base.html", title="default Jinja and Flask")

students = [
    {"name": "Sandrine",  "score": 100},
    {"name": "Gergeley", "score": 87},
    {"name": "Frieda", "score": 92},
    {"name": "Fritz", "score": 40},
    {"name": "Sirius", "score": 75},
]

@app.route("/results")
def results():
    context = {
        "title": "Results",
        "students": students,
        "test_name": "a",
        "max_score": "b",
    }
    return render_template("results.html", **context)

if __name__ == "__main__":
    app.run(debug=True)