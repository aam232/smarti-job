from flask import Blueprint, flash, redirect, render_template, url_for

from . import db
from .forms import CustomerForm, OnboardingStatusForm
from .models import Customer
from .statuses import ONBOARDING_ALLOWED, ONBOARDING_STATUSES, can_transition

bp = Blueprint("customers", __name__, url_prefix="/customers")


@bp.route("/")
def index():
    query = db.select(Customer).order_by(Customer.last_name, Customer.first_name)
    customers = db.session.scalars(query).all()
    return render_template("customers/list.html", customers=customers)


@bp.route("/new", methods=["GET", "POST"])
def new():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer()  # onboarding_status falls back to the column default, "New Enquiry"
        form.populate_obj(customer)
        db.session.add(customer)
        db.session.commit()
        flash("Customer added.", "success")
        return redirect(url_for("customers.detail", customer_id=customer.id))
    return render_template(
        "customers/form.html", form=form, title="Add customer",
        cancel_url=url_for("customers.index"),
    )


@bp.route("/<int:customer_id>")
def detail(customer_id):
    customer = db.get_or_404(Customer, customer_id)
    status_form = OnboardingStatusForm()
    # The dropdown only offers the statuses this customer is allowed to move to.
    allowed = ONBOARDING_ALLOWED.get(customer.onboarding_status, set())
    status_form.status.choices = [(s, s) for s in ONBOARDING_STATUSES if s in allowed]
    return render_template("customers/detail.html", customer=customer, status_form=status_form)


@bp.route("/<int:customer_id>/edit", methods=["GET", "POST"])
def edit(customer_id):
    customer = db.get_or_404(Customer, customer_id)
    form = CustomerForm(obj=customer)  # pre-fills the form on GET
    if form.validate_on_submit():
        form.populate_obj(customer)  # copies the form values onto the customer
        db.session.commit()
        flash("Customer updated.", "success")
        return redirect(url_for("customers.detail", customer_id=customer.id))
    return render_template(
        "customers/form.html", form=form, title="Edit customer",
        cancel_url=url_for("customers.detail", customer_id=customer.id),
    )


@bp.route("/<int:customer_id>/status", methods=["POST"])
def change_status(customer_id):
    customer = db.get_or_404(Customer, customer_id)
    form = OnboardingStatusForm()
    # Here the field only has to accept any real status. Whether the move is
    # allowed is decided by can_transition, not by what the dropdown showed.
    form.status.choices = [(s, s) for s in ONBOARDING_STATUSES]

    if not form.validate_on_submit():
        flash("Invalid status change request.", "error")
    elif can_transition(ONBOARDING_ALLOWED, customer.onboarding_status, form.status.data):
        customer.onboarding_status = form.status.data
        db.session.commit()
        flash(f"Status changed to {customer.onboarding_status}.", "success")
    else:
        flash(
            f"Cannot change status from {customer.onboarding_status} to {form.status.data}.",
            "error",
        )
    return redirect(url_for("customers.detail", customer_id=customer.id))
