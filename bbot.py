from twisted.words.xish import domish

def processMessage (msg):
    # construct a basic chat reply
    reply = domish.Element((None, "message"))
    reply["to"] = msg["from"]
    reply["from"] = msg["to"]
    reply["type"] = 'chat'

    if msg["type"] == 'chat' and hasattr(msg, "body"):
        reply.addElement('body', content="bbecho: %s" % str(msg.body))
    else:
        reply.addElement('body', \
                content="Unsupported message.  Try 'help' for help.")

    return reply
