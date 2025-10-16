import json
import logging
import requests
from ckan.common import config
from ckanext.mailchimp.util import name_splitter

def mailchimp_client():
  client = MailChimpClient(
        api_key=config.get('ckan.mailchimp.api_key'),
        base_url=config.get('ckan.mailchimp.base_url'),
        member_list_id=config.get('ckan.mailchimp.member_list_id')
    )
  return client

class MailChimpClient(object):
    # lifecycle status is:
    # start: create with pending
    # => subscribed if accepted
    # => archived if unsubscribe
    # => back to pending if resubscribe
    STATUS_SUBSCRIBED = "subscribed"
    STATUS_PENDING = "pending"
    STATUS_ARCHIVED = "archived"
    def __init__(self, api_key, base_url, member_list_id):
        assert api_key, "An API key must be supplied"
        assert base_url, "A base URL must be supplied"
        assert member_list_id, "A member list ID must be supplied"

        self.base_url = base_url
        self.member_list_id = member_list_id
        self.headers = {"Authorization": "apikey {0}".format(api_key)}
        self.logger = logging.getLogger(__name__)
        self.sub_by_email_cache = {}

    def is_active_subscriber(self, email):
        subscriber = self.find_subscriber_by_email(email)
        return subscriber and subscriber.get("status") == self.STATUS_SUBSCRIBED
      
    def is_pending_subscriber(self, email):
        subscriber = self.find_subscriber_by_email(email)
        return subscriber and subscriber.get("status") == self.STATUS_PENDING

    def is_archived_subscriber(self, email):
        subscriber = self.find_subscriber_by_email(email)
        return subscriber and subscriber.get("status") == self.STATUS_ARCHIVED

    def find_subscriber_by_email(self, email):
        if email in self.sub_by_email_cache:
            return self.sub_by_email_cache[email]
        subscriber = self._get_subscriber_by_email(email)
        self.sub_by_email_cache[email] = subscriber
        return subscriber

    def _get_subscriber_by_email(self, email):
        response = requests.get(f"{self.base_url}/search-members?query={email}", headers=self.headers)
        response_obj = response.json()
        if response.status_code == 200:
          if len(response_obj["exact_matches"]["members"]) >= 1:
            return response_obj["exact_matches"]["members"][0]
          elif len(response_obj["full_search"]["members"]) >= 1:
            # This endpoint does not count email addresses with a '+' as a, exact match,
            # but will still show them in full_search. So check for exact matches in full_search too.
            # This might be mailchimp stripping away the '+' part, or something else.
            for member in response_obj["full_search"]["members"]:
                if member.get("email_address") == email:
                    return member

        return None

    def create_new_subscriber(self, name, email, tags=None):
        subscriber = self.find_subscriber_by_email(email)
        if subscriber and subscriber.get("status") == self.STATUS_ARCHIVED:
            # user was subscribed in the past and unsubbed, making them archived. 
            # Resubscribe via status change. This is set to "pending" instead of "subscribed" so
            # the user has to reconfirm their subscription. This avoids users using someone else's email address
            # to subscribe them without their consent.
            response = requests.patch(f"{self.base_url}/lists/{self.member_list_id}/members/{subscriber['contact_id']}",
                                 json.dumps({"status": self.STATUS_PENDING}), headers=self.headers)
        else:
          firstname, lastname = name_splitter(name)
          create_data = {
              "email_address": email,
              "status": self.STATUS_PENDING,
              "merge_fields": {
                  "FNAME": firstname,
                  "LNAME": lastname
              }
          }
          if tags and len(tags) > 0:
              create_data["tags"] = []
              for tag in tags:
                  create_data["tags"].append(tag)
          response = requests.post(f"{self.base_url}/lists/{self.member_list_id}/members",
                                  json.dumps(create_data), headers=self.headers)

        if response.status_code in [200, 201]:
            succes = True
            message = "SUCCESS"
        elif response.status_code in [400] and response.json().get("title", "") == "Member Exists":
            succes = False
            message = "ALREADY_SUBSCRIBED"
            self.logger.warning(response.json().get("detail", "Already a list member"))
        else:
            succes = False
            message = "ERROR_ADD"
            self.logger.error(response.text)
        return succes, message

    def delete_subscriber_by_email(self, email):
        subscriber = self.find_subscriber_by_email(email)
        if subscriber:
            requests.delete(
                f"{self.base_url}/lists/{self.member_list_id}/members/{subscriber['id']}",
                headers=self.headers
            )

    def update_subscriber_name(self, email, name):
        subscriber = self.find_subscriber_by_email(email)
        if subscriber:
            firstname, lastname = name_splitter(name)
            response = requests.patch(
                f"{self.base_url}/lists/{self.member_list_id}/members/{subscriber['contact_id']}",
                json.dumps({"merge_fields": {"FNAME": firstname, "LNAME": lastname}}),
                headers=self.headers
            )
            if response.status_code not in [200, 201, 204]:
                self.logger.error(response.text)
                return False
            return True
    def update_subscriber_tags(self, subscriber_id, tags):
        tag_objects = [{"name": tag, "status": "active"} for tag in tags]
        response = requests.post(
                f"{self.base_url}/lists/{self.member_list_id}/members/{subscriber_id}/tags",
                json.dumps({"tags": tag_objects}),
                headers=self.headers
            )
        if response.status_code not in [200, 201, 204]:
            self.logger.error(response.text)
            return False
        
        return True
