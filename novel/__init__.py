from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

from config import config_map

db = SQLAlchemy()
bootstrap = Bootstrap()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_map.get(config_name))
    db.init_app(app)
    bootstrap.init_app(app)

    from novel.main.view import main as main_blueprint
    app.register_blueprint(main_blueprint)


    return app
