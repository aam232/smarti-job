from flask import Blueprint, flash, redirect, render_template, request, url_for

from . import db
from .forms import JobForm, JobStatusForm, customer_choices, staff_choices
from .models import Job, Staff
from .statuses import JOB_ALLOWED, JOB_STATUSES, OPEN_JOB_STATUSES, can_transition

bp = Blueprint("jobs", __name__, url_prefix="/jobs")


@bp.route("/")
def index():
    jobs = db.session.scalars(db.select(Job).order_by(Job.id.desc())).all()  # newest first
    return render_template("jobs/list.html", jobs=jobs)


@bp.route("/new", methods=["GET", "POST"])
def new():
    # ?customer_id=3 pre-selects that customer. On a POST the submitted value wins.
    form = JobForm(customer=request.args.get("customer_id", type=int))
    form.customer.choices = customer_choices()
    form.staff.choices = staff_choices()

    if form.validate_on_submit():
        # form.staff.data is a list of ids. Turn them into Staff objects: assigning
        # that list to job.staff makes SQLAlchemy insert the job_staff rows for us.
        # (A repeated id can't create a duplicate: the query returns each person once.)
        staff_members = db.session.scalars(
            db.select(Staff).where(Staff.id.in_(form.staff.data))
        ).all()
        job = Job(
            customer_id=form.customer.data,
            title=form.title.data,
            description=form.description.data,
            location_line1=form.location_line1.data,
            location_line2=form.location_line2.data,
            location_city=form.location_city.data,
            location_postcode=form.location_postcode.data,
            staff=staff_members,
        )  # status is not set here: the column default is "Pending"
        db.session.add(job)
        db.session.commit()
        flash("Job created.", "success")
        return redirect(url_for("jobs.detail", job_id=job.id))
    return render_template(
        "jobs/form.html", form=form, title="Create job", cancel_url=url_for("jobs.index"),
    )


@bp.route("/<int:job_id>")
def detail(job_id):
    job = db.get_or_404(Job, job_id)
    status_form = JobStatusForm()
    # The dropdown only offers the statuses this job is allowed to move to.
    allowed = JOB_ALLOWED.get(job.status, set())
    status_form.status.choices = [(s, s) for s in JOB_STATUSES if s in allowed]
    return render_template(
        "jobs/detail.html", job=job, status_form=status_form, open_statuses=OPEN_JOB_STATUSES,
    )


@bp.route("/<int:job_id>/status", methods=["POST"])
def change_status(job_id):
    job = db.get_or_404(Job, job_id)
    form = JobStatusForm()
    # The field only has to accept any real status. Whether the move is allowed
    # is decided by can_transition, not by what the dropdown showed.
    form.status.choices = [(s, s) for s in JOB_STATUSES]

    if not form.validate_on_submit():
        flash("Invalid status change request.", "error")
    elif can_transition(JOB_ALLOWED, job.status, form.status.data):
        job.status = form.status.data
        db.session.commit()
        flash(f"Job status changed to {job.status}.", "success")
    else:
        flash(f"Cannot change status from {job.status} to {form.status.data}.", "error")
    return redirect(url_for("jobs.detail", job_id=job.id))
