"""
Various utility functions.
"""

from django.conf import settings
import boto


def get_boto_ses_connection():
    """
    Shortcut for instantiating and returning a boto SESConnection object.

    :rtype: boto.ses.SESConnection
    :returns: A boto SESConnection object, from which email sending is done.
    """

    access_key_id = getattr(settings, 'CUCUMBER_SES_ACCESS_KEY_ID',
                            getattr(settings, 'AWS_ACCESS_KEY_ID', None))
    access_key = getattr(settings, 'CUCUMBER_SES_SECRET_ACCESS_KEY',
                         getattr(settings, 'AWS_SECRET_ACCESS_KEY', None))

    return boto.connect_ses(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=access_key,
    )


def dkim_sign(message):
    """
    :returns: A signed email message if dkim package and settings are available.
    """

    try:
        import dkim
    except ImportError:
        return message

    dkim_domain = getattr(settings, "DKIM_DOMAIN", None)
    dkim_key = getattr(settings, 'DKIM_PRIVATE_KEY', None)
    dkim_selector = getattr(settings, 'DKIM_SELECTOR', 'ses')
    dkim_headers = getattr(settings, 'DKIM_HEADERS', ('From', 'To', 'Cc', 'Subject'))

    if dkim_domain and dkim_key:
        sig = dkim.sign(message,
                        dkim_selector,
                        dkim_domain,
                        dkim_key,
                        include_headers=dkim_headers)
        message = sig + message
    return message
