from flask import Blueprint, render_template

bp = Blueprint("jobs", __name__, url_prefix="/jobs")


@bp.route("/")
def index():
    # Placeholder until the job list is built
    return render_template("placeholder.html", title="Jobs")
