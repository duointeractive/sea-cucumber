"""
Handles management of SES email addresses.
"""
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email

from seacucumber.util import get_boto_ses_client


class Command(BaseCommand):
    """
    This is a completely optional command used to manage the user's SES
    email addresses. Make sure to have 'seacucumber' in INSTALLED_APPS, or this
    won't be available.
    """

    args = "<action> [<email address>]"
    help = (
        "Manages SES emails. <action> may be one of the following:\n"
        "  verify <email>   Sends a verification request for an address.\n"
        "  list             Lists all fully verified addresses.\n"
        "  delete <email>   Deletes an address from your SES account.\n\n"
        "Examples:\n"
        "  ./manage.py ses_address verify some@addres.com\n"
        "  ./manage.py ses_address list\n"
        "  ./manage.py ses_address delete some@address.com"
    )

    # <action> must be one of the following.
    valid_actions = ["verify", "list", "delete"]

    def add_arguments(self, parser):
        # Kept the argument name args to be compatible with django 1.6+
        parser.add_argument("args", nargs="+", type=str)

    def handle(self, *args, **options):
        """
        Parses/validates, and breaks off into actions.
        """
        if len(args) < 1:
            raise CommandError("Please specify an action. See --help.")
        action = args[0]
        email = None

        if action not in self.valid_actions:
            message = "Invalid action: %s" % action
            raise CommandError(message)

        if action in ["verify", "delete"]:
            if len(args) < 2:
                message = "Please specify an email address to %s." % action
                raise CommandError(message)

            email = args[1]

            if not email or not self._is_valid_email(email):
                message = "Invalid email address provided: %s" % email
                raise CommandError(message)

        # Hand this off to the action routing method.
        self._route_action(action, email)

    def _route_action(self, action, email):
        """
        Given an action and an email (can be None), figure out what to do
        with the validated inputs.

        :param str action: The action. Must be one of self.valid_actions.
        :type email: str or None
        :param email: Either an email address, or None if the action doesn't
            need an email address.
        """
        client = get_boto_ses_client()
        if action == "verify":
            client.verify_email_address(EmailAddress=email)
            print("A verification email has been sent to %s." % email)
        elif action == "delete":
            client.delete_verified_email_address(EmailAddress=email)
            print("You have deleted %s from your SES account." % email)
        elif action == "list":
            verified_result = client.list_verified_email_addresses()
            if len(verified_result.get("VerifiedEmailAddresses", [])) > 0:
                print(
                    "The following emails have been fully verified on your "
                    "Amazon SES account:"
                )
                for vemail in verified_result.get("VerifiedEmailAddresses"):
                    print("  %s" % vemail)
            else:
                print("Your account has no fully verified email addresses yet.")

    def _is_valid_email(self, email):
        """
        Given an email address, make sure that it is well-formed.

        :param str email: The email address to validate.
        :rtype: bool
        :returns: True if the email address is valid, False if not.
        """
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False
