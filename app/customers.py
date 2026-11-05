from flask import Blueprint, render_template

bp = Blueprint("customers", __name__, url_prefix="/customers")


@bp.route("/")
def index():
    # Placeholder until the customer list is built
    return render_template("placeholder.html", title="Customers")
