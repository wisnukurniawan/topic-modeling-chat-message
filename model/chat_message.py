
class ChatMessage:
    name = ""
    content = ""
    create_at = ""
    channel = ""
    sender_role = ""
    sender_id = ""

    def __init__(self,
                 name,
                 content,
                 create_at,
                 channel,
                 sender_role,
                 sender_id):
        self.name = name
        self.content = content
        self.create_at = create_at
        self.channel = channel
        self.sender_role = sender_role
        self.sender_id = sender_id

    def __str__(self):
        return "name: %s, content: %s, create_at: %s, channel: %s, sender_role: %s, sender_id: %s" % \
               (self.name, self.content, self.create_at, self.channel, self.sender_role, self.sender_id)
