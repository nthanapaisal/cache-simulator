- Cache Simulator: Computer Architecture (CS3853) at UT San Antonio

   Written by: Supakjeera Thanapaisal, Kyle Becker, Joshua Garcia

- Purpose:
   To simulate an internal operations of CPU caches which is a Level 1 cache for a 32-bit CPU, a 32-bit data bus.
   The program is command line configurable to be direct-mapped, 2-way, 4-way, 8-way, or 16-way set associative 
   and implement both roundrobin and random replacement policies for performance comparisons.

- Command line:

	python3 cachesim.py -f Trace1.trc -s 1024 -b 16 -a 2 -r RR

	python3 cachesim.py -s 1024 -b 16 -a 2 -r RR

- Files:
   cachesim.py - main program
   cacheFunc.py - for this program functions
   Trace1.trc - example trace file
- Switches:
  1. –f <trace file name> [ name of text file with the trace ] 
  2. –s <cache size in KB> [ 1 KB to 8 MB ] 
  3. –b <block size>  [ 4 bytes to 64 bytes ] 
  4. –a <associativity>   [ 1, 2, 4, 8, 16 ] 
  5. –r <replacement policy> [ RR or RND ]
