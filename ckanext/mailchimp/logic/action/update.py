from ckan.common import config
from ckan.logic.action.update import user_update
import ckan.plugins.toolkit as tk

from ckanext.mailchimp.logic.mailchimp import mailchimp_client

def mailchimp_user_update(context, data_dict):
    '''
    This function is called whenever an user_update action is triggered.
    This is not only happening in the update user form but e.g. also in promote user to sysadmin.
    This is why we added the 'is-edit-user' to make sure to only update the newsletter preferences there.
    Otherwise we might remove a user from the mailing list by accident because the newsletter attribute is only 
    added to the data_dict when submitting via that form.
    '''
    previous_user_data = tk.get_action('user_show')(context, {'id': data_dict['id']})
    previous_email = previous_user_data.get('email')
    previous_name = previous_user_data.get('fullname', previous_user_data.get('name'))
    user = user_update(context, data_dict)
    # Make sure to only update mailchimp settings when changes are made
    # Via the form
    if not data_dict.get('should-update-newsletter'):
        return user

    client = mailchimp_client()
    
    if data_dict:
        user_email = data_dict.get('email')
        name = data_dict.get('fullname', data_dict.get('name'))
        if previous_email != user_email:
            # User changed email. Remove old email from the subscription list
            client.delete_subscriber_by_email(previous_email)
        elif previous_name != name:
            client.update_subscriber_name(user_email, name)

        if data_dict.get('newsletter') == 'subscribed':
            # if user is not already a subscriber, add them
            if user_email and not client.is_active_subscriber(user_email):
                client.create_new_subscriber(
                    name, user_email, tags=["NAP-user"]
                )
        else:
            client.delete_subscriber_by_email(user_email)

    return user
