"""
Supporting celery tasks go in this module. The primarily interesting one is
SendEmailTask, which handles sending a single Django EmailMessage object.
"""

import logging

from celery import Task
from django.conf import settings

from seacucumber.util import dkim_sign, get_boto_ses_client


logger = logging.getLogger(__name__)


class SendEmailTask(Task):
    """
    Sends an email through Boto's SES API module.
    """

    def __init__(self):
        self.max_retries = getattr(settings, "CUCUMBER_MAX_RETRIES", 60)
        self.default_retry_delay = getattr(settings, "CUCUMBER_RETRY_DELAY", 60)
        self.rate_limit = getattr(settings, "CUCUMBER_RATE_LIMIT", 1)

        self._client = None

    def run(self, from_email, recipients, message):
        """
        This does the dirty work. Connects to Amazon SES via boto and fires
        off the message.

        :param str from_email: The email address the message will show as
            originating from.
        :param list recipients: A list of email addresses to send the
            message to.
        :param str message: The body of the message.
        """
        client = self._get_boto_ses_client()
        try:
            # We use the send_raw_email func here because the Django
            # EmailMessage object we got these values from constructs all of
            # the headers and such.
            client.send_raw_email(
                Source=from_email,
                Destinations=recipients,
                RawMessage={"Data": dkim_sign(message)},
            )
        except client.exceptions.AccountSendingPausedException as exc:
            # Happens when the account gets disabled. We shouldn't be retrying this
            logger.warning("SES Account Paused", exc_info=exc, extra={"trace": True})
            return False
        except client.exceptions.MessageRejected as exc:
            # Message got rejected by SES.
            logger.warning(
                "Message intended for %s got rejected by AWS" % recipients,
                exc_info=exc,
                extra={"trace": True},
            )
            return False
        except client.exceptions.BaseClientException as exc:
            logger.error(
                "General SES Exception occured while trying to send to %s" % recipients,
                exc_info=exc,
                extra={"trace": True},
            )
            return False
        except Exception as exc:
            # Something else happened that we haven't explicitly forbade
            # retry attempts for.
            logger.error(
                "Something went wrong; retrying: %s" % recipients,
                exc_info=exc,
                extra={"trace": True},
            )
            self.retry(exc=exc)
        else:
            logger.info("An email has been successfully sent: %s" % recipients)

        # We shouldn't ever block long enough to see this, but here it is
        # just in case (for debugging?).
        return True

    def _get_boto_ses_client(self):
        """
        Create a connection to the AWS API server. This can be reused for
        sending multiple emails.
        """
        if not self._client:
            self._client = get_boto_ses_client()
        return self._client
