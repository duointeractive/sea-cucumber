from optparse import OptionParser, make_option

from boto.ses import SESConnection

from django.core.management.base import BaseCommand, CommandError
from django.core.validators import email_re
from django.conf import settings

def is_valid_email(email):
    if email_re.match(email):
        return True
    return False

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-c", "--command", dest="command", default="", help="The verify command to run: verify, delete, list"),
        make_option("-e", "--email", dest="email", default=""),
    )

    def handle(self, *args, **options):
        command = options.get("command")
        email = options.get("email")
        
        if command in ['verify', 'delete']:
            if not email or not is_valid_email(email):
                raise CommandError("Please pass a valid email address to verify.")        
        
        connection = self.get_ses_connection()    
        if command == "verify":
            connection.verify_email_address(email)
        elif command == "delete":
            connection.delete_verified_email_address(email)
        elif command == "list":
            verified_result = connection.list_verified_email_addresses()
            if len(verified_result.VerifiedEmailAddresses) > 0:
                print "The following emails have been verified with your Amazon SES account:"
                for vemail in verified_result.VerifiedEmailAddresses:
                    print vemail
            else:
                print "No email addresses have been verified for your SES account."
    
    def get_ses_connection(self):
        access_key_id = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
        access_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
        api_endpoint = getattr(settings, 'AWS_SES_API_HOST', SESConnection.DefaultHost)        
        
        connection = None
        try:
            connection = SESConnection(
                aws_access_key_id=access_key_id,
                aws_secret_access_key=access_key,
                host=api_endpoint,
            )
            return connection
        except:
            raise Exception("Could not connect to Amazon SES service")        
