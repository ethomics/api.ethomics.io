import re
from django.core.mail import send_mail

def send_welcome_email(user, hostname):
    """Sends an email welcoming a user to ethomics."""

    message = re.compile(r"  +").sub("", f"""Dear {user.name},
    <br><br>
    Thank you for signing up to <a href=\"{hostname}\">ethomics.io</a>.

    <br><br>
    Thanks,<br>
    The ethomics.io Team""").strip()
    send_mail(
        subject="Welcome to ethomics",
        message=message,
        html_message=message,
        from_email="ethomics <noreply@ethomics.io>",
        recipient_list=[user.email],
        fail_silently=True
    )


def send_waiting_list_email(email):
    """Sends an email confirming waiting list position."""

    message = re.compile(r"  +").sub("", f"""Thank you for signing up to the
    ethomics waiting list.
    <br><br>
    Once you reach the front of the list, we'll let you know and you can create
    your account.
    <br><br>
    In the meantime, please feel free to reach out to us via email at
    <a href=\"mailto:support@ethomics.io\">support@ethomics.io</a>, or
    <a href=\"https://twitter.com/ethomicsio\">on Twitter</a> if you have any
    queries.
    <br><br>
    Thanks,<br>
    The ethomics Team
    """).strip()
    send_mail(
        subject="You're on the ethomics.io Waiting List",
        message=message,
        html_message=message,
        from_email="ethomics <noreply@ethomics.io>",
        recipient_list=[email],
        fail_silently=False
    )


def send_approval_email(email, hostname):
    """Sends an email informing user they can sign up."""

    message = re.compile(r"  +").sub("", f"""Great news - you can now sign up
    for ethomics.<br><br>
    ethomics is the tool for PIs to manage their lab's projects, deadlines and
    members. Some time ago you signed up for our waiting list, and now we're
    ready for you.
    <br><br>
    You can signup at <a href=\"{hostname}/signup/\">{hostname.split('//')[1]}/signup</a>.
    <br><br>
    Thanks,<br>
    The ethomics.io Team
    """).strip()
    send_mail(
        subject="You can now sign up for ethomics.io!",
        message=message,
        html_message=message,
        from_email="ethomics.io <noreply@ethomics.io>",
        recipient_list=[email],
        fail_silently=False
    )