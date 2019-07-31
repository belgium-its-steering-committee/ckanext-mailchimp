from ckan.logic.action.create import user_create
from ckan.common import config

from ckanext.mailchimp.logic.mailchimp import MailChimpClient


def mailchimp_user_create(context, data_dict):
    print(data_dict)
    user = user_create(context, data_dict)
    mailchimp_client = MailChimpClient(
        api_key=config.get('ckan.mailchimp.api_key', None),
        base_url=config.get('ckan.mailchimp.base_url', None),
        member_list_id=config.get('ckan.mailchimp.member_list_id', None)
    )

    if user is not None and data_dict is not None and data_dict.get('newsletter', None) == 'subscribed':
        # if user is not already in mailchimp add user to mailchimp
        if mailchimp_client.find_subscriber_by_email(data_dict.get('email', None)) is None:
            mailchimp_client.create_new_subscriber(
                data_dict.get('fullname', data_dict.get('name', None)),
                data_dict.get('email', None)
            )

    return user
