import textwrap

from .payload import Payload, Attachment, Color, Header, Text, TextType, TextSection
from ..models import ExpiringUser

RENEW_DOC = "https://doc.nais.io/how-to-guides/persistence/kafka/renew-credentials-for-non-nais/"

FALLBACK = " ".join(textwrap.dedent("""\
    Your team has users with expiring credentials in the {main_project} pool, defined in {cluster_name}.
    Consult the nais documentation to find out how to fix these.
    The following users needs attention:
    {usernames} 
""").splitlines())
MAIN_HEADER = "Your team has users in Kafka with expiring credentials"
WHAT_IS_THIS = " ".join(textwrap.dedent("""\
    Kafka service users are issued certificates with a limited lifespan.
    When the certificates are getting close to expiring, warnings are issued to avoid interruptions in service.
    The applications using the affected users needs to get new credentials before the expiry date.
""").splitlines())
USERS_HEADER = ("*Found service users defined in `{cluster_name}`, for the `{main_project}` pool,"
                " with expiring credentials*")
SOLUTION_HEADER = "*Solution*"
SOLUTION_PROTECTED = " ".join(textwrap.dedent(f"""\
    For users used by legacy applications not running in the nais platform, consult the documentation on
    <{RENEW_DOC}|how to renew credentials for non-nais>.
""").splitlines())
SOLUTION_NAIS_APP = " ".join(textwrap.dedent("""\
    For users used by applications running in the nais platform, a simple redeploy of your application should be enough.
""").splitlines())
NEEDS_HELP = " ".join(textwrap.dedent("""\
    If you need help, reach out in <#C5KUST8N6|nais>
""").splitlines())
USER_ROW = "`{username}` used by {application}{protected}: Expires after {expires}"


def create_user_payload(team, channel, users: list[ExpiringUser], main_project, cluster_name):
    usernames = [user.username for user in users]
    fallback_text = FALLBACK.format(main_project=main_project, usernames="\n* ".join(usernames),
                                    cluster_name=cluster_name)
    users_header = USERS_HEADER.format(main_project=main_project, team=team, cluster_name=cluster_name)
    blocks = [
        Header(Text(TextType.PLAIN, MAIN_HEADER)),
        TextSection(Text(TextType.MRKDWN, WHAT_IS_THIS)),
        TextSection(Text(TextType.MRKDWN, users_header)),
    ]

    rows = []
    for user in users:
        params = {
            "username": user.username,
            "application": user.application,
            "protected": " (non-nais)" if user.is_protected else "",
            "expires": user.expiring_cert_not_valid_after_time,
        }
        rows.append(USER_ROW.format(**params))
    blocks.append(TextSection(Text(TextType.MRKDWN, "\n".join(rows))))

    blocks.extend([
        TextSection(Text(TextType.MRKDWN, SOLUTION_HEADER)),
        TextSection(Text(TextType.MRKDWN, SOLUTION_PROTECTED.format(team=team))),
        TextSection(Text(TextType.MRKDWN, SOLUTION_NAIS_APP.format(team=team))),
        TextSection(Text(TextType.MRKDWN, NEEDS_HELP)),
    ])

    return Payload(channel, attachments=[
        Attachment(Color.WARNING, fallback_text, blocks=blocks)
    ])
