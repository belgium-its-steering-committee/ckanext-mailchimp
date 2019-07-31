from ckan.common import config
from ckan.logic.action.update import user_update

from ckanext.mailchimp.logic.mailchimp import MailChimpClient


def mailchimp_user_update(context, data_dict):
    user = user_update(context, data_dict)
    mailchimp_client = MailChimpClient(
        api_key=config.get('ckan.mailchimp.api_key', None),
        base_url=config.get('ckan.mailchimp.base_url', None),
        member_list_id=config.get('ckan.mailchimp.member_list_id', None)
    )

    if user is not None and data_dict is not None:
        if data_dict.get('newsletter', None) == 'subscribed':
            # if user is not already in mailchimp add user to mailchimp
            if mailchimp_client.find_subscriber_by_email(data_dict.get('email', None)) is None:
                mailchimp_client.create_new_subscriber(data_dict.get('name', None), data_dict.get('email', None))
        elif data_dict.get('newsletter', None) is None or data_dict.get('newsletter', None) == '':
            # if user is already in mailchimp remove user from mailchimp
            if mailchimp_client.find_subscriber_by_email(data_dict.get('email', None)) is not None:
                mailchimp_client.delete_subscriber_by_email(data_dict.get('email', None))

    return user
