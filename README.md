The idea here is to demonstrate Huffman Encoding Algorithm
to compress a text file in loss-less manner.

To compress a txt file
```
$ python huffman.py --compress <<somefile.txt>>
```

To decompress the file in .hfmn format
```
$ python huffman.py --decompress <<somefile.txt.hfmn>>
```

Note: 
	you can't decompress a compressed binary file.
So compress only text files and other human readable files