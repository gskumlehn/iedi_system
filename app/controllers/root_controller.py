from flask import Blueprint, render_template

root_bp = Blueprint("root", __name__)

@root_bp.route("/")
def index():
    """Listagem de análises"""
    return render_template("index.html")


@root_bp.route("/detail")
def detail():
    """Detalhamento de análise"""
    return render_template("detail.html")


@root_bp.route("/create")
def create():
    """Criação de nova análise"""
    return render_template("create.html")
