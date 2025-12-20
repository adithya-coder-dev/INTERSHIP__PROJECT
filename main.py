from flask import Flask, render_template
from controller.database import db
from controller.config import config 
from controller.models import *   

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)    

with app.app_context():
    db.create_all()

@app.route("/")
def hello_world():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()