from twisted.application import service
from twisted.application.internet import TimerService
from twisted.words.protocols.jabber import jid
from wokkel.client import XMPPClient

from abbott import AbbottProtocol, DelayedMessageQueue

application = service.Application("abbott")

xmppclient = XMPPClient(jid.internJID("abbott@ransford.org/abbott"), \
        open('password.txt').read().rstrip())
xmppclient.logTraffic = True
abbott = AbbottProtocol()
abbott.setHandlerParent(xmppclient)
xmppclient.setServiceParent(application)

dq = DelayedMessageQueue()
ts = TimerService(1, dq.drainQueue)
ts.setServiceParent(application)

# vim:ft=python
