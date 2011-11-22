# http://metajack.im/2008/09/25/an-xmpp-echo-bot-with-twisted-and-wokkel/

import sys
from wokkel.xmppim import MessageProtocol, AvailablePresence
import bbot

class EchoBotProtocol(MessageProtocol):
    def connectionMade(self):
        print "Connected!"

        # send initial presence
        self.send(AvailablePresence())

    def connectionLost(self, reason):
        print "Disconnected!"

    def onMessage(self, msg):
        print str(msg)
        try:
            reply = bbot.processMessage(msg)
        except:
            print "Unhandled exception: ", sys.exc_info()[0]

        self.send(reply)
