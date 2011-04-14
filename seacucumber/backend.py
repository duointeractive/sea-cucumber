from django.core.mail.backends.base import BaseEmailBackend
from seacucumber.tasks import SendEmailTask

class SESBackend(BaseEmailBackend):
    """
    A Django Email backend that uses Amazon's Simple Email Service.
    """
    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of
        email messages sent.
        """
        num_sent = 0
        for message in email_messages:
            # Hand this off to a celery task.
            SendEmailTask.delay(
                message.from_email,
                message.recipients(),
                message.message().as_string(),
            )
            num_sent += 1
        return num_sent

