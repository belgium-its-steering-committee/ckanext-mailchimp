import ckan.lib.base as base
from ckan.common import request

from ckanext.mailchimp.logic.action.create import mailchimp_add_subscriber
from ckanext.mailchimp.util import name_from_email


class NewsletterController(base.BaseController):

    def subscribe(self):
        email = request.params.get('email', None)
        if email:
            names = name_from_email(email)
            success = mailchimp_add_subscriber(names[0], names[1], email)
            # TODO handle success or failure
        else:
            # TODO handle no email
            pass
