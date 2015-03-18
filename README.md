
An non-Pythonic implementation of gSpan

This is based off of the gSpan implementaiton found here:

https://github.com/Jokeren/DataMining-gSpan

This is not how you would write gspan in python. It is
some scratch code I'm writing as an experiment to help me
understand gspan better to write a C implementation.

This code is currently BROKEN in that it, compared to the 
original C++ implementation, it misses a few subgraphs.
I'm not entirely sure why. It may have something to do
with ordering of the DFS codes between C++ maps and unordered
python dicts sorted by key.


DO NOT USE.



