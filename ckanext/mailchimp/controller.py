# coding=utf-8
from ckan.common import request
from ckan.controllers.home import HomeController
from ckan.lib.helpers import flash_success, flash_error, get_translated, lang

from ckanext.mailchimp.logic.action.create import mailchimp_add_subscriber
from ckanext.mailchimp.util import name_from_email

from validate_email import validate_email

flash_messages = {
    "SUCCESS": {
        "en": "A confirmation email was sent to you to verify your email address. Please check your spam folder if "
              "you did not receive this email. If the problem persists, contact us at <a "
              "href='mailto:contact@transportdata.be'>contact@transportdata.be</a>",
        "nl": "Een bevestigingsmail werd verstuurd naar uw email adres. Controleer uw spam folder indien u deze niet "
              "ontvangen heeft. Bij verdere problemen kan u ons contacteren via <a "
              "href='mailto:contact@transportdata.be'>contact@transportdata.be</a> ",
        "fr": "Nous vous avons envoyé un mail de confirmation. Si vous ne le voyez pas, vérifiez dans vos spam s’il "
              "ne s’y trouve pas. Si le problème persiste, prenez contact avec nous via <a "
              "href='mailto:contact@transportdata.be'>contact@transportdata.be</a> ",
        "de": "Eine E-Mail wurde an Sie gesendet, um Ihre E-Mail-Adresse zu bestätigen. Bitte überprüfen Sie auch "
              "Ihren Spam-Ordner wenn Sie diese E-Mail nicht erhalten haben. Wenn das Problem weiterhin besteht, "
              "kontaktiere uns per <a href='mailto:contact@transportdata.be'>contact@transportdata.be</a>  "
    },
    "ERROR_ADD": {
        "en": "An error occurred while adding you to the mailing list."
    },
    "ALREADY_SUBSCRIBED": {
        "en", "You already subscribed to the newsletter."
    },
    "ERROR_UPDATE": {
        "en": "An error occurred while updating your information."
    }
}


def translate_flash_message(msg_key, lang):
    msg = flash_messages.get(msg_key, {})
    if lang in msg:
        msg_translated = msg.get(lang, "An error occurred")
    else:
        msg_translated = msg.get("en", "An error occurred")
    return msg_translated


class NewsletterController(HomeController):

    def subscribe(self):
        email = request.params.get('email', None)
        if email and validate_email(email):
            names = name_from_email(email)
            success, msg_key = mailchimp_add_subscriber(names[0], names[1], email, tags=["Mailinglist-user"])
            if success:
                flash_success(translate_flash_message(msg_key, lang()))
            else:
                flash_error(translate_flash_message(msg_key, lang()))
        else:
            flash_error("Please provide a valid email address!")
        return super(NewsletterController, self).index()
