class Packet(object):
    def __init__(self, data_type=0, data_id=0, sequence_number=0, length=0, checksum=0, data=bytearray(), parsed_bytes=0, parsed_data=0):
        if (parsed_data!=0):
            self.data_packet(parsed_data, data_id, sequence_number, data_type)
        elif (parsed_bytes==0):
            self.data_type = data_type # Hex number (0x0-0x3)
            self.data_id = data_id # Hex number (0x0-0x3)
            self.sequence_number = sequence_number # Integer
            self.length = length # Integer
            self.checksum = checksum # CRC, check = 0xFFFF = 65535, Size = 16 bit
            self.data = data # bytearray
        else:
            self.data_type = parsed_bytes[0]%16 # Hex number (0x0-0x3)
            self.data_id = parsed_bytes[0]//16 # Hex number (0x0-0x3)
            self.sequence_number = parsed_bytes[1]*256 + parsed_bytes[2]  # Integer
            self.length = parsed_bytes[3]*256 + parsed_bytes[4]  # Integer
            self.checksum = parsed_bytes[5]*256 + parsed_bytes[6]  # CRC, check = 0xFFFF = 65535, Size = 16 bit
            self.data = parsed_bytes[7:] # bytearray

    def parse(self):
        result = bytearray(7)

        #Type + ID
        first_byte = self.data_type + self.data_id*16
        result[0] = first_byte

        #Sequence Number
        result[1] = self.sequence_number // 256
        result[2] = self.sequence_number % 256

        #Length
        result[3] = self.length // 256
        result[4] = self.length % 256
        
        #checksum
        result[5] = self.checksum // 256
        result[6] = self.checksum % 256

        #data
        result = result + self.data
        return bytes(result)

    def data_packet(self, parsed_data, data_id, sequence_number, data_type):
        self.data_type = data_type
        self.data_id = data_id
        self.sequence_number = sequence_number
        self.length = len(parsed_data)
        self.data = parsed_data
        self.checksum = 0
        # # Checksum creation (CRC)
        # arr = bytearray(self.parse())
        # i=1
        # length = len(arr)
        # buffer = 0
        # int_values = [x for x in arr]
        # for x in int_values:
        #     y = x << 16
        #     if (buffer != 0):
        #         y = y^buffer
        #         buffer = 0
        #     y = y << 16
        #     while (y>65535):
        #         polynom = 65535
        #         while polynom<y:
        #             polynom = polynom << 1
        #         y = y^polynom
        #     buffer = y & 65535
        
        # Checksum creation (Every 2 bytes)
        arr = bytearray(self.parse())
        i=0
        length = len(arr)
        buffer = 0
        int_values = [x for x in arr]
        length =len(int_values)//2 
        extra = len(int_values)%2
        while i<length:
            buffer = buffer ^ (int_values[i*2]*256 + int_values[i*2+1])
            i+=1
        if (extra>0):
            buffer = buffer ^ int_values[i*2]
        self.checksum = buffer

    def sum_checker(self):
        temp = self.checksum
        self.checksum = 0
        # # Checksum creation (CRC)
        # arr = bytearray(self.parse())
        # i=1
        # length = len(arr)
        # buffer = 0
        # int_values = [x for x in arr]
        # for x in int_values:
        #     y = x << 16
        #     if (buffer != 0):
        #         y = y^buffer
        #         buffer = 0
        #     y = y << 16
        #     while (y>65535):
        #         polynom = 65535
        #         while polynom<y:
        #             polynom = polynom << 1
        #         y = y^polynom
        #     buffer = y & 65535
        # Checksum creation (Every 2 bytes)
        arr = bytearray(self.parse())
        i=0
        length = len(arr)
        buffer = 0
        int_values = [x for x in arr]
        length =len(int_values)//2 
        extra = len(int_values)%2
        while i<length:
            buffer = buffer ^ (int_values[i*2]*256 + int_values[i*2+1])
            i+=1
        if (extra>0):
            buffer = buffer ^ int_values[i*2]
        self.checksum = buffer

        self.checksum = buffer
        result = (self.checksum == temp)
        self.checksum = temp
        return result 