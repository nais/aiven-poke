import textwrap

from .payload import Text, TextType, Payload, Attachment, Color, Header, TextSection, FieldsSection

CREATE_DOC = "https://doc.nais.io/persistence/kafka/manage_topics/#creating-topics-and-defining-access"
PERMA_DELETE_DOC = "https://doc.nais.io/persistence/kafka/manage_topics/#permanently-deleting-topic-and-data"
MAIN_HEADER = "Your team has topics on Aiven which are not found in a nais cluster"
WHAT_IS_THIS = " ".join(textwrap.dedent("""
    Topics on Aiven should be defined by a Topic resource in a nais cluster.
    Topics not defined by such a resource are inaccessible by applications on nais,
    which indicates that this topic may be forgotten.
""").splitlines())
TOPIC_HEADER = "*Forgotten topics found in the {main_project} pool for namespace `{namespace}`*"
SOLUTION_HEADER = "*Solution*"
SOLUTION1 = " ".join(textwrap.dedent(f"""\
    To rectify the situation, start by <{CREATE_DOC}|re-creating each topic> in the `{{team}}` namespace.
    If the intention was to delete the topic, follow the procedure for <{PERMA_DELETE_DOC}|permanently deleting data>.
""").splitlines())
SOLUTION2 = " ".join(textwrap.dedent("""\
    If you need help, reach out in <#C73B9LC86|kafka> or <#C5KUST8N6|nais>
""").splitlines())
FALLBACK = "Your team has topics on Aiven which are not found in a nais cluster. " \
           "If this is not intentional, please rectify the situation."


def create_topic_payload(team_topic, main_project):
    topic_header = TOPIC_HEADER.format(main_project=main_project, namespace=team_topic.team)
    topics = [Text(TextType.MRKDWN, "`{}`".format(topic.split(".", maxsplit=1)[-1])) for topic in team_topic.topics]
    return Payload(team_topic.slack_channel, attachments=[
        Attachment(Color.WARNING, FALLBACK, blocks=[
            Header(Text(TextType.PLAIN, MAIN_HEADER)),
            TextSection(Text(TextType.MRKDWN, WHAT_IS_THIS)),
            TextSection(Text(TextType.MRKDWN, topic_header)),
            FieldsSection(topics),
            TextSection(Text(TextType.MRKDWN, SOLUTION_HEADER)),
            TextSection(Text(TextType.MRKDWN, SOLUTION1.format(team=team_topic.team))),
            TextSection(Text(TextType.MRKDWN, SOLUTION2)),
        ])
    ])
