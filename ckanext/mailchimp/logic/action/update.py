from ckan.logic.action.update import user_update


def mailchimp_user_update(context, data_dict):
    user = user_update(context, data_dict)

    if user is not None and data_dict is not None:
        if data_dict.get('newsletter', None) == 'subscribed':
            print("-" * 35)
            print("if user is not already in mailchimp add user to mailchimp")
            print(data_dict.get('name', None))
            print(data_dict.get('email', None))
            print("-" * 35)
        elif data_dict.get('newsletter', None) is None or data_dict.get('newsletter', None) == '':
            print("-" * 35)
            print("if user is already in mailchimp remove user from mailchimp")
            print(data_dict.get('name', None))
            print(data_dict.get('email', None))
            print("-" * 35)

    return user
