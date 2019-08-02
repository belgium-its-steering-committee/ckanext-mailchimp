from ckan.common import request
from ckan.controllers.home import HomeController
from ckan.lib.helpers import flash_success, flash_error

from ckanext.mailchimp.logic.action.create import mailchimp_add_subscriber
from ckanext.mailchimp.util import name_from_email

from validate_email import validate_email


class NewsletterController(HomeController):

    def subscribe(self):
        email = request.params.get('email', None)
        if email and validate_email(email):
            names = name_from_email(email)
            success = mailchimp_add_subscriber(names[0], names[1], email)
            if success:
                flash_success("Successfully added to mailing list")
            else:
                flash_error("An error occurred while adding you to the mailing list")
        else:
            flash_error("Please provide a valid email address!")
        return super(NewsletterController, self).index()
