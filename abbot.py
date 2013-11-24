# http://metajack.im/2008/09/25/an-xmpp-echo-bot-with-twisted-and-wokkel/

# http://pleac.sourceforge.net/pleac_python/datesandtimes.html

import re, sys
from heapq import heappop, heappush
from time import mktime
from datetime import datetime, timedelta
from twisted.words.xish import domish
from wokkel.xmppim import MessageProtocol, AvailablePresence

class AbbotProtocol (MessageProtocol):
    dmq = None

    def __init__ (self):
        pass

    def setDMQ (self, d):
        self.dmq = d

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
                reply.addElement('body', content=str(ma.dispatch(verb, msg, args)))
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
             'time', \
             'echo', \
             'in', \
             'at', \
    ]
    abprot = None

    def __init__ (self, abprot):
        self.abprot = abprot

    def verb_help (self, msg, args):
        """Usage: help [cmd]
        Without arguments, lists available verbs.
        With optional [cmd] arguments, shows help for verb 'cmd'."""
        if len(args) == 1:
            if args[0] in self.verbs:
                return getattr(self, 'verb_%s' % args[0]).__doc__
            else:
                return 'Unknown verb "{}".'.format(args[0])
        elif len(args) == 0:
            return 'Known verbs: %s.' % ', '.join(self.verbs) + \
                '\n"help <verb>" for specific help.'

    def verb_time (self, msg, args):
        """Usage: time
        Echos the current time."""
        return datetime.now().strftime('%c')

    def verb_echo (self, msg, args):
        """Usage: echo string ...
        Echos back string arguments."""
        return ' '.join(args)

    def verb_in (self, msg, args):
        """Usage: in N<h,m> string ...
        Echos back string arguments N hours/minutes from now."""
        # parse time argument
        stm = datetime.now()
        m = re.match('(\d+)([hm])', args[0])
        if m is None:
            return verb_in.__doc__

        howmany = int(m.group(1))
        units = m.group(2).lower()
        if units == 'h':
            stm = stm + timedelta(hours=howmany)
        else: # minutes
            stm = stm + timedelta(minutes=howmany)
        print args[0], " -> ", stm

        reply = self.abprot.makeMessage(m_to=msg['from'],  m_from=msg['to'], \
                m_body=' '.join(args[1:]))

        self.abprot.getDMQ().put(stm, reply)
        return 'scheduled for %s' % stm

    def verb_at (self, msg, args):
        """Usage: at HH:MM string ...
        Echos back string arguments at time HH:MM."""
        # parse time argument
        now = datetime.now()
        stm = datetime.now()
        m = re.match('(\d+):(\d+)', args[0])
        stm = stm.replace(hour=int(m.group(1)), minute=int(m.group(2)), \
                second=0, microsecond=0)

        if stm < now:
            stm = stm + timedelta(hours=12)
        print args[0], " -> ", stm

        reply = self.abprot.makeMessage(m_to=msg['from'],  m_from=msg['to'], \
                m_body=' '.join(args[1:]))

        self.abprot.getDMQ().put(stm, reply)
        return 'scheduled for %s' % stm

    def dispatch (self, fname, msg, args):
        fn = getattr(self, 'verb_%s' % fname)
        return fn(msg, args)

class MessageParser:
    abprot = None

    def __init__ (self, abprot):
        self.abprot = abprot

    def parseString (self, string):
        verb = string.split(' ')[0]
        if verb and verb not in MessageActor.verbs:
            raise RuntimeError("Unsupported verb \"{}\".  " \
                    "Try 'help'.".format(verb))
        args = string.split(' ')[1:]
        return (verb, args)

class DelayedMessageQueue:
    heap = []
    abprot = None

    def __init__ (self, abprot):
        if abprot.getDMQ() is None:
            abprot.setDMQ(self)
        self.abprot = abprot

    def put (self, msg_time, msg_obj):
        heappush(self.heap, (msg_time, msg_obj))

    def drainQueue (self):
        # print "Draining queue."
        while len(self.heap):
            (mtime, msg) = self.heap[0]
            if datetime.now() < mtime:
                break
            (mtime, msg) = heappop(self.heap)
            print "Time: ", mtime, " vs. now()=", datetime.now()
            print "Body: ", self.abprot.send(msg)
