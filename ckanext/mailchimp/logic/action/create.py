from ckan.logic.action.create import user_create

from ckanext.mailchimp.logic.mailchimp import mailchimp_client as get_mailchimp_client

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
    client = get_mailchimp_client()
    if client.is_active_subscriber(email):
       # email might be from a newsletter email, which does not have the NAP-user tag yet
      success = client.update_subscriber_tags(email, ["NAP-user"])
      if success:
          return False, "ALREADY_SUBSCRIBED"
      else:
          return False, "ERROR_UPDATE"
    else:
       return client.create_new_subscriber(name, email, tags=["NAP-user"])