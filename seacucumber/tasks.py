from django.conf import settings
from boto.ses import SESConnection
from celery.task import Task

class SendEmailTask(Task):
    """
    Sends an email through Boto's SES API module.
    """
    # TODO: Make this a setting.
    max_retries = 60
    # TODO: Make this a setting.
    default_retry_delay = 60

    def __init__(self, *args, **kwargs):
        self.connection = None
        self._access_key_id = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
        self._access_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
        self._api_endpoint = getattr(settings, 'AWS_SES_API_HOST',
                                     SESConnection.DefaultHost)

    def run(self, from_email, recipients, message):
        """
        This does the dirty work.
        
        TOOD: Document params.
        """
        self._open_ses_conn()
        try:
            self.connection.send_raw_email(
                source=from_email,
                destinations=recipients,
                raw_message=message,
            )
        except SESConnection.ResponseError:
            self.retry(
                countdown=self.default_retry_delay,
                exc=SESConnection.ResponseError,
            )
        self._close_ses_conn()


    def _open_ses_conn(self):
        """
        Create a connection to the AWS API server. This can be reused for
        sending multiple emails.
        """
        if self.connection:
            return

        try:
            self.connection = SESConnection(
                aws_access_key_id=self._access_key_id,
                aws_secret_access_key=self._access_key,
                host=self._api_endpoint,
            )
        # TODO: Get more specific with this exception block.
        except:
            self.retry(
                countdown=self.default_retry_delay,
            )

    def _close_ses_conn(self):
        """
        Close any open HTTP connections to the API server.
        """
        try:
            self.connection.close()
            self.connection = None
        except:
            # It doesn't really matter at this point.
            pass
