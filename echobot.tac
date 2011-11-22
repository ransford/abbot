from twisted.application import service
from twisted.words.protocols.jabber import jid
from wokkel.client import XMPPClient

from echobot import EchoBotProtocol

application = service.Application("echobot")

xmppclient = XMPPClient(jid.internJID("bbot@ransford.org/bbot"), \
        open('password.txt').read().rstrip())
xmppclient.logTraffic = True
echobot = EchoBotProtocol()
echobot.setHandlerParent(xmppclient)
xmppclient.setServiceParent(application)

# vim:ft=python
