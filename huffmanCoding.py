import heapq
import os

class BinaryTreeNode:
    def __init__(self, value, freq):
        self.value = value
        self.freq = freq
        self.left = None
        self.right = None

    # overloading the less than sign for comparing the binary tree nodes in a heap
    def __lt__(self, other):
        return self.freq < other.freq

    # overloading the equal to sign
    def __eq__(self, other):
        return self.freq == other.freq

class HuffmanCoding:

    def __init__(self, file_path):
        self.file_path = file_path
        self.__heap = []
        self.__codes = {} # dict to store the codes of each character, eg: 'a' -> '101'
        self.__reverseCodes = {} # to store code and its character, eg: '101' -> 'a'

    # constructing a frequency dictionary for each character in the text
    def __make_freq_dict(self, text):
        freq_dict = {}
        for char in text:
            if char not in freq_dict:
                freq_dict[char] = 0
            freq_dict[char] += 1

        return freq_dict

    # constructing a min heap from the frequency dictionary
    def __buildHeap(self, freq_dict):
        for char, freq in freq_dict.items():
            bt_node = BinaryTreeNode(char, freq)
            heapq.heappush(self.__heap, bt_node)

    # constructing a binary tree from heap
    def __buildTree(self):
        while len(self.__heap) > 1:
            bt_node1 = heapq.heappop(self.__heap)
            bt_node2 = heapq.heappop(self.__heap)
            freq_sum = bt_node1.freq + bt_node2.freq
            newNode = BinaryTreeNode(None, freq_sum)
            newNode.left = bt_node1
            newNode.right = bt_node2
            heapq.heappush(self.__heap, newNode)
        return

    # to construct codes for each character through tree traversal
    def __buildCodesHelper(self, root, curr_bits):
        if root is None:
            return

        if root.value is not None:
            self.__codes[root.value] = curr_bits
            self.__reverseCodes[curr_bits] = root.value
            return

        self.__buildCodesHelper(root.left, curr_bits+'0')
        self.__buildCodesHelper(root.right, curr_bits+'1')

    def __buildCodes(self):
        root = heapq.heappop(self.__heap)
        self.__buildCodesHelper(root, "")

    def __getEncodedText(self, text):
        encoded_text = ""
        for char in text:
            encoded_text += self.__codes[char]
        return encoded_text

    # padding 0 in the encoded text, so that its length becomes a multiple of 8
    # this helps in easy conversion of the encoded text(which is a string) to bytes
    # also the binary value(8 bits) of the number of 0's padded is added in front of encoded text
    # this helps us to remove the padded 0's at the time of decoding
    def __getPaddedEncodedText(self, encoded_text):
        padded_amount = 8 - (len(encoded_text) % 8)
        encoded_text += padded_amount*'0'

        padded_info = "{0:08b}".format(padded_amount)
        padded_encoded_text = padded_info + encoded_text
        return padded_encoded_text

    # convert a sequence of 8 characters(representing 8 bits i.e 1 byte)
    # in the padded encoded text into integer and add these integers in an array
    def __getBytesArray(self, padded_encoded_text):
        arr = []
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            arr.append(int(byte, 2))

        return arr

    def compress(self):
        # read the text from the file
        # separating the file name and it's extension
        file_name, file_extension = os.path.splitext(self.file_path)
        # create the output compressed file path as <filename>.txt
        output_path = file_name + ".bin"

        with open(self.file_path, 'r+') as file, open(output_path, 'wb') as output:
            text = file.read()
            text = text.rstrip()

            freq_dict = self.__make_freq_dict(text)
            self.__buildHeap(freq_dict)
            self.__buildTree()
            self.__buildCodes()
            encoded_text = self.__getEncodedText(text)
            padded_encoded_text = self.__getPaddedEncodedText(encoded_text)
            bytes_arr = self.__getBytesArray(padded_encoded_text)

            final_bytes = bytes(bytes_arr)
            # write the binary file
            output.write(final_bytes)
        print("The file has been Compressed !!")
        # return this binary file as output
        return output_path

    # removing the 0's padded in the compressed file
    def __removePadding(self, text):
        padded_info = text[:8] # number of zeros present in the end
        extra_padding = int(padded_info, 2) # converting it to int

        text = text[8:]
        text_after_padding_removed = text[:-1*extra_padding]
        return text_after_padding_removed

    def __decodeText(self, text):
        decoded_text = ""
        current_bits = ""
        # iterate on each bit
        for bit in text:
            current_bits += bit
            # if a pattern is found add the character to the string and start searching for next pattern, else continue the search
            if current_bits in self.__reverseCodes:
                character = self.__reverseCodes[current_bits]
                decoded_text += character
                current_bits = ""
        return decoded_text

    def decompress(self, input_path):
        # separating the file name and it's extension
        filename, file_extension = os.path.splitext(self.file_path)
        # create the output decompressed file path as <filename>_decompressed.txt
        output_path = filename + "_decompressed" + ".txt"

        with open(input_path, 'rb') as file, open(output_path, 'w') as output:
            bit_string = ""
            byte = file.read(1) # read one byte at a time from the file
            # while the file is not empty
            while byte:
                byte = ord(byte) # converts the byte to it's corresponding ascii value(which is an int)
                bits = bin(byte)[2:].rjust(8,'0') # convert the int(eg: 5) to binary('0b101'), so [2:] is used to remove 0b
                # and rjust(8,'0') to make the length of string as 8 fill remaining places with '0'
                # now the final output will be '00000101'
                bit_string += bits # adding 8 bits to the string
                byte = file.read(1) # reading next byte
            actual_text = self.__removePadding(bit_string)
            decompressed_text = self.__decodeText(actual_text)
            output.write(decompressed_text)
        print("The file has been Decompressed !!")
        return


path = "sample.txt"
h = HuffmanCoding(path)
output_path = h.compress()
h.decompress(output_path)

print("The size of the file before compression:", os.stat('sample.txt').st_size, "bytes")
print("The size of the file after compression:", os.stat('sample.bin').st_size, "bytes")
print("The size of the file after decompression:", os.stat('sample_decompressed.txt').st_size, "bytes")
