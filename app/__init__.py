from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from app.controllers.root_controller import root_bp
from app.controllers.bank_controller import bank_bp
from app.controllers.media_controller import media_bp
from app.controllers.analysis_controller import analysis_bp

def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    # ProxyFix para nginx
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
    app.config["PREFERRED_URL_SCHEME"] = "https"
    app.config['JSON_AS_ASCII'] = False

    # Registrar blueprints
    app.register_blueprint(root_bp, url_prefix="/")
    app.register_blueprint(bank_bp, url_prefix="/bancos")
    app.register_blueprint(media_bp, url_prefix="/veiculos")
    app.register_blueprint(analysis_bp, url_prefix="/analises")

    return app
