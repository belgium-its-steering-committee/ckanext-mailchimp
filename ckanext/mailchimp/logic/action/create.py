from ckan.logic.action.create import user_create


def mailchimp_user_create(context, data_dict):
    user = user_create(context, data_dict)

    if user is not None and data_dict is not None and data_dict.get('newsletter', None) == 'subscribed':
        print("-" * 35)
        print("if user is not already in mailchimp add user to mailchimp")
        print(data_dict.get('name', None))
        print(data_dict.get('email', None))
        print("-" * 35)

    return user
