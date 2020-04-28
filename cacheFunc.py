#!/usr/bin/env python3

import math
import re
import sys
import os
import glob
import pprint
import random
import time

# printHeaderArgs
#   Parameters:
#	   blockSize   - size of a block in bytes
#	   cacheSize   - size of the cache in bytes
#	   assoc	   - Associativity
#      rPolicy  - replacement policy
#   Returns:
#	   n/a
def printHeaderArgs(cacheSize, blockSize, assoc, rPolicy):
	print("***** Cache Input Parameters ***** \n")
	print("Cache Size: " + str(cacheSize) + " KB")
	print("Block Size: " + str(blockSize) + " bytes")
	print("Associativity: " + str(assoc))
	print("Replacement Policy: " + rPolicy + "\n")

# printCacheCalcValues
#   Parameters:
#	   numBlocks   -	number of blocks
#	   tagSize   -	size of tag in bits
#	   indexSize   - size of index iu bits
#	   numRows   - number of rows
#	   overheadSize	   - overHead size in bytes
#      impMemSize  - implementation memory size
#      cost  - cost of cache
#   Returns:
#	   n/a
def printCacheCalcValues(numBlocks, tagSize, indexSize, numRows, overheadSize, impMemSize, cost):
	print("***** Cache Calculate Values *****\n")
	#PRINT TOTAL # BLOCKS:				numBlocks
	print("Total # Blocks: " + str(numBlocks))
	#PRINT TAG SIZE:					  tagSize
	print("Tag Size: " + str(tagSize) + " bits")
	#PRINT INDEX SIZE:					indexSize, numRows
	print("Index Size: " + str(indexSize) + " bits")
	#PRINT TOTAL # ROWS:				  numRows
	print("Total # Rows: " + str(numRows))
	#PRINT OVERHEAD SIZE:				 overheadSize
	print("Overhead  Size: " + str(overheadSize) + " bytes")
	#PRINT IMPLEMENTATION MEMORY SIZE:	impMemSize
	print("Implementation Memory Size: %.2f" % (impMemSize/1024)  +" KB (" + str(impMemSize) + " bytes)")
	#COST:	cost						  
	print("Cost: $%.2f \n" % cost)
	
def printCacheSimResults(totalCacheAccesses, hits, misses, compulsoryMisses, conflictMisses):
	print("***** Cache Simulation Results *****\n")
	print("Total Cache Accesses:   " + str(totalCacheAccesses))
	print("Cache Hits:             " + str(hits))
	print("Cache Misses:           " + str(misses))
	print("--- Compulsory Misses:     " + str(compulsoryMisses))
	print("--- Conflict Misses:       " + str(conflictMisses) + "\n")

# printCacheHitAndMiss
#   Parameters:
#	     hitRate -	hit rate
#	     missRate -	miss rate
#	     cpi - calculated cpi value
#	     unusedKB - unused KB out of total
#	   	 implementationMemSize  - implementation memory size
#        waste - waste in dollars
#        totalBlocks - total cache blocks
#		 compulsoryMisses - number of compulsory Misses
#   Returns:
#	   n/a	
def printCacheHitAndMiss(hitRate, missRate, cpi, unusedKB, implementationMemSize, waste, totalBlocks, compulsoryMisses):
	print("***** *****  CACHE HIT & MISS RATE:  ***** *****\n")
	print("Hit  Rate:              " + str(round(hitRate, 4)) + "%")
	print("Miss Rate:              " + str(round(missRate, 4)) + "%")
	print("CPI:                    " + str(round(cpi, 2)) + " Cycles/Instruction")
	print("Unused Cache Space:     " + str(round(unusedKB, 2)) + " KB / " + str(implementationMemSize/1024) + " KB = " + str(round((unusedKB / (implementationMemSize / 1014)*100), 4)) + "%  Waste: $" + str(round(waste, 2)))
	print("Unused Cache Blocks:    " + str((totalBlocks - compulsoryMisses)) + " / " + str(totalBlocks))

# calcNumBlocks
#   Parameters:
#	   blockSize   - size of a block in bytes
#	   cacheSize   - size of the cache in bytes
#   Returns:
#	   numBlocks	 - number of blocks
def calcNumBlocks(blockSize,cacheSize): 
    
    numBlocks = int(cacheSize / blockSize)
    
    return numBlocks

# calcTagSize
#   Parameters:
#	   blockSize   - size of a block in bytes
#	   cacheSize   - size of the cache in bytes
#	   assoc	   - Associativity
#      offsetBits  - block offset in bits
#   Returns:
#	   bitsTag	 - Size of the tag in bits
def calcTagSize(blockSize, cacheSize, assoc,offsetBits):

	bitsIndex = int(math.log2(calcNumRows(blockSize, cacheSize, assoc)))
	bitsTag = 32 - offsetBits - bitsIndex
    
	return bitsTag

# calcNumRows
#   Parameters:
#	   blockSize   - size of a block in bytes
#	   cacheSize   - Size of the cache in bytes
#	   assoc	   - Associativity
#   Returns:
#	   numRows	 - Total # of rows
#   Notes: 
#	   math.log2() this function to get the index size in bits
def calcNumRows(blockSize, cacheSize, assoc):

	if blockSize <= 0 or assoc <= 0:
		print('<INPUT ERROR> blockSize and Association must be larger than 0')
		sys.exit()
	numRows = int(cacheSize / (blockSize * assoc))
    
	return numRows

# calcOverhead
#   Parameters:
#	   totalBlock   - number of all blocks
#	   tagSize	  - number of bits for tag
#   Returns:
#	   overHead	 - overhead in bytes
def calcOverhead(totalBlock,tagSize): 

	tagValid = int(1 + tagSize)
	top = int(tagValid * totalBlock)
	overHead = int(top / 8)
    
	return overHead


# imMemory
#   Parameters:
#	   cacheSize	- cache size in bytes
#	   overHead	    - overhead in bytes
#   Returns:
#	   memorySize   - total memory size in bytes
def imMemory(cacheSize, overHead):

	memorySize = int(cacheSize + overHead)
    
	return memorySize


# costCalc
#   Parameters:
#	   memorySize   - total memory size in KB
#   Returns:
#	   cost		 - total cost for total memory size
#   Notes:
#	   each KB is $0.05
#calculate cost
def costCalc(memorySize):

	cost = float(memorySize * 0.05)
    
	return round(cost,2)

# cpiCalc
#   Parameters:
#	   cycles   - total num of cycles
#	   numOfInstructions - total number of instructions
#   Returns:
#	   cpi		 
#   Notes:
#	  
def cpiCalc(cycles, numOfInstructions):
	
	cpi = cycles/numOfInstructions
	return cpi

# hitRate
#   Parameters:
#	   hits   - total num of hits
#	   totalAccesses - total num of accesses
#   Returns:
#	   hitRate		 
#   Notes:
#	  
def hitRate(hits, totalAccesses):
	hitRate = (hits * 100) / totalAccesses
    
	return hitRate

# missRate
#   Parameters:
#	   hitRate - rate we get hits
#   Returns:
#	   missRate		 
#   Notes:
#	  
def missRate(hitRate):
	
	missRate = 1 - (hitRate / 100)
	return missRate * 100

# waste
#   Parameters:
#	     cost - cost of this sim
#	     totalBlocks -	total num of blocks
#	     compulsoryMisses - misses when not valid
#	     blockSize - blockSize in bytes
#	   	 overHeadSize  - overHeadSize in bytes
#        implementationMemSize - implementation memory size
#   Returns:
#	   returns waste and unusedKB	
def waste(totalBlocks, compulsoryMisses, blockSize, overHeadSize, implementationMemSize):
    implementationMemSize = implementationMemSize * 1024
    bitBlock = blockSize * 8
    blockOverSize = bitBlock + overHeadSize
    unusedKB = ( (totalBlocks - compulsoryMisses) * (blockOverSize / 8) ) / 1024
    return (.05 * unusedKB) , unusedKB

# parseTraceFile
#   Parameters:
#	   traceFile - trace file to be parsed
#   Returns:
#	   cache - Dictionary containing hex address as key and instruction fetch length as value
#   Notes:
#	   Only stores first 20 lines, remove after M1, to do this just delete the counter variables
#	   Does not account for duplicate keys, need to change after M1
def parseTraceFile(traceFile):

	regexLine = re.compile('EIP \((\d{2})\): (\w{8})')
    
	cache = {}

	counter = 0
	with open(traceFile, 'r') as t:
		for line in t:
			
			# if the line is empty, ignore it
			if line.rstrip() != '':
				fetchMatch = regexLine.search(line.rstrip())
				
				# if the regex matched
				if fetchMatch is not None:
					instructionLength = fetchMatch.group(1)
					hexAddress = hex(int(fetchMatch.group(2), base=16))
					# if the hex address and instruction fetch length are valid
					if hexAddress != 0 and int(fetchMatch.group(1)) != 0:
						# to include a zero at the beginning of the hex address (NOT THE 0x)
						if len(str(hexAddress)) < 10:
							strHexAddress = str(hexAddress)
							hexAddress = strHexAddress[:2] + '0' + strHexAddress[2:]
							cache[hexAddress] = fetchMatch.group(1)

						cache[str(hexAddress)] = fetchMatch.group(1)
	return cache


# insert
#   Parameters:
#	   iBlockSubscript - subscript
# 	   blockList - list of blocks
#	   iTag - tag for the block
#   Returns:
#	   blockList
#   Notes:
def insert(iBlockSubscript, blockList,iTag):
    
    #loop through each blocks of that index and check if the tag already exists
    for i in range(0,len(blockList)):
           
        #assign each block with its info into blockInfoList
        if i == iBlockSubscript:
            blockInfoList = blockList[i]
            blockInfoList[0] = '1'
            blockInfoList[1] = iTag
            blockList[i] = blockInfoList
            return blockList
    return   
# overLap
#   Parameters:
#	   blockSize - size of blocks
# 	   offset - 
#	   bytesToRead - num of bytes to read
#   Returns:
#	   overLap
#   Notes:
def overlap(blockSize, offset, bytesToRead):
    if type(blockSize) != int:
        print('Blocksize is invalid type, returned: ' + str(type(blockSize)))
    if type(offset) != int:
        print('Offset is invalid type, returned: ' + str(type(offset)))
    if type(bytesToRead) != int:
        print('BytesToRead is invalid type, returned: ' + str(type(bytesToRead)))
    bytesRemaining = int(blockSize - offset)
    bytesRead = int(bytesToRead - bytesRemaining)
    overlapBy = math.ceil(bytesRead/blockSize)

    if(overlapBy > 0):
        return(overlapBy)
    else:
        return(0)
        
# cacheBuilder
#   Parameters:
#	   numRows - number of rows
# 	   associativity - type of associativity
#   Returns:
#	   cacheDict
#   Notes:       
def cacheBuilder(numRows, associativity):
    cacheDict=dict()
    for row in range(0, numRows):
        bigList = []
        for blocks in range (0, associativity):
            miniList = ['v', '00000000']
            bigList.append(miniList)
        cacheDict[row] = bigList

    return cacheDict
    
# totalInstructions
#   Parameters:
#	   traceFile - traceFile to check
#   Returns:
#	   count of instructions
#   Notes:  
def totalInstructions(traceFile):
    iCount = 0
    with open(traceFile, 'r') as traceFile:
        for line in traceFile:
            iCount += 1
    instructionCount = iCount // 3
    return(instructionCount)

# hitMissCycles
#   Parameters:
#	   hit - number of hits
#	   miss - number of misses
#   Returns:
#	   hitmissCycles
#   Notes:     
def hitMissCycles(hit, miss, blockSize):
	hitmissCycle = 0
	numReads = math.ceil(blockSize / 4)
	hitmissCycle += hit
	hitmissCycle += miss * (3 * numReads)
	return hitmissCycle
	