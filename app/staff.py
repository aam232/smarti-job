from flask import Blueprint, flash, redirect, render_template, url_for

from . import db
from .forms import StaffForm
from .models import Staff

bp = Blueprint("staff", __name__, url_prefix="/staff")


@bp.route("/")
def index():
    query = db.select(Staff).order_by(Staff.last_name, Staff.first_name)
    staff_members = db.session.scalars(query).all()
    return render_template("staff/list.html", staff_members=staff_members)


@bp.route("/new", methods=["GET", "POST"])
def new():
    form = StaffForm()
    if form.validate_on_submit():
        staff_member = Staff()
        form.populate_obj(staff_member)
        db.session.add(staff_member)
        db.session.commit()
        flash("Staff member added.", "success")
        return redirect(url_for("staff.index"))
    return render_template(
        "staff/form.html", form=form, title="Add staff member",
        cancel_url=url_for("staff.index"),
    )
