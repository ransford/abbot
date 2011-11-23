import abbott
from twisted.words.xish import domish

def makeMessage (msg):
    fakeMessage = domish.Element((None, 'message'))
    fakeMessage['from'] = 'ben@ransford.org'
    fakeMessage['to'] = 'abbott@ransford.org'
    fakeMessage['type'] = 'chat'
    fakeMessage.addElement('body', content=str(msg))
    return fakeMessage

mp = abbott.MessageParser()
(verb, args) = mp.parseString('help')

ap = abbott.AbbottProtocol()
m = makeMessage(verb)
print "Message: ", m
rep = ap.processMessage(m)

print "Response:", str(rep)
