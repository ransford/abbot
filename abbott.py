import sys
from twisted.words.xish import domish

class MessageActor:
    verbs = ['help', 'echo']

    def __init__ (self):
        pass

    def help (self, args):
        return 'Known verbs: %s' % ', '.join(self.verbs)

    def echo (self, args):
        return ' '.join(args)

    def dispatch (self, fname, args):
        fn = getattr(self, fname)
        return fn(args)

class MessageParser:

    def __init__ (self):
        pass

    def parseString (self, string):
        verb = string.split(' ')[0]
        if verb not in MessageActor.verbs:
            raise RuntimeError("Unsupported verb.  Try 'help'.")
        args = string.split(' ')[1:]
        return (verb, args)

def processMessage (msg):
    # construct a basic chat reply
    reply = domish.Element((None, "message"))
    reply["to"] = msg["from"]
    reply["from"] = msg["to"]
    reply["type"] = 'chat'

    ma = MessageActor()
    mp = MessageParser()

    if msg["type"] == 'chat' and hasattr(msg, "body"):
        try:
            (verb, args) = mp.parseString(str(msg.body))
            reply.addElement('body', content=str(ma.dispatch(verb, args)))
        except RuntimeError as re:
            reply.addElement('body', content=re.message)
        except:
            print "Unhandled exception: ", sys.exc_info()
            reply.addElement('body', content="Unknown error.")
    else:
        reply.addElement('body', content="Unsupported message format.")

    return reply
