import logging
import celery
from celery import Task
from django.conf import settings
from boto.ses.exceptions import SESAddressBlacklistedError, SESDomainEndsWithDotError
from seacucumber.util import get_boto_ses_connection

logger = logging.getLogger(__name__)

class EmailTask(Task):
    """
    Base email task that provides a connection that email tasks can reuse.
    """
    abstract = True
    _connection = None

    def __init__(self):
        self.max_retries = getattr(settings, 'CUCUMBER_MAX_RETRIES', 60)
        self.default_retry_delay = getattr(settings, 'CUCUMBER_RETRY_DELAY', 60)
        self.rate_limit = getattr(settings, 'CUCUMBER_RATE_LIMIT', 1)

    @property
    def connection(self):
        if self._connection is None:
            self._connection = get_boto_ses_connection()
        return self._connection

@celery.task(base=EmailTask)
def send_email(from_email, recipients, message):
    """
        This does the dirty work. Connects to Amazon SES via boto and fires
        off the message.

        :param str from_email: The email address the message will show as
            originating from.
        :param list recipients: A list of email addresses to send the
            message to.
        :param str message: The body of the message.
    """
    try:
        # We use the send_raw_email func here because the Django
        # EmailMessage object we got these values from constructs all of
        # the headers and such.
        send_email.connection.send_raw_email(
            source=from_email,
            destinations=recipients,
            raw_message=message,
            )
    except SESAddressBlacklistedError, exc:
        # Blacklisted users are those which delivery failed for in the
        # last 24 hours. They'll eventually be automatically removed from
        # the blacklist, but for now, this address is marked as
        # undeliverable to.
        logger.warning(
            'Attempted to email a blacklisted user: %s' % recipients,
            exc_info=exc,
            extra={'trace': True}
        )
        return False
    except SESDomainEndsWithDotError, exc:
        # Domains ending in a dot are simply invalid.
        logger.warning(
            'Invalid recipient, ending in dot: %s' % recipients,
            exc_info=exc,
            extra={'trace': True}
        )
        return False
    except Exception, exc:
        # Something else happened that we haven't explicitly forbade
        # retry attempts for.
        #noinspection PyUnresolvedReferences
        raise send_email.retry(exc=exc)

    # We shouldn't ever block long enough to see this, but here it is
    # just in case (for debugging?).
    return True