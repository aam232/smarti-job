from flask import Blueprint, render_template

bp = Blueprint("staff", __name__, url_prefix="/staff")


@bp.route("/")
def index():
    # Placeholder until the staff list is built
    return render_template("placeholder.html", title="Staff")
