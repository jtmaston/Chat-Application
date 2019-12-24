import json
import socket

DebugFlag = True

"""~~~~DEV2 TODO~~~~"""
# Done: Sender and address
# Done: All ip addresses become tuples, w/o separate methods
# Todo: Comment and code cleanup
# Todo: When done, merge into dev
# Todo: Perhaps get rid of aux packages?
"""~~~~~~~~~~~~~~~~~"""

class PacketSchema:
    """Base schema for all packet types"""

    def __init__(self, JsonData):
        self.senderAddress = tuple()
        self.destinationAddress = tuple()
        self.senderUsername = str()
        self.destinationUsername = str()
        self.command = str()
        self.processed = False
        if JsonData:
            self.LoadJson(JsonData)

    def load(self, json_data):  # transfer data from json to parameters
        self.senderAddress = json_data['senderAddress']
        self.destinationAddress = json_data['destinationAddress']
        self.senderUsername = json_data['senderUsername']
        self.destinationUsername = json_data['destinationUsername']
        self.command = json_data['command']
        self.processed = json_data['processed']

    def __str__(self):
        return f"Sending package from {self.senderAddress[0]}:{self.senderAddress[1]} to " \
               f"{self.destinationAddress[0]}:{self.destinationAddress[1]}"

    def DumpJson(self):  # returns binary json data
        return json.dumps(self.__dict__).encode('UTF-8')

    def LoadJson(self, JsonData):  # loads binary json data into attrs
        self.load(json.loads(JsonData))

    def __eq__(self, other):
        if not isinstance(other, PacketSchema):
            raise TypeError
        return self.__dict__ == other.__dict__


class HandshakePacket(PacketSchema):
    """Packet used in Handshake part of communication"""
    pass


class ClientPacket(PacketSchema):
    """Packet used for exchanging chat data"""
    pass


class ListenerPacket(PacketSchema):
    def __init__(self, JsonData):
        super().__init__(JsonData)
        self.destinationAddress = "LISTENER"


class BadPacket(PacketSchema):
    def __init__(self, JsonData):
        super().__init__(JsonData)
        self.command = "Bad"


def PacketFormatValidator(TestedObject):
    return isinstance(TestedObject, PacketSchema)
