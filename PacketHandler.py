import json


class PacketSchema:
    """Base schema for all packet types"""

    def __init__(self, JsonData):
        self.command = ''
        self.hostname = ''
        self.port = 0
        self.username = ''
        self.message = ''
        self.destination = ''
        self.processed = False
        if JsonData:
            self.LoadJson(JsonData)

    def load(self, json_data):   # transfer data from json to parameters
        self.hostname = json_data['hostname']
        self.port = json_data['port']
        self.username = json_data['username']
        self.message = json_data['message']
        self.command = json_data['command']
        self.destination = json_data['destination']
        self.processed = json_data['processed']

    def __str__(self):
        return self.hostname + '\n' + str(self.port) + '\n' + self.username

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

    def __init__(self, JsonData):
        super().__init__(JsonData)
        self.command = 'hello'
        self.username = 'Alexey'
        self.message = "nobody's home"
        self.destination = 'Danny'
        self.processed = False
        if JsonData:
            self.LoadJson(JsonData)
    def LoadIp(self, Address):
        if not isinstance(Address, tuple):
            raise TypeError
        else:
            self.hostname = Address[0]
            self.port = Address[1]


class PotatoPackage(PacketSchema):
    pass


def PacketFormatValidator(TestedObject):
    return isinstance(TestedObject, PacketSchema)