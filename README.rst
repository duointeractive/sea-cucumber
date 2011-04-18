================
Sea Cucumber 1.2
================
:Info: A Django email backend for Amazon Simple Email Service, backed by django-celery_
:Author: DUO Interactive, LLC
:Inspired by: Harry Marr's django-ses_.

A bird's eye view
=================
Sea Cucumber is a mail backend for Django_. Instead of sending emails
through a traditional SMTP mail server, Sea Cucumber routes email through
Amazon Web Services' excellent Simple Email Service (SES_) via django-celery_.

Why Sea Cucumber/SES instead of SMTP?
=====================================
Configuring, maintaining, and dealing with some complicated edge cases can be
time-consuming. Sending emails with Sea Cucumber might be attractive to you if:

* You don't want to maintain mail servers.
* Your mail server is slow or unreliable, blocking your views from rendering.
* You need to send a high volume of email.
* You don't want to have to worry about PTR records, Reverse DNS, email
  whitelist/blacklist services.
* You are already deployed on EC2 (In-bound traffic to SES is free from EC2
  instances). This is not a big deal either way, but is an additional perk if 
  you happen to be on AWS.

Installation
============
Assuming you've got Django_ and django-celery_ installed, you'll need 
Boto_ 2.0b4 or higher. boto_ is a Python library that wraps the AWS API.

You can do the following to install boto_ 2.0b4 (we're using --upgrade here to
make sure you get 2.0b4)::

    pip install --upgrade boto

Install Sea Cucumber::

    pip install seacucumber

Add the following to your settings.py::

    EMAIL_BACKEND = 'seacucumber.backend.SESBackend'

    # These are optional -- if they're set as environment variables they won't
    # need to be set here as well
    AWS_ACCESS_KEY_ID = 'YOUR-ACCESS-KEY-ID'
    AWS_SECRET_ACCESS_KEY = 'YOUR-SECRET-ACCESS-KEY'

    # Make sure to do this if you want the ``ses_address`` management command.
    INSTALLED_APPS = (
        ...
        'seacucumber'
    )

Email Address Verification
==========================

Before you can send email 'from' an email address through SES, you must first 
verify your ownership of it::

	./manage.py ses_address verify batman@gotham.gov

After you've run the verification above you will need to check the email
account's inbox (from your mail client or provider's web interface) and click 
the authorization link in the email Amazon sends you. After that, your address
is ready to go.

To confirm the verified email is ready to go::

	./manage.py ses_address list

To remove a previously verified address::

	./manage.py ses_address delete batman@gotham.gov

Now, when you use ``django.core.mail.send_mail`` from a verified email address, 
Sea Cucumber will handle message delivery.

Rate Limiting
=============

If you are a new SES user, your default quota will be 1,000 emails per 24
hour period at a maximum rate of one email per second. Sea Cucumber defaults
to enforcing the one email per second at the celery level, but you must not
have disabled celery rate limiting. 

If you have this::

    CELERY_DISABLE_RATE_LIMITS = True
    
Change it to this::

    CELERY_DISABLE_RATE_LIMITS = False
    
Then check your SES max rate by running::

    ./manage.py ses_usage
    
If your rate limit is more than ``1.0/sec``, you'll need to set that numeric
value in your ``CUCUMBER_RATE_LIMIT`` setting like so::

    # Rate limit to three outgoing SES emails a second.
    CUCUMBER_RATE_LIMIT = 3
    
Failure to follow the rate limits may result in BotoServerError exceptions
being raised, which makes celery unhappy.

As a general note, your quota and max send rate will increase with usage, so
check the ``ses_usage`` management command again at a later date after you've
sent some emails. You'll need to manually bump up your rate settings in
``settings.py``.

Django Builtin-in Error Emails
==============================

If you'd like Django's `Builtin Email Error Reporting`_ to function properly
(actually send working emails), you'll have to explicitly set the
``SERVER_EMAIL`` setting to one of your SES-verified addresses. Otherwise, your
error emails will all fail and you'll be blissfully unaware of a problem.

*Note:* You can use the included ``ses_address`` management command to handle
address verification.

Getting Help
============

If you have any questions, feel free to either post them to our
`issue tracker`_, or visit us on IRC at:

:Host: irc.freenode.net
:Port: 6667
:Room: #duo

.. _django-ses: https://github.com/hmarr/django-ses
.. _django-celery: http://ask.github.com/django-celery/
.. _celery: http://docs.celeryproject.org/en/v2.2.5/index.html
.. _Builtin Email Error Reporting: http://docs.djangoproject.com/en/1.2/howto/error-reporting/
.. _Django: http://djangoproject.com
.. _Boto: http://boto.cloudhackers.com/
.. _SES: http://aws.amazon.com/ses/
.. _issue tracker: https://github.com/duointeractive/django-athumb/issues