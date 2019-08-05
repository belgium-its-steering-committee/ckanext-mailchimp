import json
import logging
import requests


class MailChimpClient(object):

    def __init__(self, api_key, base_url, member_list_id):
        self.base_url = base_url
        self.member_list_id = member_list_id
        self.headers = {"Authorization": "apikey {0}".format(api_key)}
        self.logger=logging.getLogger(__name__)

    def find_subscriber_by_email(self, email):
        response = requests.get("{0}/search-members?query={1}".format(self.base_url, email), headers=self.headers)
        response_obj = response.json()
        if response.status_code == 200 and len(response_obj["exact_matches"]["members"]) >= 1:
            return response_obj["exact_matches"]["members"][0]
        else:
            return None

    def create_new_subscriber(self, firstname, lastname, email):
        create_data = {"email_address": email,
                       "status": "subscribed", "merge_fields": {
                            "FNAME": firstname,
                            "LNAME": lastname
                        }}
        response = requests.post("{0}/lists/{1}/members".format(self.base_url, self.member_list_id),
                                 json.dumps(create_data), headers=self.headers)
        if response.status_code not in [200, 201]:
            self.logger.error(response.text)
        return True if response.status_code in [200, 201] else False

    def delete_subscriber_by_email(self, email):
        subscriber = self.find_subscriber_by_email(email)
        if subscriber:
            requests.delete(
                "{0}/lists/{1}/members/{2}".format(self.base_url, self.member_list_id, subscriber["id"]),
                headers=self.headers
            )
