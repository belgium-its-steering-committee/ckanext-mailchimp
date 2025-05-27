# coding=utf-8
from ckan.common import request
from ckan.lib.helpers import flash_success, flash_error, lang
from validate_email import validate_email

from ckanext.mailchimp.logic.action.create import mailchimp_add_subscriber
from ckanext.mailchimp.util import name_from_email

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
        "en": "An error occurred while adding you to the mailing list.",
        "nl": "Er is een fout opgetreden bij het toevoegen aan de mailinglijst.",
        "fr": "Une erreur s'est produite lors de votre ajout à la liste de diffusion.",
        "de": "Beim Hinzufügen zur Mailingliste ist ein Fehler aufgetreten."
    },
    "ALREADY_SUBSCRIBED": {
        "en": "You already subscribed to the newsletter.",
        "nl": "U bent reeds ingeschreven op de mailinglijst.",
        "fr": "Vous êtes déjà abonné à la newsletter.",
        "de": "Sie haben den Newsletter bereits abonniert."
    },
    "ERROR_UPDATE": {
        "en": "An error occurred while updating your information.",
        "nl": "Er is een fout opgetreden tijdens het updaten van uw informatie",
        "fr": "Une erreur s'est produite lors de la mise à jour de vos informations.",
        "de": "Beim Aktualisieren Ihrer Informationen ist ein Fehler aufgetreten."
    },
    "ERROR_NOT_VALID": {
        "en": "Please provide a valid email address!",
        "nl": "Gelieve een geldig email adres op te geven!",
        "fr": "Veuillez fournir une adresse email valide!",
        "de": "Bitte geben Sie eine gültige E-Mail Adresse an!"
    }
}


def translate_flash_message(msg_key, lang):
    msg = flash_messages.get(msg_key, {})
    if lang in msg:
        msg_translated = msg.get(lang, "An error occurred")
    else:
        msg_translated = msg.get("en", "An error occurred")
    return msg_translated

def subscribe():
    email = request.form.get('email') or request.args.get('email')

    if email and validate_email(email):
        first, last = name_from_email(email)
        success, msg_key = mailchimp_add_subscriber(first, last, email, tags=["Mailinglist-user"])
        if success:
            flash_success(translate_flash_message(msg_key, lang()), allow_html=True)
        else:
            flash_error(translate_flash_message(msg_key, lang()), allow_html=True)
    else:
        flash_error(translate_flash_message("ERROR_NOT_VALID", lang()), allow_html=True)

    return redirect(url_for("home.index"))
