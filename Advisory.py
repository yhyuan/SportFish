# -*- coding: utf-8 -*-
import cx_Oracle
from datetime import date

def encode(input_string):
	count = 1
	prev = ''
	lst = []
	for character in input_string:
		if character != prev:
			if prev:
				entry = (prev,count)
				lst.append(entry)
				#print lst
			count = 1
			prev = character
		else:
			count += 1
	else:
		entry = (character,count)
		lst.append(entry)
	return lst
	
speciesDict = {"051": "Bowfin","063": "Gizzard Shad","071": "Pink Salmon","073": "Coho Salmon","075": "Chinook Salmon","076": "Rainbow Trout","077": "Atlantic Salmon","078": "Brown Trout","080": "Brook Trout","081": "Lake Trout","082": "Splake","087": "Siscowet","091": "Lake Whitefish","093": "Cisco(Lake Herring)","102": "Round Whitefish","121": "Rainbow Smelt","131": "Northern Pike","151": "Goldeye","152": "Mooneye","161": "Quillback Carpsucker","162": "Longnose Sucker","163": "White Sucker","166": "Bigmouth Buffalo","168": "Silver Redhorse","177": "Redhorse Sucker","181": "Goldfish","186": "Common Carp","233": "Brown Bullhead","234": "Channel Catfish","271": "Ling (Burbot)","301": "White Perch","302": "White Bass","311": "Rock Bass","313": "Pumpkinseed","314": "Bluegill","316": "Smallmouth Bass","317": "Largemouth Bass","318": "White Crappie","319": "Black Crappie","331": "Yellow Perch","332": "Sauger","334": "Walleye","371": "Freshwater Drum"}
analysisDict = [[],[1],[2],[3],[4],[5],[6],[8],[10],[1,12],[2,10],[2,10,11],[2,10,11,12],[2,10,12],[2,11],[2,12],[2,7],[2,7,8,9],[2,7,9],[2,8],[2,8,10],[2,8,10,],[2,8,10,11],[2,8,10,12],[2,8,9],[2,8,9,10],[2,8,9,10,11],[2,8,9,10,12],[],[2,9],[2,9,10],[2,9,10,11],[2,9,10,12],[5,10],[5,10,11],[5,10,11,12],[5,10,12],[5,12],[5,7],[5,7,8],[5,7,8,9],[5,7,9],[5,8],[5,8,10],[5,8,11],[5,8,9],[5,8,9,10],[5,8,9,10,11],[5,9],[5,9,10],[5,9,10,11],[6,12],[8,9],[1,10],[13],[2,8,12],[1,13],[2,13],[2,9,11],[2,7,9,11],[2,7,8,9,10,12],[5,8,9,10,11,12],[5,8,9,10,12],[],[],[],[5,8,10,12,13],[],[2,10,11,12,13],[2,10,13],[5,10,12,13],[],[2,6],[5,9,10,11,12,13],[2,7,12],[2,7,11,12],[2,10,12,13],[2,10,11,13],[5,8,9,12],[5,10,11,12,13],[2,8,9,10,11,12,13],[5,8,9,10,11,12,13],[5,8,10,11,12,13],[5,13],[2,9,10,12,13],[2,9,10,11,12],[2,7,9,11,12],[2,8,9,10,13],[5,8,9,10,13],[5,8,9,10,12,13]]
lengthCategory = {15:0,20:1,25:2,30:3,35:4,40:5,45:6,50:7,55:8,60:9,65:10,70:11,75:12};

connection = cx_Oracle.connect('sportfish/xxxxxxx@sde')
cursor = connection.cursor()
cursor.execute('SELECT GUIDE_WATERBODY_CODE, SPECIES_CODE, POPULATION_TYPE_ID, LENGTH_CATEGORY_ID, ADV_LEVEL, ANALYSIS_CLASS_ID FROM FISH_ADVISORY')
rows = cursor.fetchall()
advisoryIndexDict = {'11': 'a', '10': '8', '00': '6', '20': '5', '48': 'b', '44': '7', '42': '9', '88': '4', '40': '3', 'xx': '0', '80': '2', '84': '1'}
sites = list(set(map(lambda row: row[0], rows)))
print "WATERBODYC\tADVISORY\tANALYMETHOD"
for site in sites:
	site_rows = filter(lambda row: row[0] == site, rows)
	speciesList = list(set(map(lambda row: row[1], site_rows)))
	result = []
	for species in speciesList:
		species_rows = filter(lambda row: row[1] == species, site_rows)
		populationTypeList = list(set(map(lambda row: row[2], species_rows)))
		dict = {}
		for populationType in populationTypeList:
			populationType_rows = filter(lambda row: row[2] == populationType, species_rows)
			adv = ['x'] * 13
			for row in populationType_rows:
				lengthIndex = lengthCategory[row[3]]
				adv[lengthIndex] = str(row[4])
			dict[populationType] = adv
		populationTypeAdv = [''] * 13
		for i in range(13):
			populationTypeAdv[i] = dict[1][i] + dict[2][i]
			populationTypeAdv[i] = advisoryIndexDict[populationTypeAdv[i]]
			#if (not (populationTypeAdv[i] in advisoryIndexDict)):
			#	advisoryIndexDict[populationTypeAdv[i]] = len(advisoryIndexDict)
		encodeList = encode(''.join(populationTypeAdv))
		encoderesult = ""
		for encodeitem in encodeList:
			encoderesult = encoderesult + encodeitem[0] + str(encodeitem[1])
		result.append("'" + species + "': '" + str(encoderesult) + "'")
		analysisMethod = []
		for row in species_rows:
			analysisMethod = list(set(analysisMethod + analysisDict[row[5]]))
	print site + "\t{" + ",".join(result) + "}\t\"" + ",".join(map(lambda method: str(method), analysisMethod)) + "\""
#print advisoryIndexDict
