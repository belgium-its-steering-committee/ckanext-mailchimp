
from ckanext.mailchimp.logic.mailchimp import mailchimp_client

def mailchimp_is_user_subscribed(user_email):
  client = mailchimp_client()
  return client.is_active_subscriber(user_email)

def mailchimp_is_user_pending(user_email):
  client = mailchimp_client()
  return client.is_pending_subscriber(user_email)