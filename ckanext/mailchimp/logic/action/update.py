from ckan.common import config
from ckan.logic.action.update import user_update

from ckanext.mailchimp.logic.mailchimp import MailChimpClient
from ckanext.mailchimp.util import name_splitter


def mailchimp_user_update(context, data_dict):
    '''
    This function is called whenever an user_update action is triggered.
    This is not only happening in the update user form but e.g. also in promote user to sysadmin.
    This is why we added the 'is-edit-user' to make sure to only update the newsletter preferences there.
    Otherwise we might remove a user from the mailing list by accident because the newsletter attribute is only 
    added to the data_dict when submitting via that form.

    TODO: To fix this issue, we should store the newsletter subscribed state in the
    database, so we need to add this property to the user model.
    '''
    user = user_update(context, data_dict)
    # Make sure to only update mailchimp settings when changes are made
    # Via the form
    if not data_dict.get('should-update-newsletter'):
        return user

    client = MailChimpClient(
        api_key=config.get('ckan.mailchimp.api_key'),
        base_url=config.get('ckan.mailchimp.base_url'),
        member_list_id=config.get('ckan.mailchimp.member_list_id')
    )

    if data_dict:
        user_email = data_dict.get('email')
        if data_dict.get('newsletter') == 'subscribed':
            # if user is not already in mailchimp add user to mailchimp
            if user_email and not client.find_subscriber_by_email(user_email):
                first, last = name_splitter(
                    data_dict.get('fullname', data_dict.get('name'))
                )
                client.create_new_subscriber(
                    first, last, user_email, tags=["NAP-user"]
                )
        else:
            # if user is already in mailchimp remove user from mailchimp
            if client.find_subscriber_by_email(user_email):
                client.delete_subscriber_by_email(user_email)

    return user
