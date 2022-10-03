"""
Shows some usage levels and limits for the last and previous 24 hours.
"""
import datetime

from django.core.management.base import BaseCommand

from seacucumber.util import get_boto_ses_client


class Command(BaseCommand):
    """
    This command shows some really vague usage and quota stats from SES.
    """

    help = "Shows SES usage and quota limits."

    def handle(self, *args, **options):
        """
        Renders the output by piecing together a few methods that do the
        dirty work.
        """
        # AWS SES connection, which can be re-used for each query needed.
        client = get_boto_ses_client()
        self._print_quota(client)
        self._print_daily_stats(client)

    def _print_quota(self, client):
        """
        Prints some basic quota statistics.
        """
        quota = client.get_send_quota()

        print("--- SES Quota ---")
        print("  24 Hour Quota: %s" % quota["Max24HourSend"])
        print("  Sent (Last 24 hours): %s" % quota["SentLast24Hours"])
        print("  Max sending rate: %s/sec" % quota["MaxSendRate"])

    def _print_daily_stats(self, client):
        """
        Prints a Today/Last 24 hour stats section.
        """
        stats = client.get_send_statistics()
        stats = stats["SendDataPoints"]

        today = datetime.date.today()
        current_day = {"HeaderName": "Current Day: %s/%s" % (today.month, today.day)}
        prev_day = {"HeaderName": "Past two weeks"}

        for data_point in stats:
            if data_point.get("Timestamp").date() == today:
                day_dict = current_day
            else:
                day_dict = prev_day

            self._update_day_dict(data_point, day_dict)

        for day in [current_day, prev_day]:
            print("--- %s ---" % day.get("HeaderName", 0))
            print("  Delivery attempts: %s" % day.get("DeliveryAttempts", 0))
            print("  Bounces: %s" % day.get("Bounces", 0))
            print("  Rejects: %s" % day.get("Rejects", 0))
            print("  Complaints: %s" % day.get("Complaints", 0))

    def _update_day_dict(self, data_point, day_dict):
        """
        Helper method for :meth:`_print_daily_stats`. Given a data point and
        the correct day dict, update attribs on the dict with the contents
        of the data point.

        :param dict data_point: The data point to add to the day's stats dict.
        :param dict day_dict: A stats-tracking dict for a 24 hour period.
        """
        for topic in ["Bounces", "Complaints", "DeliveryAttempts", "Rejects"]:
            day_dict[topic] = day_dict.get(topic, 0) + int(data_point[topic])
