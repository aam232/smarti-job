import os

from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Created here but not tied to any app yet. create_app() connects it with
# db.init_app(). Other modules use it with `from . import db`.
db = SQLAlchemy()


def create_app(config=None):
    app = Flask(__name__)

    # The SQLite file lives in the instance folder, which must exist first.
    os.makedirs(app.instance_path, exist_ok=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key-change-me"),
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "smarti.db"),
    )
    if config:
        app.config.update(config)  # tests pass e.g. an in-memory database here

    db.init_app(app)

    # Imported inside the function because these modules do `from . import db`,
    # which would fail if they were imported before db is defined above.
    from . import appointments, customers, jobs, models, staff  # noqa: F401 (models registers the tables)
    from .commands import seed

    app.cli.add_command(seed)
    app.register_blueprint(customers.bp)
    app.register_blueprint(staff.bp)
    app.register_blueprint(jobs.bp)
    app.register_blueprint(appointments.bp)

    @app.route("/")
    def home():
        return redirect(url_for("customers.index"))

    return app
