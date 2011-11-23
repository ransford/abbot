from twisted.application import service
from twisted.words.protocols.jabber import jid
from wokkel.client import XMPPClient

from abbott import AbbottProtocol

application = service.Application("abbott")

xmppclient = XMPPClient(jid.internJID("abbott@ransford.org/abbott"), \
        open('password.txt').read().rstrip())
xmppclient.logTraffic = True
abbott = AbbottProtocol()
abbott.setHandlerParent(xmppclient)
xmppclient.setServiceParent(application)

# vim:ft=python
