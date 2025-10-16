from ckan.logic.action.create import user_create

from ckanext.mailchimp.logic.mailchimp import mailchimp_client as get_mailchimp_client
from ckanext.mailchimp.util import name_splitter


def mailchimp_user_create(context, data_dict):
    user = user_create(context, data_dict)

    if user and (data_dict or {}).get('newsletter') == 'subscribed':
        name = data_dict.get('fullname', data_dict.get('name'))
        mailchimp_add_subscriber(name, data_dict.get('email'), tags=["NAP-user"])
    return user


def mailchimp_add_subscriber(name, email, tags=None):
    """
    if user is not already in mailchimp add user to mailchimp

    :param name: full name of the subscriber
    :param email: email of the subscriber
    :param tags: array of tags for the subscriber -> https://mailchimp.com/help/manage-tags/
    :return: True if successful, False if not
    """
    mailchimp_client = get_mailchimp_client()
    if not mailchimp_client.is_active_subscriber(email):
        success, message = mailchimp_client.create_new_subscriber(
            name,
            email,
            tags
        )
        return success, message
    else:
        subscriber = mailchimp_client.find_subscriber_by_email(email)
        subscriber_tags = [tag.get('name', '') for tag in subscriber.get('tags', [])]
        merged_tags = subscriber_tags + tags if tags else subscriber_tags
        success = mailchimp_client.update_subscriber_tags(subscriber.get('id'), merged_tags)
        if success:
            return False, "ALREADY_SUBSCRIBED"
        else:
            return False, "ERROR_UPDATE"
