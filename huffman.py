import argparse, re, math, sys, time, os

class HuffmanNode:
	"""
			Node Object that supports Merging operation as in the
		Huffman Encoding Algorithm.

		self.alphabet: list of characters at a node which share
			a common ancestors in the Huffman Tree.
		self.count: number of times the element in the list of
			characters have occured. Used for statistical purpose
			while Merging

		Example:
		>>> import huffman.HuffmanNode as HN
		>>> hn1 = HN(['A','B'],100)
		>>> hn2 = HN(['C'],200)
		>>> hn3 = hn1.merge(hn2)
		>>> hn3
		HuffmanNode(['A', 'B', 'C']|300)		
	"""
	def __init__(self, alphabet,count):
		"Create an HuffmanNode() Object"
		self.alphabet = alphabet
		self.count = count

	def merge(self, other):
		"""
				Merge two HuffmanNode() and return the newly created
			HuffmanNode() which has all the element of the two nodes 
			self and other, with count being sum of their counts.
		"""
		alphabet = self.alphabet + other.alphabet
		count = self.count + other.count
		return HuffmanNode(alphabet,count)

	def __repr__(self):
		"Returns string representation of an HuffmanNode() Object"
		return "HuffmanNode("+str(self.alphabet)\
			+"|"+str(self.count)+")"

class Huffman:
	r"""
		The main class that does Compression and Decompression.

		The flow chart below shows how Compression is done.

						+---------------+
						|               |
						|  Input File   |
						|               |
						+---------------+
								|
				/---------------^--------------\
				|				  			   |
				v                              v
		+------------------+ 	  	+------------------+
		|                  | 	  	|                  |
		|   Huffman Code   |------->|    Encoded Bytes |
		|                  | 	  	|                  |
		+------------------+ 	  	+------------------+
				|                              |
				|				  			   |
				v                              v
		+------------------+ 	  	+------------------+
		|                  | 	  	|                  |
		|     Metadata     | 	  	|    Packed Bytes  |
		|   (Code Table)   | 	  	|     (Payload)    |
		|                  | 	  	|                  |
		+------------------+ 	  	+------------------+
				|                              |
				\---------------v--------------/
								|
								|
								V
						+---------------+
						|               |
						|  Outfil File  |
						|  (Frame Dump) |
						|               |
						+---------------+

		1.File in read and the file stream is used to generate
			Huffman Code Table
		Documentation under progress...

		In Short: The procedure follow in Decompression is as 
			shown above in the flow chart except that it flows 
			in the reverse direction

	"""
	def __init__(self,text = None):

		self.text = text
		self.code = self.generate_huffman_code()

	def generate_huffman_code(self):
		
		if not self.text:
			return

		set_of_unique_chars = set(self.text)
		nodes = []
		code = {}
		
		for char in set_of_unique_chars:
			nodes.append(HuffmanNode([char],self.text.count(char)))
			code[char] = ""

		while len(nodes) > 1:
			
			nodes = sorted(nodes,reverse = True, key = lambda ht: ht.count)
			last_node = nodes.pop()
			last_second_node = nodes.pop()
			
			for char in last_second_node.alphabet:
				code[char] += "0"
			
			for char in last_node.alphabet:
				code[char] += "1"
			
			new_node = last_second_node.merge(last_node)
			nodes.append(new_node)

		for k, v in code.items():
			code[k] = v[::-1]

		return code
		

	def decode(self, string):
		
		print "Decoding bit stream..."
		regex = "|".join(("(" + bit + ")" for bit in self.code.values()))
		inverse_code = {}
		decoded_string = []

		for char, bit in self.code.items():
			inverse_code[bit] = char

		delta = 100
		chunk_ptr = delta #chunk stride
		chunk = string[0:delta]
		
		stream_len = len(string)
		stream_len_by_100 = stream_len / 100
		stream = 0
		percentage_complete = 0

		while chunk:
			mo = re.match(regex,chunk)
			if mo:
				match = mo.group()
				chunk = chunk[len(match):]

				if len(chunk) < 20:
					if chunk_ptr+delta > len(string):
						chunk += string[chunk_ptr:]
					else:
						chunk += string[chunk_ptr:chunk_ptr+delta]
					chunk_ptr += delta

					if chunk_ptr > stream:
						self.print_progress_bar(percentage_complete)
						percentage_complete += 1
						stream += stream_len_by_100

				decoded_string.append(inverse_code[match])
			else:
				print """
				[ERROR]: Matching error, Unable to process the file. 
					File format not supported or File may be corrupt!!
					File should in valid format as defined HFMN standards,
					with file extension .hfmn.
				"""
				exit()

		sys.stdout.write("\n")

		return "".join(decoded_string)

	def print_progress_bar(self,percentage_complete):

		columns = 40
		steps = int(percentage_complete * float(columns) / 100)

		if percentage_complete > 100:
			percentage_complete = 100
		sys.stdout.write("\r[" + "=" * steps + ">" + \
			" " * ( columns - steps ) + "] " + \
			str(percentage_complete) +"%")
		sys.stdout.flush()

	def encode(self, string = None):

		if not string:
			string = self.text

		code_list = [self.code[char] for char in string]
		code_string = "".join(code_list)

		self.code_string = code_string
		return code_string

	def pack(self, string):

		packed = [chr(8 - len(string) % 8)]
		if len(string) % 8 != 0:
			string += "0" * (8 - len(string) % 8)

		for i in range(0,len(string),8):
			byte = string[i:i+8]
			packed.append(chr(int(byte,2)))

		return "".join(packed)

	def unpack(self, string):

		padding = ord(string[0])
		string = string[1:]
		unpacked = []

		for byte in string:
			byte = bin(ord(byte))
			byte = byte[2:]
			byte = "0" * (8 - len(byte)) + byte
			unpacked.append(byte)

		return "".join(unpacked)[:-padding]

	def make_metadata(self):
		
		if len(self.code) == 256:
			len_code = 0
		else:
			len_code = len(self.code)

		metadata = "HFMN" + chr(len_code)

		for char, bits in self.code.items():
			size = chr(len(bits))
			if len(bits) % 8 != 0:
				bits += "0" * (8 - len(bits) % 8)

			packed = []

			for i in range(0,len(bits),8):
				byte = bits[i:i+8]
				packed.append(chr(int(byte,2)))

			packed = "".join(packed)
			metadata += char + size + packed

		return metadata

	def process_metadata(self,metadata):

		if metadata[0:4] != "HFMN": #the magic number of my file format
			print "[ERROR]: In parsing metadata, file format invalid!!"
			exit()

		code_len = ord(metadata[4])
		if code_len == 0:
			code_len = 256

		pointer = 5
		code = {}
		
		for i in range(code_len):
			
			char = metadata[pointer]
			size = ord(metadata[pointer + 1])
			delta = int(math.ceil(float(size) / 8))
			bits = []

			for j in range(delta): 
				byte = bin(ord(metadata[pointer + 2 + j]))[2:] 
				byte = "0" * (8 - len(byte)) + byte
				bits.append(byte)

			bits = "".join(bits)[:size]
			code[char] = bits
			pointer += 2 + delta

		return code,pointer 


	def compress_file(self, filename, outfile):
		
		tic = time.time()
		print "Begining Compression using Huffman Encoding Algorithm..."
		
		self.text = open(filename,'r').read()
		self.code = self.generate_huffman_code()
		payload = self.pack(self.encode())
		metadata = self.make_metadata()
		frame = metadata + payload
		open(outfile,'wb').write(frame)
		
		print "[DONE]: Time Elapsed: %f seconds" % (time.time() - tic)
		print "\tSaved the compressed file as %s" % outfile
		print "\tCompressed %.2f KB to %.2f KB " % \
			(float(len(self.text)) / 1024.0, float(len(frame)) / 1024.0)
		print "\tCompression ratio: %.4f" % \
			( float(len(self.text)) / float(len(frame)))


	def decompress_file(self, filename, outfile):
		
		tic = time.time()
		print "Begining Decompression using Huffman Encoding Algorithm..."
		
		contents = open(filename,'r').read()
		self.code, pointer = self.process_metadata(contents)
		contents = contents[pointer:]
		original_contents = self.decode(self.unpack(contents))
		open(outfile,'wb').write(original_contents)
		
		print "[DONE]: Time Elapsed: %f seconds" % (time.time() - tic)
		print "\tSaved the decompressed file as %s" % outfile
		print "\tDecompressed %.2f KB to %.2f KB" % \
			(float(os.path.getsize(filename)) / 1024.0,
			float(os.path.getsize(outfile)) / 1024.0)
		print "\tCompression Ratio: %.4f" % (float(os.path.getsize(outfile)) /\
			float(os.path.getsize(filename))) 

def main():


	parser = argparse.ArgumentParser(
		description="""
			Compress and Decompress a text file, using
			Huffman Encoding Algorithm. Use -c xor -d.

	""", formatter_class=argparse.RawTextHelpFormatter)

	parser.add_argument('-c', '--compress', nargs=1,
						help='compress a file\n'
							 'Usages: \n'
							 '--compress <filename>\n')

	parser.add_argument('-d', '--decompress', nargs=1,
						help='decompress a file\n'
							 'Usages: \n'
							 '--decompress <filename>\n')

	args = parser.parse_args()

	huffman = Huffman()

	if args.compress:
		if os.path.isfile(args.compress[0]):
			huffman.compress_file(args.compress[0],args.compress[0]+".hfmn")
		else:
			print "[ERROR]: File %s not found." % args.compress[0]
	
	elif args.decompress:
		if os.path.isfile(args.decompress[0]):
			outfile = os.path.splitext(args.decompress[0])[0]
			outfile = os.path.splitext(outfile)
			outfile = outfile[0] + "_decompressed" + outfile[1]

			huffman.decompress_file(args.decompress[0],outfile)
		else:
			print "[ERROR]: File %s not found." % args.decompress[0]

	else:
		print """
			Try: 

			$ python huffman.py --help
				
			---------------- OR TRY ---------------

			$ python huffman.py -c small.txt 
					AND THEN TRY 
			$ python huffman.py -d small.txt.hfmn
		"""

if __name__ == '__main__':
	main()