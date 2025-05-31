import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultTranslation

from ckanext.mailchimp.logic.action.create import mailchimp_user_create
from ckanext.mailchimp.logic.action.update import mailchimp_user_update

from flask import Blueprint
from ckanext.mailchimp import controller 

def get_blueprint():
    bp = Blueprint('mailchimp', __name__)

    @bp.route('/newsletter/subscribe', methods=['GET', 'POST'])
    def subscribe():
        return controller.subscribe()

    return bp


# TODO: Add IConfigDeclaration implementation for the 3 config options
class MailchimpPlugin(plugins.SingletonPlugin,  DefaultTranslation):
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IConfigurer, inherit=True)
    plugins.implements(plugins.IActions, inherit=True)
    plugins.implements(plugins.IBlueprint)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')

    # IActions
    def get_actions(self):
        return {
            'user_create': mailchimp_user_create,
            'user_update': mailchimp_user_update
        }

    # IBlueprint
    def get_blueprint(self):
        return get_blueprint()
