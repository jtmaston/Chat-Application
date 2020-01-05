import json

DebugFlag = False


class PacketSchema:
    """Base schema for all packet types"""

    def __init__(self):
        self.senderAddress = tuple()
        self.destinationAddress = tuple()
        self.senderUsername = str()
        self.destinationUsername = str()
        self.command = str()
        self.processed = False

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


class HandshakePacket(PacketSchema):  # handshake packets have an extra parameter
    def __init__(self, JsonData):
        super().__init__()
        self.connectionType = str()
        if JsonData:
            self.LoadJson(JsonData)

    def load(self, json_data):
        super().load(json_data)
        self.connectionType = json_data['connectionType']


class ClientPacket(PacketSchema):  # superfluous, will remove
    """Packet used for exchanging chat data"""
    pass


class ListenerPacket(PacketSchema):  # the listener packet, equally superfluous
    def __init__(self, JsonData):
        super().__init__()
        if JsonData:
            self.LoadJson(JsonData)


class BadPacket(PacketSchema):  # bad packet
    def __init__(self):
        super().__init__()
        self.command = "Bad"


class TesterPacket(PacketSchema):  # bad packet
    def __init__(self):
        super().__init__()
        self.command = "test"
        self.connectionType = "none"


def PacketFormatValidator(TestedObject):  # packet tester
    return isinstance(TestedObject, PacketSchema)
