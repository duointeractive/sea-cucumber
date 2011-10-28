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
    access_key_id = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
    access_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)

    return boto.connect_ses(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=access_key,
    )
