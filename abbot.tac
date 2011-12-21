from twisted.application import service
from twisted.application.internet import TimerService
from twisted.words.protocols.jabber import jid
from wokkel.client import XMPPClient

from abbot import AbbotProtocol, DelayedMessageQueue

application = service.Application("abbot")

xmppclient = XMPPClient(jid.internJID("abbot@ransford.org/abbot"), \
        open('password.txt').read().rstrip())
xmppclient.logTraffic = True
abbot = AbbotProtocol()
abbot.setHandlerParent(xmppclient)
xmppclient.setServiceParent(application)

dq = DelayedMessageQueue()
ts = TimerService(1, dq.drainQueue)
ts.setServiceParent(application)

# vim:ft=python
