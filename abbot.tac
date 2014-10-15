from twisted.application import service
from twisted.application.internet import TimerService
from twisted.words.protocols.jabber import jid
from wokkel.client import XMPPClient

from abbot import AbbotProtocol, DelayedMessageQueue

application = service.Application("abbot")

xmppclient = XMPPClient(jid.internJID("abbot@ransford.org/abbot"), \
        open('password.txt').read().rstrip())
xmppclient.logTraffic = True
dmq = DelayedMessageQueue()
abbot = AbbotProtocol(dmq)
abbot.setHandlerParent(xmppclient)
xmppclient.setServiceParent(application)
ts = TimerService(10, dmq.drainQueue)
ts.setServiceParent(application)

# vim:ft=python
