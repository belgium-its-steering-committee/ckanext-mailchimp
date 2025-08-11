import json
import logging
import requests


class MailChimpClient(object):

    def __init__(self, api_key, base_url, member_list_id):
        assert api_key, "An API key must be supplied"
        assert base_url, "A base URL must be supplied"
        assert member_list_id, "A member list ID must be supplied"

        self.base_url = base_url
        self.member_list_id = member_list_id
        self.headers = {"Authorization": "apikey {0}".format(api_key)}
        self.logger = logging.getLogger(__name__)

    def find_subscriber_by_email(self, email):
        response = requests.get(f"{self.base_url}/search-members?query={email}", headers=self.headers)
        response_obj = response.json()
        if response.status_code == 200 and len(response_obj["exact_matches"]["members"]) >= 1:
            return response_obj["exact_matches"]["members"][0]

    def create_new_subscriber(self, firstname, lastname, email, tags=None):
        create_data = {
            "email_address": email,
            "status": "pending",
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
            self.logger.warn(response.json().get("detail", "Already a list member"))
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
