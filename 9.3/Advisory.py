import sys
reload(sys)
sys.setdefaultencoding("latin-1")

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

# Read password file to get the password. 
file = open("password.txt")
password = file.readline()
file.close()
connection = cx_Oracle.connect('sportfish/' + password + '@sde')
cursor = connection.cursor()

# Generate specieslist file. 
cursor.execute('SELECT SPECIES_CODE, SPECNAME, NOM_D_ESPECE FROM FISH_ADVISORY')
rows = cursor.fetchall()
speciesList = list(set(rows))
speciesList = map(lambda row: ["" if (row[0] is None) else row[0], "" if (row[1] is None) else row[1], "" if (row[2] is None) else row[2]], speciesList)
species_file = open("species.txt", "w")
species_file.write( "Latitude, Longitude, SPECIES_CODE, SPECNAME, NOM_D_ESPECE\n")
speciesDict = {}
for species in speciesList:
	species_file.write( "0, 0, \"" + species[0] + "\",\"" + species[1] + "\",\"" + species[2] + "\"\n")
	speciesDict[species[0]] = [species[1], species[2]]
species_file.close()

# Generate analysis file and analysisDict.
cursor.execute('SELECT ANALYSIS_CLASS_ID, ANALYSIS_DESC FROM FISH_ADVISORY')
rows = cursor.fetchall()
analysisList = list(set(rows))
analysis_file = open("analysis.txt", "w")
analysis_file.write( "Latitude, Longitude, ANALYSIS_CLASS_ID, ANALYSIS_DESC\n")
analysisDict = {}
for analysis in analysisList:
	analysis_file.write( "0, 0, " + str(analysis)[1:-1] + "\n")
	analysisDict[analysis[0]] = analysis[1].split("_");
analysis_file.close()

# Generate length category file and lengthCategoryDict.
cursor.execute('SELECT LENGTH_CATEGORY_ID FROM FISH_ADVISORY')
rows = cursor.fetchall()
lengthCategoryList = list(set(rows))
lengthCategoryList.sort()
lengthCategory_file = open("lengthCategory.txt", "w")
lengthCategory_file.write( "Latitude, Longitude, LENGTH_CATEGORY_ID, INDEX\n")
lengthCategoryDict = {}
i = 0
for lengthCategory in lengthCategoryList:
	lengthCategory_file.write( "0, 0, " + str(lengthCategory[0]) + ", " + str(i) + "\n")
	lengthCategoryDict[lengthCategory[0]] = i;
	i = i + 1
lengthCategory_file.close()

# Generate advisoryIndexDict.
#print lengthCategoryDict
cursor.execute('SELECT GUIDE_WATERBODY_CODE, SPECIES_CODE, POPULATION_TYPE_ID, LENGTH_CATEGORY_ID, ADV_LEVEL, ANALYSIS_CLASS_ID FROM FISH_ADVISORY')
rows = cursor.fetchall()
sites = list(set(map(lambda row: row[0], rows)))
advisoryIndexDict = {}
lookupList = map(lambda i: str(i), list(range(0, 10))) + map(chr, range(97, 123))
for site in sites:
	site_rows = filter(lambda row: row[0] == site, rows)
	speciesList = list(set(map(lambda row: row[1], site_rows)))
	result = []
	analysisMethodResult = []
	for species in speciesList:
		species_rows = filter(lambda row: row[1] == species, site_rows)
		populationTypeList = list(set(map(lambda row: row[2], species_rows)))
		dict = {}
		for populationType in populationTypeList:
			populationType_rows = filter(lambda row: row[2] == populationType, species_rows)
			adv = ['x'] * 13
			for row in populationType_rows:
				#print row[3]
				#print lengthCategory
				#print lengthCategory['20']
				lengthIndex = lengthCategoryDict[row[3]]
				adv[lengthIndex] = str(row[4])
			dict[populationType] = adv
		populationTypeAdv = [''] * 13
		for i in range(13):
			populationTypeAdv[i] = dict[1][i] + dict[2][i]
			#populationTypeAdv[i] = advisoryIndexDict[populationTypeAdv[i]]
			if (not (populationTypeAdv[i] in advisoryIndexDict)):
				advisoryIndexDict[populationTypeAdv[i]] = lookupList[len(advisoryIndexDict)]

advisoryIndexDict_file = open("advisoryIndexDict.txt", "w")
advisoryIndexDict_file.write( "Latitude, Longitude, ADVISORY_LEVEL, KEY\n")
for key in advisoryIndexDict.keys():
	advisoryIndexDict_file.write( "0, 0, \"" + advisoryIndexDict[key] + "\", \"" + key + "\"\n")
advisoryIndexDict_file.close()

#print lengthCategoryDict

#print advisoryIndexDict;

#speciesDict = {"051": "Bowfin","063": "Gizzard Shad","071": "Pink Salmon","073": "Coho Salmon","075": "Chinook Salmon","076": "Rainbow Trout","077": "Atlantic Salmon","078": "Brown Trout","080": "Brook Trout","081": "Lake Trout","082": "Splake","087": "Siscowet","091": "Lake Whitefish","093": "Cisco(Lake Herring)","102": "Round Whitefish","121": "Rainbow Smelt","131": "Northern Pike","151": "Goldeye","152": "Mooneye","161": "Quillback Carpsucker","162": "Longnose Sucker","163": "White Sucker","166": "Bigmouth Buffalo","168": "Silver Redhorse","177": "Redhorse Sucker","181": "Goldfish","186": "Common Carp","233": "Brown Bullhead","234": "Channel Catfish","271": "Ling (Burbot)","301": "White Perch","302": "White Bass","311": "Rock Bass","313": "Pumpkinseed","314": "Bluegill","316": "Smallmouth Bass","317": "Largemouth Bass","318": "White Crappie","319": "Black Crappie","331": "Yellow Perch","332": "Sauger","334": "Walleye","371": "Freshwater Drum"}
#print len(speciesDict)
#analysisDict = [[],[1],[2],[3],[4],[5],[6],[8],[10],[1,12],[2,10],[2,10,11],[2,10,11,12],[2,10,12],[2,11],[2,12],[2,7],[2,7,8,9],[2,7,9],[2,8],[2,8,10],[2,8,10,],[2,8,10,11],[2,8,10,12],[2,8,9],[2,8,9,10],[2,8,9,10,11],[2,8,9,10,12],[],[2,9],[2,9,10],[2,9,10,11],[2,9,10,12],[5,10],[5,10,11],[5,10,11,12],[5,10,12],[5,12],[5,7],[5,7,8],[5,7,8,9],[5,7,9],[5,8],[5,8,10],[5,8,11],[5,8,9],[5,8,9,10],[5,8,9,10,11],[5,9],[5,9,10],[5,9,10,11],[6,12],[8,9],[1,10],[13],[2,8,12],[1,13],[2,13],[2,9,11],[2,7,9,11],[2,7,8,9,10,12],[5,8,9,10,11,12],[5,8,9,10,12],[],[],[],[5,8,10,12,13],[],[2,10,11,12,13],[2,10,13],[5,10,12,13],[],[2,6],[5,9,10,11,12,13],[2,7,12],[2,7,11,12],[2,10,12,13],[2,10,11,13],[5,8,9,12],[5,10,11,12,13],[2,8,9,10,11,12,13],[5,8,9,10,11,12,13],[5,8,10,11,12,13],[5,13],[2,9,10,12,13],[2,9,10,11,12],[2,7,9,11,12],[2,8,9,10,13],[5,8,9,10,13],[5,8,9,10,12,13]]
#lengthCategoryDict = {15:0,20:1,25:2,30:3,35:4,40:5,45:6,50:7,55:8,60:9,65:10,70:11,75:12};
def convertLatLngString(latlng):
	latlngStr = str(latlng)
	degrees = latlngStr[:2]
	minutes = latlngStr[2:4]
	seconds = "00"
	if(len(latlngStr) > 5):
		seconds = latlngStr[4:]
	elif (len(latlngStr) == 5):
		seconds = latlngStr[4:] + "0"
	return degrees + minutes + seconds
def convertLatLng(latlng):
	latlngStr = str(latlng)
	degrees = int(latlngStr[:2])
	minutes = int(latlngStr[2:4])
	seconds = 0
	if(len(latlngStr) > 4):
		seconds = int(latlngStr[4:])
	return (degrees + minutes/60.0 + seconds/3600.0)
def getSpeciesNames(speciesList, language):
	index = 1
	if (language == "EN"):
		index = 0
	speciesNames = map(lambda species: speciesDict[species][index].replace(" ", "_").decode('latin-1').upper(), speciesList)
	return "-" + "-".join(speciesNames) + "-"

cursor.execute('SELECT GUIDE_WATERBODY_CODE, SPECIES_CODE, POPULATION_TYPE_ID, LENGTH_CATEGORY_ID, ADV_LEVEL, ANALYSIS_CLASS_ID, GUIDE_LOCNAME_ENG, GUIDE_LOCNAME_FR, LATITUDE, LONGITUDE, GUIDE_LOCDESC FROM FISH_ADVISORY')
rows = cursor.fetchall()
#advisoryIndexDict = {'11': 'a', '10': '8', '00': '6', '20': '5', '48': 'b', '44': '7', '42': '9', '88': '4', '40': '3', 'xx': '0', '80': '2', '84': '1'}
sites = list(set(map(lambda row: row[0], rows)))
advisory_file = open("advisory.txt", "w")
#advisory_file.write( "WATERBODYC\tLOCNAME_EN\tLOCNAME_FR\tLATITUDE\tLONGITUDE\tGUIDELOC_EN\tGUIDELOC_FR\tSPECIES_EN\tSPECIES_FR\tLAT_DISPLAY\tLONG_DISPLAY\tADVISORY\tANALYMETHOD\n")
#advisory_file.write("CREATE TABLE SPORTFISH_DATA ( WATERBODYC  int, LOCNAME_EN varchar2(4000), LOCNAME_FR varchar2(4000), LATITUDE NUMBER(16,8), LONGITUDE NUMBER(16,8), GUIDELOC_EN varchar2(4000), GUIDELOC_FR varchar2(4000), SPECIES_EN varchar2(4000), SPECIES_FR varchar2(4000), LAT_DISPLAY varchar2(10), LONG_DISPLAY varchar2(10), ADVISORY varchar2(4000), ANALYMETHOD varchar2(4000));\n")
station_file = open("station.txt", "w")
station_file.write( "WATERBODYC\tLOCNAME_EN\tLOCNAME_FR\tLATITUDE\tLONGITUDE\tGUIDELOC_EN\tGUIDELOC_FR\tLAT_DISPLAY\tLONG_DISPLAY\n")

for site in sites:
	site_rows = filter(lambda row: row[0] == site, rows)
	speciesList = list(set(map(lambda row: row[1], site_rows)))
	result = []
	analysisMethodResult = []
	row0 = site_rows[0]
	locDesc = ["  ", "  "] 
	if((not(row0[10] is None)) and ("|" in row0[10])):
		locDesc = row0[10].split("|")
	#elif (not(row0[10] is None)):
	#	locDesc[0] = row0[10]
	#advisory_file.write(site + "\t\"" + row0[6] + "\"\t\"" + row0[7] + "\"\t" + str(convertLatLng(row0[8]))  + "\t" + str(-convertLatLng(row0[9]))  + "\t\"" + locDesc[0]  + "\"\t\"" +  locDesc[1]  + "\"\t\"" +  getSpeciesNames(speciesList, "EN") + "\"\t\"" +  getSpeciesNames(speciesList, "FR") + "\"\t\"" +  convertLatLngString(row0[8]) + "\"\t\"" +  convertLatLngString(row0[9]) + "\"")
	station_file.write(site + "\t\"" + row0[6] + "\"\t\"" + row0[7] + "\"\t" + str(convertLatLng(row0[8]))  + "\t" + str(-convertLatLng(row0[9]))  + "\t\"" + locDesc[0]  + "\"\t\"" +  locDesc[1]  + "\"\t\"" +  convertLatLngString(row0[8]) + "\"\t\"" +  convertLatLngString(row0[9]) + "\"\n")
	advisory_file.write(site + "\t" + getSpeciesNames(speciesList, "EN") + "\t" +  getSpeciesNames(speciesList, "FR") + "")
	for species in speciesList:
		species_rows = filter(lambda row: row[1] == species, site_rows)
		populationTypeList = list(set(map(lambda row: row[2], species_rows)))
		dict = {}
		for populationType in populationTypeList:
			populationType_rows = filter(lambda row: row[2] == populationType, species_rows)
			adv = ['x'] * 13
			for row in populationType_rows:
				lengthIndex = lengthCategoryDict[row[3]]
				adv[lengthIndex] = str(row[4])
			dict[populationType] = adv
		populationTypeAdv = [''] * 13
		for i in range(13):
			populationTypeAdv[i] = dict[1][i] + dict[2][i]
			populationTypeAdv[i] = advisoryIndexDict[populationTypeAdv[i]]
		encodeList = encode(''.join(populationTypeAdv))
		encoderesult = ""
		for encodeitem in encodeList:
			encoderesult = encoderesult + encodeitem[0] + lookupList[encodeitem[1]]
		result.append('"' + species + '":"' + str(encoderesult) + '"')
		analysisMethod = []
		for row in species_rows:
			analysisMethod = list(set(analysisMethod + analysisDict[row[5]]))
		#print site + "\t" + species
		#print analysisMethod
		analysisMethod = filter(lambda x: len(x) > 0, analysisMethod)
		analysisMethod = map(lambda x: int(x), analysisMethod)
		analysisMethod.sort()
		#print analysisMethod
		analysisMethod = map(lambda x: str(x), analysisMethod)
		analysisMethodResult.append('"' + species + '":"' + ",".join(analysisMethod) + '"')
	advisory_file.write("\t{" + ",".join(result) + "}\t{" + ",".join(analysisMethodResult) + "}\n")
	#advisory_file.write("INSERT INTO SPORTFISH_DATA VALUES (" + site + ", \"" + row0[6] + "\", \"" + row0[7] + "\", " + str(convertLatLng(row0[8]))  + ", " + str(-convertLatLng(row0[9]))  + ", \"" + locDesc[0]  + "\", \"" +  locDesc[1]  + "\", \"" +  getSpeciesNames(speciesList, "EN") + "\", \"" +  getSpeciesNames(speciesList, "FR") + "\", \"" +  convertLatLngString(row0[8]) + "\", \"" +  convertLatLngString(row0[9]) + "\", '{" + ",".join(result) + "}','{" + ",".join(analysisMethodResult) + "}');\n");
station_file.close()
advisory_file.close()
#print advisoryIndexDict

# Since ArcGIS can not open the text file with text field which is longer than 255 characters, the following steps are required. 
# 1. Create a table in Oracle with following SQL: CREATE TABLE SPORTFISH_DATA ( WATERBODYC  int, SPECIES_EN varchar2(4000), SPECIES_FR varchar2(4000), ADVISORY varchar2(4000), ANALYMETHOD varchar2(4000));
# 2. Use SQL loader to load the advisory.txt to Oracle. sqlldr username/password@sde control=sportfish.ctl, log=1.log, bad=1.bad
# 3. Use ArcGIS to convert station.txt to feature class. Join it with the SPORTFISH_DATA table in Oracle and create a required feature class. 
# 
#
#
#
#
