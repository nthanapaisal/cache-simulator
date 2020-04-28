# Cache Simulator: Computer Architecture (CS3853) at UT San Antonio
#
#   Written by: Supakjeera Thanapaisal, Kyle Becker, Joshua Garcia
#
# Purpose:
#   To simulate an internal operations of CPU caches which is a Level 1 cache for a 32-bit CPU, a 32-bit data bus.
#   The program is command line configurable to be direct-mapped, 2-way, 4-way, 8-way, or 16-way set associative 
#   and implement both roundrobin and random replacement policies for performance comparisons.
#
# Command line:
#
#	python3 cachesim.py -f Trace1.trc -s 1024 -b 16 -a 2 -r RR
#
#	python3 cachesim.py -s 1024 -b 16 -a 2 -r RR
#
# File:
#   cacheFunc.py - for this program functions
#   Trace1.trc - example trace file
#
#######################################################################################################################
#!/usr/bin/env python3

import math
import re
import sys
import os
import glob
import pprint
import random
import time
from cacheFunc import printHeaderArgs, printCacheCalcValues, calcNumBlocks, calcTagSize, \
    calcNumRows, calcOverhead, imMemory, costCalc, parseTraceFile, insert, overlap, \
    cacheBuilder, cpiCalc, hitRate, missRate, waste, printCacheSimResults, printCacheHitAndMiss, totalInstructions, hitMissCycles

    
if "-f" in sys.argv:
    iNumArgs = 11;
else:
    iNumArgs = 9;
    
if len(sys.argv) !=  iNumArgs:
	print("Incomplete Command Line Arguments: " + str(sys.argv))
	sys.exit(1)

#pop exe file
sys.argv.pop(0)

# parse each individual args
i = 0

# reads in command line arguments, parse file for addresses, and check for errors
while i < len(sys.argv):
	
    # setting arg to variables
	curArg = sys.argv[i]

	#checking if current arg is a file flag
	if curArg == "-f":
		traceFile = sys.argv[i+1]
		if not os.access("./" + sys.argv[i+1],os.F_OK):  
			print("ERROR: " + traceFile + " doesn't exists")
			sys.exit(2)
		cache = parseTraceFile(traceFile)
	#checking if current arg is a size tag
	elif curArg == "-s": 
		minSize = int(math.pow(2,10))
		maxSize = int(math.pow(2,23))
		cacheSize = int(sys.argv[i+1])
		cacheSizeBytes = int(cacheSize * minSize)
		if cacheSizeBytes > maxSize or cacheSizeBytes < minSize:
			print("ERROR: Invalid Cache Size")
			sys.exit(2)
	#checking if current arg is a byte size flag
	elif curArg == "-b":
		blockSize = int(sys.argv[i+1])
        
		if blockSize > 64 or blockSize < 4:
			print("ERROR: Invalid block Size")
			sys.exit(2)
        
	#checking if current arg is a associativity flag
	elif curArg == "-a":
		asso = [1,2,4,8,16]
		associateSize = int(sys.argv[i+1]) 
		if associateSize not in asso:
			print("ERROR: Invalid associateSize")
			sys.exit(2)
	#checking if current arg is a replacement policy flag
	elif curArg == "-r":
		replacementP = sys.argv[i+1]
		if replacementP == "RR":
			replacementP = "Round Robin"
		elif replacementP == "RND":
			replacementP = "Randomly Select"
		else:
			print("ERROR: Invalid replacement policy" + replacementP)
			sys.exit(2)
	else:
		i += 1
		continue  
	i += 1

# performs calculations for cache values
offsetBits = int(math.log2(blockSize))
numBlocks = calcNumBlocks(blockSize,cacheSizeBytes)
tagSize = calcTagSize(blockSize,cacheSizeBytes,associateSize,offsetBits)
numRows = calcNumRows(blockSize,cacheSizeBytes,associateSize)
indexSize = int(math.log2(numRows))
overHead = calcOverhead(numBlocks,tagSize)
impMemSize = imMemory(cacheSizeBytes,overHead)
impMemSizeKB = impMemSize / 1024
cost = costCalc(impMemSizeKB)

# print header, arguments, and calculated cache values
print("Cache Simulator - cs3853 - Team 02 \n")
if iNumArgs == 11:
	print("Trace File: " + traceFile + "\n")

#print 
printHeaderArgs(cacheSize, blockSize, associateSize, replacementP)
printCacheCalcValues(numBlocks,tagSize,indexSize,numRows,overHead,impMemSize,cost)

########################################### Milestone 2 ###############################################################
#   Purpose: 
#       To construct cache data structure which is a combination of dictionary and two dimensional list.
#   Notes:
#       This part of the program parse the tracefile into 4 parts (has to be non 000000000)
#       -   bytes read per address for instruction  
#       -   instruction address (2 clock cycles, n bytes read) 
#       -   source address (1 clock cycle + 4 bytes read )
#       -   desination address(1 clock cycle + 4  bytes read)
#   Algorithm:
#       1. build cache
#       2. parse file for addresses and instruction byte reads
#       3. convert address to binary and slice them into specifed (tag,index,offset) bits then convert to decimal (easier for human debug)
#       4. access(loop) the cache at that index check if that address already in cache and if it's overlap (if overlap insert to other indexes)
#       5. else (loop) again to check for the first empty spot (compolsory miss), insert, and if it's overlap (if overlap insert to other indexes)
#       6. else means it's full, start the RR or RND operation then check if it's overlap (if overlap insert to other indexes)
#######################################################################################################################
#useful globals
hitCount = 0
missCount = 0
conflictMiss = 0
compulsoryMiss = 0
totalCacheAccess = 0
rrReminder = 0
totalCycles = 0
addressList = list()
rrDict = {}

#create cache data structure: dictionary with list of list as a value
cacheDict = cacheBuilder(numRows, associateSize)

#only apply when trace file exists
if iNumArgs == 11:
    
    #regex for two different lines in trace file
    regexEIP = re.compile('EIP \((\d{2})\): (\w{8})')
    regexDstSrc = re.compile(r'dstM:\s(\w{8}).{13}srcM:\s(\w{8}).*')
    
    #loop each line, when meet an empty line map the addresses in the list (addressList)
    with open(traceFile, 'r') as t:
    
        for line in t:
            
            #check if line not empty, insert address in the list based on the type
            if line not in ['\n', '\r\n']:
            
                #regex for two different lines
                fetchEIP = regexEIP.search(line.rstrip())
                matchDstSrc = regexDstSrc.search(line.rstrip())

                # dest and src line
                if matchDstSrc is not None:
                    dstAddress = matchDstSrc.group(1)
                    srcAddress = matchDstSrc.group(2)
                    
                    #count number of cycles
                    if dstAddress != '00000000' and srcAddress != '00000000':
                        totalCycles += 2
                        
                    elif dstAddress != '00000000' or srcAddress != '00000000':
                        totalCycles += 1
                        
                    #add to the list
                    addressList.append(dstAddress)
                    addressList.append(srcAddress)
                    
    	        # instruction line
                if fetchEIP is not None:
                
                    #get instruction length (bytes read) and address
                    instructionLength = int(fetchEIP.group(1))
                    instructionAddress = hex(int(fetchEIP.group(2),16))
                    
                    #count cycle (2 for instruction)
                    totalCycles += 2
                    
                    #add to the list
                    addressList.append(instructionAddress)
            else: 
                
                for i in range(0,len(addressList)):
                    
                    #if empty ignroe this address
                    if addressList[i] == "00000000":
                        continue
                    
                    # make sure instructionLength (bytes read) for dest and src are 4
                    if (i == 1) or (i == 2):
                        instructionLength = 4
                    
                    #set vars
                    biLen = 32
                    iMatch = 0
                    totalCacheAccess += 1
                    
                    #convert address to binary
                    biAddress = "{0:032b}".format(int(addressList[i],16))
                    
                    #parse offset,index, tag
                    biOffset = biAddress[-offsetBits:]
                    biIndex = biAddress[-offsetBits-indexSize:-offsetBits]
                    biTag = biAddress[:-offsetBits-indexSize]
                    
                    #convert to decimal
                    if biIndex != '':
                        iIndex = int(biIndex,2)
                    else:
                        iIndex = 0
                    iOffset = int(biOffset,2)
                    iTag = int(biTag,2)
                  
                    #check if overlap
                    iOverlap = overlap(blockSize, iOffset, int(instructionLength))
                    
                    #check valid, map, and count
                    blockList = cacheDict[iIndex]
                     
                    #loop through each blocks of that index and check if the tag already exists
                    for g in range(0,associateSize):
                       
                        #assign each block with its info into blockInfoList
                        blockInfoList = blockList[g]
                        
                        #check if its valid and tag already exists
                        if blockInfoList[0] == "1":
                            
                            if blockInfoList[1] == iTag:
                                           
                                iMatch = 1
                                hitCount += 1
                                
                                if iOverlap > 0:
                                    
                                    iNewIndex = iIndex + 1                      
                                    
                                    #overlap then insert at specify
                                    while iOverlap > 0:
                                        
                                        #pass max cachesize
                                        if iNewIndex >= numRows:
                                            iNewIndex = 0
                                        
                                        newBlocklist = cacheDict[iNewIndex]
                                        
                                        #####################################
                                        blockInfoList = newBlocklist[g]
                                        
                                        if blockInfoList[0] == "1":
                                        
                                           if blockInfoList[1] == iTag:
                                                hitCount += 1
                                                
                                           else:
                                                missCount += 1
                                                conflictMiss += 1
                                                   
                                        else:
                                            missCount += 1
                                            compulsoryMiss += 1

                                        #insert new info into that block
                                        newBlocklist = insert(g,cacheDict[iNewIndex],iTag)
                                        #reset block list
                                        cacheDict[iNewIndex] = newBlocklist    
                                            
                                        #####################################
                                        #increment to next index and decrease overlap
                                        iNewIndex += 1
                                        iOverlap -= 1
                                        totalCacheAccess += 1
                                    
                                break

                            
                    #not found -> find a place to put it
                    if iMatch == 0:
                        missCount += 1 
                        compulsoryMiss += 1
                        
                        for p in range(0,associateSize):
                               
                            #assign each block with its info into blockInfoList
                            
                            blockInfoList = blockList[p]    
                            if blockInfoList[0] == 'v':
                                
                                #insert new info into that block
                                newBlocklist = insert(p,cacheDict[iIndex],iTag)
                                cacheDict[iIndex] = newBlocklist
                                iMatch = 1
                                
                                #overlap then insert specify
                                if iOverlap > 0:
                                    iMatch = 1
                                    iNewIndex = iIndex + 1
                                    #overlap then insert at specify
                                    while iOverlap > 0:
                                    
                                        if iNewIndex >= numRows:
                                            iNewIndex = 0
                                                
                                        newBlocklist = cacheDict[iNewIndex]
                                        
                                        #####################################
                                        blockInfoList = newBlocklist[g]
                                        
                                        if blockInfoList[0] == "1":
                                        
                                           if blockInfoList[1] == iTag:
                                                hitCount += 1
                                                
                                           else:
                                                missCount += 1
                                                conflictMiss += 1
                                                
                                                
                                        else:
                                            missCount += 1
                                            compulsoryMiss += 1
                                          
                                        #insert new info into that block
                                        
                                        newBlocklist = insert(g,cacheDict[iNewIndex],iTag)
                                        #reset block list
                                        cacheDict[iNewIndex] = newBlocklist    
                                            
                                        #####################################
                                        
                                        #increment to next index and decrease overlap
                                        iNewIndex += 1
                                        iOverlap -= 1 
                                        totalCacheAccess += 1
                                    
                                break    
                            
                                
                    #no place to put it 
                    if iMatch == 0:
                        conflictMiss += 1
                        compulsoryMiss -= 1
                        
                        if replacementP == 'Randomly Select':
                        
                            k = random.randrange(associateSize)
                            newList = insert(k, cacheDict[iIndex], iTag)
                            cacheDict[iIndex] = newList
                            
                            if iOverlap > 0:
                               
                                iNewIndex = iIndex+1
                                    
                                #overlap then insert at specify
                                while iOverlap > 0:
                                    
                                    if iNewIndex >= numRows:
                                        iNewIndex = 0
                                        
                                    newBlocklist = cacheDict[iNewIndex]
                                        
                                    #####################################
                                    blockInfoList = newBlocklist[g]
                                        
                                    if blockInfoList[0] == "1":
                                        
                                        if blockInfoList[1] == iTag:
                                            hitCount += 1
                                            
                                        else:
                                            missCount += 1
                                            conflictMiss += 1
                                            
                                                
                                    else:
                                        missCount += 1
                                        compulsoryMiss += 1
                                        
                                    #insert new info into that block
                                        
                                    newBlocklist = insert(g,cacheDict[iNewIndex],iTag)
                                    #reset block list
                                    cacheDict[iNewIndex] = newBlocklist    
                                            
                                    #####################################
                                    #increment to next index and decrease overlap
                                    iNewIndex += 1
                                    iOverlap -= 1    
                                    totalCacheAccess += 1
                                            
                            
                            
                            
                        if replacementP == 'Round Robin':
                        
                            if iIndex in rrDict:
                                rrReminder = rrDict[iIndex]
                                rrDict[iIndex] += 1
                            else: 
                                rrDict[iIndex] = 0
                                rrReminder = rrDict[iIndex]
                                rrDict[iIndex] += 1
                                
                            #rrReminder = 0 on first go
                            for block in range(0, associateSize):
                            
                                if rrReminder == (associateSize):
                                    rrReminder = 0
                                    rrDict[iIndex] = 0
                                    
                                if block == rrReminder:
                                    newList = insert(rrReminder, cacheDict[iIndex], iTag)
                                    cacheDict[iIndex] = newList
                                    rrReminder += 1
                                
                                    if iOverlap > 0:
                                        
                                        iNewIndex = iIndex + 1
                                        
                                        #overlap then insert at specify
                                        while iOverlap > 0:
                                            
                                            if iNewIndex >= numRows:
                                                iNewIndex = 0
                                            
                                            
                                            newBlocklist = cacheDict[iNewIndex]
                                            
                                            #####################################
                                            blockInfoList = newBlocklist[g]
                                            
                                            if blockInfoList[0] == "1":
                                            
                                               if blockInfoList[1] == iTag:
                                                    hitCount += 1
                                                    
                                               else:
                                                    missCount += 1
                                                    conflictMiss += 1
                                                    
                                                    
                                            else:
                                                missCount += 1
                                                compulsoryMiss += 1
                                                
                                            #insert new info into that block
                                            
                                            newBlocklist = insert(g,cacheDict[iNewIndex],iTag)
                                            #reset block list
                                            cacheDict[iNewIndex] = newBlocklist    
                                                
                                            #####################################
                                            #increment to next index and decrease overlap
                                            iNewIndex += 1
                                            iOverlap -= 1
                                            totalCacheAccess += 1
                                    break
                addressList.clear()

    
    #pprint.pprint(cacheDict,width=50)
    numOfInstructions = totalInstructions(traceFile)
    totalCycles = totalCycles + hitMissCycles(hitCount,missCount,blockSize)
    cpi = cpiCalc(totalCycles, numOfInstructions)
    hitRate = hitRate(hitCount, totalCacheAccess)
    missRate = missRate(hitRate)
    over = tagSize + 1
    waste, unusedKB = waste(numBlocks, compulsoryMiss, blockSize, over, impMemSize)
    #printing output
    printCacheSimResults(totalCacheAccess, hitCount, missCount, compulsoryMiss, conflictMiss)
    printCacheHitAndMiss(hitRate, missRate, cpi, unusedKB, impMemSize, waste, numBlocks, compulsoryMiss)
   
    