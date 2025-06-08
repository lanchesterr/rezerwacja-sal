from flask import Blueprint

main = Blueprint('main', __name__)

from . import routes  # <-- bez tego widoki nie będą zarejestrowane