import sys
import os

Notes = ("E", "F", "Gb", "G", "Ab", "A", "Bb", "B", "C", "Db", "D", "Eb")	#All musical notes
AllPossibleNotes = ("E", "F", ("Gb", "F#"), "G", ("Ab", "G#"), "A", ("Bb", "A#"), "B", "C", ("Db", "C#"), "D", ("Eb", "D#"))	#All musical notes

DroppedD = [36, 31, 27, 22, 17, 10]			#Number representation of where the note is relative the lowest possible note (One octave below bottom E)
StandardE = [36, 31, 27, 22, 17, 12]		#Strings are shown from "bottom" up
StandardC = [32, 27, 23, 18, 13, 8]

def findTuning(fileR):
	DDcnt = 0								#No. of DroppedD matched strings
	SEcnt = 0								#No. of StandardE matched strings
	SCcnt = 0								#No. of StandardC matched strings
	position = 0							#position of string

	for line in fileR:
		if(line.startswith(Notes)):							#If the line starts with a note (implies tuning)
			if(Notes[DroppedD[position]%12].rstrip() == line.split('|')[0].rstrip()):	#If the line starts with the correct note for Dropped D
				DDcnt = DDcnt + 1
			if(Notes[StandardE[position]%12].rstrip() == line.split('|')[0].rstrip()):	#If the line starts with the correct note for Standard E
				SEcnt = SEcnt + 1
			if(Notes[StandardC[position]%12].rstrip() == line.split('|')[0].rstrip()):	#If the line starts with the correct note for Standard C
				SCcnt = SCcnt + 1
			position = position + 1
			if(position == 6):
				position = 0
				break

	if(SEcnt >= 6):
		print "Standard E Tuning found"
		matchedTuning = StandardE
	elif(DDcnt >= 6):
		print "Dropped D Tuning found"
		matchedTuning = DroppedD
	elif(SCcnt >= 6):
		print "Standard C Tuning found"
		matchedTuning = StandardC
	else:
		print "Tuning Not Correctly Matched"
		sys.exit()
	
	return matchedTuning

'''Start of Script'''

'''TODO
		Fix Negatives on the tab
			**Move to different string?
			**What if below lowest string or higher than highest?
		Make sure shifted notes stay aligned from the 1 digit numbers becoming two or vice versa
		Eliminate certain string lines from getting bigger than others
		DONE FOR NOW - Look out for mixed in Bass tabs / Lines that happen to start with a note that is not a tab
'''

if(len(sys.argv) < 3):
	print "Usage: python ShiftTuning.py <OrignalTab.utab> <Desired Tuning>"
	sys.exit()

if(not os.path.isfile(sys.argv[1])):
	print "Input file not recognized!"
	print "Usage: python ShiftTuning.py <OrignalTab.utab> <Desired Tuning>"
	sys.exit()

if(sys.argv[2] == "StandardE"):
	desiredTuning = StandardE
elif(sys.argv[2] == "DroppedD"):
	desiredTuning = DroppedD
elif(sys.argv[2] == "StandardC"):
	desiredTuning = StandardC
else:
	print "Not a recognized desired tuning!"
	print "Usage: python ShiftTuning.py <OrignalTab.utab> <Desired Tuning>"
	sys.exit()

readfrom = sys.argv[1]
writeto = sys.argv[1][:len(sys.argv[1])-5] + "_" + sys.argv[2] + ".utab"

fileR = open(readfrom, "r")
fileW = open(writeto, "w")

fretlength = 21							#Number of frets on a (my) guitar
position = 0							#String position
heldnum = ""
maxLineLength = 0						#Maximum number of characters in current tab line to standardize the lines
posWithMax = 0							#String position with max line length
heldLines = []							#Array of built lines to standardize line sizes
origHeldLines = []						#Originial Lines to be reverted back to if error found

matchedTuning = findTuning(fileR)		#Tuning shown in the tab

fileR.seek(0)								#Go back to the start of reading the file

for line in fileR:							#Move through input file line by line
	if(line.split('|')[0].rstrip() == Notes[StandardC[position]%12].rstrip()):				#If the line starts with the correct note for implied tuning
		origHeldLines.append(line)
		line = line.rstrip()				#Take off the newline
		buildline = ""
		buildline = buildline + (Notes[desiredTuning[position]%12])
		line = line[len(line.split('|')[0]):] 						#Cut off original first note of the tab (to be replaced with new first note)
		for eachnote in line:										#Look through notes in lines that represent strings
			if(eachnote.isdigit()):										#If the currenct character is digit (implies a note)
				if(heldnum != ""):											#Heldnum is used to get two digit numbers
					heldnum = heldnum + eachnote							#Make the two digit number
					AbsoNote = int(heldnum)+matchedTuning[position]			#Number representation of where the note is relative the lowest possible note (One octave below bottom E)
					RelNote = AbsoNote - desiredTuning[position]			#Get note relative to current string
					buildline = buildline + '[' + str(RelNote) + ']'
					heldnum = ""
					#heldLines.append(buildline)
				else:
					heldnum = eachnote		#Hold current character to see if it is two digit
			else:
				if(heldnum != ""):
					AbsoNote = int(heldnum)+matchedTuning[position]	#Number representation of where the note is relative the lowest possible note (One octave below bottom E)
					RelNote = AbsoNote - desiredTuning[position]	#Get note relative to current string
					buildline = buildline + '[' + str(RelNote) + ']'
					heldnum = ""
					#heldLines.append(buildline)
				buildline = buildline + eachnote					#Current character is not a note, just add it
		if(len(buildline) > maxLineLength):						#Get the longest line so all other lines can be extended to meet it
			maxLineLength = len(buildline)
			posWithMax = position
		heldLines.append(buildline)
		#fileW.write(buildline)		#Write the built line with new notes to file
		position = position + 1 			#increment string
		if (position >= 6):	
			for eachline in heldLines:
				lineSizeDiff = maxLineLength - len(eachline)				#Get difference of this line and largest line
				eachline = eachline[:len(eachline)-2]						#Cut off bar at end of tab line
				for cnt in range(lineSizeDiff):
					eachline = eachline + '-'									#Fill smaller lines to meet largest line
				eachline = eachline + '|\n'									#Add on bar denoting end of this line and the newline char
				fileW.write(eachline)	
			position = 0												#Reset everything
			origHeldLines = []
			heldLines = []
			maxLineLength = 0
			posWithMax = 0
	else:
		if(len(origHeldLines) > 0):
			for eachline in origHeldLines:
				fileW.write(eachline)
			origHeldLines = []
			heldLines = []
			position = 0
			maxLineLength = 0
			posWithMax = 0
		fileW.write(line)

print "Output file written to: " + writeto

fileR.close()
fileW.close()