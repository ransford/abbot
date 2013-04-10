import abbot
from twisted.words.xish import domish

def makeMessage (msg):
    fakeMessage = domish.Element((None, 'message'))
    fakeMessage['from'] = 'ben@ransford.org'
    fakeMessage['to'] = 'abbot@ransford.org'
    fakeMessage['type'] = 'chat'
    fakeMessage.addElement('body', content=str(msg))
    return fakeMessage

mp = abbot.MessageParser()
(verb, args) = mp.parseString('help')

ap = abbot.AbbotProtocol()
m = makeMessage(verb)
print "Message: ", m
rep = ap.processMessage(m)

print "Response:", str(rep)
