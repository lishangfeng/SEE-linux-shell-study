import flask
from flask import current_app, session, abort, request
from .cas_urls import create_cas_login_url
from .cas_urls import create_cas_logout_url
from .cas_urls import create_cas_validate_url
import bs4

import uuid
import random
import string

try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen

blueprint = flask.Blueprint('cas', __name__)


@blueprint.route('/login')
def login():
    """
    This route has two purposes. First, it is used by the user
    to login. Second, it is used by the CAS to respond with the
    `ticket` after the user logs in successfully.

    When the user accesses this url, they are redirected to the CAS
    to login. If the login was successful, the CAS will respond to this
    route with the ticket in the url. The ticket is then validated.
    If validation was successful the logged in username is saved in
    the user's session under the key `CAS_USERNAME_SESSION_KEY`.
    """

    cas_token_session_key = current_app.config['CAS_TOKEN_SESSION_KEY']

    redirect_url = create_cas_login_url(
        current_app.config['CAS_SERVER'],
        current_app.config['CAS_LOGIN_ROUTE'],
        (current_app.config['CALL_BACK'] or flask.url_for('.login', _external=True)))

    if 'ticket' in flask.request.args:
        flask.session[cas_token_session_key] = flask.request.args['ticket']
    else:
        flask.session["next"] = request.values.get("next")

    if cas_token_session_key in flask.session:
        if validate(flask.session[cas_token_session_key]):
            redirect_url = flask.session.get("next") or current_app.config.get("CAS_AFTER_LOGIN")
        else:
            del flask.session[cas_token_session_key]

    current_app.logger.debug('Redirecting to: {0}'.format(redirect_url))
    return flask.redirect(redirect_url)


@blueprint.route('/logout')
def logout():
    """
    When the user accesses this route they are logged out.
    """

    cas_username_session_key = current_app.config['CAS_USERNAME_SESSION_KEY']

    if cas_username_session_key in flask.session:
        del flask.session[cas_username_session_key]

    redirect_url = create_cas_logout_url(
        current_app.config['CAS_SERVER'],
        current_app.config['CAS_LOGOUT_ROUTE'],
        (current_app.config['CALL_BACK'] or flask.url_for('.login', _external=True)))

    current_app.logger.debug('Redirecting to: {0}'.format(redirect_url))

    return flask.redirect(redirect_url)


def validate(ticket):
    """
    Will attempt to validate the ticket. If validation fails, then False
    is returned. If validation is successful, then True is returned
    and the validated username is saved in the session under the
    key `CAS_USERNAME_SESSION_KEY`.
    """

    cas_username_session_key = current_app.config['CAS_USERNAME_SESSION_KEY']

    current_app.logger.debug("validating token {0}".format(ticket))

    cas_validate_url = create_cas_validate_url(
        current_app.config['CAS_SERVER'],
        current_app.config['CAS_VALIDATE_ROUTE'],
        (current_app.config['CALL_BACK'] or flask.url_for('.login', _external=True)),
        ticket)

    current_app.logger.debug("Making GET request to {0}".format(
        cas_validate_url))

    try:
        response = urlopen(cas_validate_url).read()
        ticketid = _parse_tag(response, "cas:user")
        strs = [s.strip() for s in ticketid.split('|') if s.strip()]
        if len(strs) == 4:
            username = strs[0]
            number = strs[2]
            name = strs[3]
            isValid = True
        else:
            isValid = False
            #(isValid, username) = urlopen(cas_validate_url).readlines()
            #isValid = True if isValid.strip() == b'yes' else False
            #username = username.strip().decode('utf8', 'ignore')
    except ValueError:
        current_app.logger.error("CAS returned unexpected result")
        isValid = False

    if isValid:
        current_app.logger.debug("valid")
        flask.session[cas_username_session_key] = username
        flask.session['CAS_NAME'] = name
        flask.session['CAS_NUMBER'] = number
    else:
        current_app.logger.debug("invalid")

    return isValid


def _parse_tag(string, tag):
    """
    Used for parsing xml.  Search string for the first occurence of
    <tag>.....</tag> and return text (stripped of leading and tailing
    whitespace) between tags.  Return "" if tag not found.
    """
    soup = bs4.BeautifulSoup(string)

    if soup.find(tag) is None:
        return ''
    return soup.find(tag).string.strip()
