from aiven_poke.slack import Payload, Attachment, Color, Header, Text, TextType, TextSection, \
    FieldsSection

USERS_HEADER = "*Found service users in the {main_project} pool belonging to team `{team}` with expiring credentials*"


def create_user_payload(team, channel, users, main_project):
    users_header = USERS_HEADER.format(main_project=main_project, team=team)
    return Payload(channel, attachments=[
        # TODO: Replace FALLBACK with user text
        Attachment(Color.WARNING, "FALLBACK", blocks=[
            Header(Text(TextType.PLAIN, "MAIN_HEADER")),  # TODO: Replace MAIN_HEADER with user text
            TextSection(Text(TextType.MRKDWN, users_header)),
            FieldsSection(users),
            # TODO: Replace with correct solutions for expiring users
            TextSection(Text(TextType.MRKDWN, "SOLUTION_HEADER")),
            TextSection(Text(TextType.MRKDWN, "SOLUTION1".format(team=team))),
            TextSection(Text(TextType.MRKDWN, "SOLUTION2")),
        ])
    ])
