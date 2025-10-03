from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

    @app.route("/")
    def catalog():
        return render_template("shop/index.html")

    return app
