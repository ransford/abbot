# http://metajack.im/2008/09/25/an-xmpp-echo-bot-with-twisted-and-wokkel/

import re, sys
from heapq import heappop, heappush
from time import mktime, strptime, time, localtime
from twisted.words.xish import domish
from wokkel.xmppim import MessageProtocol, AvailablePresence

class AbbotProtocol (MessageProtocol):
    dmq = None

    def __init__ (self):
        self.dmq = DelayedMessageQueue()

    def getDMQ (self):
        return self.dmq

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

    def makeMessage (self, m_type='chat', m_to=None, m_from=None, m_body=None):
        m = domish.Element((None, "message"))
        m["type"] = m_type
        m["to"] = m_to
        m["from"] = m_from
        if m_body is not None:
            m.addElement('body', content=m_body)
        return m

    def processMessage (self, msg):
        # construct a basic chat reply
        reply = self.makeMessage('chat', msg['from'], msg['to'], None)

        ma = MessageActor(self)
        mp = MessageParser(self)

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
    abprot = None

    def __init__ (self, abprot):
        self.abprot = abprot

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
        stm = mktime(strptime(args[0], '%H:%M'))
        stm = localtime()
        m = re.match('(\d+):(\d+)', args[0])
        stm.tm_hour = int(m.group(1))
        stm.tm_min  = int(m.group(2))
        print args[0], " -> ", stm
        msg = self.abprot.makeMessage(m_to='ben@ransford.org', \
                m_from='abbot@ransford.org', m_body=' '.join(args[1:]))
        self.abprot.getDMQ().put(mktime(stm), msg)
        return 'scheduled.'

    def dispatch (self, fname, args):
        fn = getattr(self, 'verb_%s' % fname)
        return fn(args)

class MessageParser:
    abprot = None

    def __init__ (self, abprot):
        self.abprot = abprot

    def parseString (self, string):
        verb = string.split(' ')[0]
        if verb not in MessageActor.verbs:
            raise RuntimeError("Unsupported verb.  Try 'help'.")
        args = string.split(' ')[1:]
        return (verb, args)

class DelayedMessageQueue:
    heap = []

    def __init__ (self):
        pass

    def put (self, msg_time, msg_obj):
        heappush(self.heap, (msg_time, msg_obj))

    def drainQueue (self):
        print "Draining queue."
        while len(self.heap):
            (mtime, msg) = self.heap[0]
            if time() < mtime:
                break
            (mtime, msg) = heappop(self.heap)
            print "Time: ", mtime, " vs. time()=", time()
            print "Body: ", msg.body
