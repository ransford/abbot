# http://metajack.im/2008/09/25/an-xmpp-echo-bot-with-twisted-and-wokkel/

import sys
from twisted.words.xish import domish
from wokkel.xmppim import MessageProtocol, AvailablePresence

class AbbottProtocol (MessageProtocol):
    def connectionMade(self):
        print "Connected!"

        # send initial presence
        self.send(AvailablePresence())

    def connectionLost(self, reason):
        print "Disconnected!"

    def onMessage(self, msg):
        print str(msg)
        reply = None
        try:
            reply = self.processMessage(msg)
        except:
            print "Unhandled exception: ", sys.exc_info()

        self.send(reply)

    def processMessage (self, msg):
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

class MessageActor:
    verbs = ['help', \
             'echo', \
             'in', \
             'at', \
    ]

    def __init__ (self):
        pass

    def verb_help (self, args):
        """Usage: help [cmd]
        Without arguments, lists available verbs.
        With optional [cmd] arguments, shows help for verb 'cmd'."""
        if len(args) == 1:
            if args[0] in self.verbs:
                return getattr(self, 'verb_%s' % args[0]).__doc__
            else:
                return 'Unknown verb.'
        elif len(args) == 0:
            return 'Known verbs: %s.' % ', '.join(self.verbs) + \
                '\n"help <verb>" for specific help.'

    def verb_echo (self, args):
        """Usage: echo string ...
        Echos back string arguments."""
        return ' '.join(args)

    def verb_in (self, args):
        """Usage: in N<h,m,s> string ...
        Echos back string arguments N hours/minutes/seconds from now."""
        # parse time argument
        return ' '.join(args)

    def verb_at (self, args):
        """Usage: at HH:MM string ...
        Echos back string arguments at time HH:MM."""
        # parse time argument
        return ' '.join(args)

    def dispatch (self, fname, args):
        fn = getattr(self, 'verb_%s' % fname)
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
