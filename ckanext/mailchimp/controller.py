# coding=utf-8
import ckan.plugins.toolkit as tk
from ckan.common import request
from ckan.lib.helpers import flash_success, flash_error

from ckanext.mailchimp.logic.action.create import mailchimp_add_subscriber
from ckanext.mailchimp.util import name_from_email

FLASH_MESSAGES = {
    "SUCCESS": tk._("A confirmation email was sent to you to verify your email address. Please check your spam folder if you did not receive this email. If the problem persists, contact us at <a href='mailto:contact@transportdata.be'>contact@transportdata.be</a>"),
    "ERROR_ADD": tk._("An error occurred while adding you to the mailing list."),
    "ALREADY_SUBSCRIBED": tk._("You already subscribed to the newsletter."),
    "ERROR_UPDATE": tk._("An error occurred while updating your information."),
    "ERROR_NOT_VALID": tk._("Please provide a valid email address!"),
}


def flash_message(msg_key):
    message = FLASH_MESSAGES.get(msg_key)
    if not message:
        return tk._("An error occurred")
    return message

def subscribe():
    email = request.form.get('email') or request.args.get('email')

    _, errors = tk.navl_validate(
        {"email": email },
        {"email": [tk.get_validator("email_validator")]}
    )

    if email and not errors:
        first, last = name_from_email(email)
        success, msg_key = mailchimp_add_subscriber(first, last, email, tags=["Mailinglist-user"])
        if success:
            flash_success(flash_message(msg_key), allow_html=True)
        else:
            flash_error(flash_message(msg_key), allow_html=True)
    else:
        flash_error(flash_message("ERROR_NOT_VALID"), allow_html=True)

    return tk.redirect_to(tk.url_for("home.index"))
