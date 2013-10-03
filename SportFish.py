import sys, arcpy, os, zipfile, time
reload(sys)
sys.setdefaultencoding("latin-1")

import cx_Oracle
from datetime import date
start_time = time.time()
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

OUTPUT_PATH = "output"
INPUT_PATH = "input"
if arcpy.Exists(OUTPUT_PATH + "\\SportFish.gdb"):
	os.system("rmdir " + OUTPUT_PATH + "\\SportFish.gdb /s /q")
os.system("del " + OUTPUT_PATH + "\\*SportFish*.*")
arcpy.CreateFileGDB_management(OUTPUT_PATH, "SportFish", "9.3")
arcpy.env.workspace = OUTPUT_PATH + "\\SportFish.gdb"

# Read password file to get the password. 
file = open("password.txt")
password = file.readline()
file.close()
connection = cx_Oracle.connect('sportfish/' + password + '@sde')
cursor = connection.cursor()

# Generate species feature class. 
print "Create species feature class"
cursor.execute('SELECT SPECIES_CODE, SPECNAME, NOM_D_ESPECE FROM FISH_ADVISORY')
rows = cursor.fetchall()
speciesList = list(set(rows))
speciesList = map(lambda row: ["" if (row[0] is None) else row[0], "" if (row[1] is None) else row[1], "" if (row[2] is None) else row[2]], speciesList)
arcpy.CreateFeatureclass_management(arcpy.env.workspace, "species", "POINT", "", "DISABLED", "DISABLED", "", "", "0", "0", "0")
arcpy.DefineProjection_management(arcpy.env.workspace + "\\species", "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
arcpy.AddField_management(arcpy.env.workspace + "\\species", "SPECIES_CODE", "TEXT", "", "", "", "", "NON_NULLABLE", "REQUIRED", "")
arcpy.AddField_management(arcpy.env.workspace + "\\species", "SPECNAME", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(arcpy.env.workspace + "\\species", "NOM_D_ESPECE", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
speciesDict = {}
try:
	with arcpy.da.InsertCursor("species", ("SHAPE@XY", "SPECIES_CODE", "SPECNAME", "NOM_D_ESPECE")) as cur:
		for species in speciesList:
			cur.insertRow([(0, 0), species[0], species[1], species[2]])
			speciesDict[species[0]] = [species[1], species[2]]
except Exception as e:
	print e.message

# Generate analysis file and analysisDict.
print "Create analysis feature class"
cursor.execute('SELECT ANALYSIS_CLASS_ID, ANALYSIS_DESC FROM FISH_ADVISORY')
rows = cursor.fetchall()
analysisList = list(set(rows))
arcpy.CreateFeatureclass_management(arcpy.env.workspace, "analysis", "POINT", "", "DISABLED", "DISABLED", "", "", "0", "0", "0")
arcpy.DefineProjection_management(arcpy.env.workspace + "\\analysis", "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
arcpy.AddField_management(arcpy.env.workspace + "\\analysis", "ANALYSIS_CLASS_ID", "LONG", "", "", "", "", "NON_NULLABLE", "REQUIRED", "")
arcpy.AddField_management(arcpy.env.workspace + "\\analysis", "ANALYSIS_DESC", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
analysisDict = {}
try:
	with arcpy.da.InsertCursor("analysis", ("SHAPE@XY", "ANALYSIS_CLASS_ID", "ANALYSIS_DESC")) as cur:
		for analysis in analysisList:
			cur.insertRow([(0, 0), analysis[0], analysis[1]])
			analysisDict[analysis[0]] = analysis[1].split("_");
except Exception as e:
	print e.message

# Generate length category file and lengthCategoryDict.
print "Create lengthCategory feature class"
cursor.execute('SELECT LENGTH_CATEGORY_ID FROM FISH_ADVISORY')
rows = cursor.fetchall()
lengthCategoryList = list(set(rows))
lengthCategoryList.sort()
arcpy.CreateFeatureclass_management(arcpy.env.workspace, "lengthCategory", "POINT", "", "DISABLED", "DISABLED", "", "", "0", "0", "0")
arcpy.DefineProjection_management(arcpy.env.workspace + "\\lengthCategory", "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
arcpy.AddField_management(arcpy.env.workspace + "\\lengthCategory", "LENGTH_CATEGORY_ID", "TEXT", "", "", "", "", "NON_NULLABLE", "REQUIRED", "")
arcpy.AddField_management(arcpy.env.workspace + "\\lengthCategory", "INDEX", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
lengthCategoryDict = {}
i = 0
try:
	with arcpy.da.InsertCursor("lengthCategory", ("SHAPE@XY", "LENGTH_CATEGORY_ID", "INDEX")) as cur:
		for lengthCategory in lengthCategoryList:
			cur.insertRow([(0, 0),  str(lengthCategory[0]), str(i)])
			lengthCategoryDict[lengthCategory[0]] = i;
			i = i + 1
except Exception as e:
	print e.message

# Generate advisoryIndexDict.
print "Create advisoryIndexDict feature class"
#print lengthCategoryDict
cursor.execute('SELECT GUIDE_WATERBODY_CODE, SPECIES_CODE, POPULATION_TYPE_ID, LENGTH_CATEGORY_ID, ADV_LEVEL, ANALYSIS_CLASS_ID FROM FISH_ADVISORY')
rows = cursor.fetchall()
sites = list(set(map(lambda row: row[0], rows)))
arcpy.CreateFeatureclass_management(arcpy.env.workspace, "advisoryIndexDict", "POINT", "", "DISABLED", "DISABLED", "", "", "0", "0", "0")
arcpy.DefineProjection_management(arcpy.env.workspace + "\\advisoryIndexDict", "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
arcpy.AddField_management(arcpy.env.workspace + "\\advisoryIndexDict", "ADVISORY_LEVEL", "TEXT", "", "", "", "", "NON_NULLABLE", "REQUIRED", "")
arcpy.AddField_management(arcpy.env.workspace + "\\advisoryIndexDict", "KEY", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

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
				lengthIndex = lengthCategoryDict[row[3]]
				adv[lengthIndex] = str(row[4])
			dict[populationType] = adv
		populationTypeAdv = [''] * 13
		for i in range(13):
			populationTypeAdv[i] = dict[1][i] + dict[2][i]
			if (not (populationTypeAdv[i] in advisoryIndexDict)):
				advisoryIndexDict[populationTypeAdv[i]] = lookupList[len(advisoryIndexDict)]

try:
	with arcpy.da.InsertCursor("advisoryIndexDict", ("SHAPE@XY", "ADVISORY_LEVEL", "KEY")) as cur:
		for key in advisoryIndexDict.keys():
			cur.insertRow([(0, 0),  advisoryIndexDict[key], key])
except Exception as e:
	print e.message

#print lengthCategoryDict

#print advisoryIndexDict;
print "Create GuideLocs feature class"
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

arcpy.CreateFeatureclass_management(arcpy.env.workspace, "station", "POINT", "", "DISABLED", "DISABLED", "", "", "0", "0", "0")
arcpy.DefineProjection_management(arcpy.env.workspace + "\\station", "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
arcpy.AddField_management(arcpy.env.workspace + "\\station", "WATERBODYC", "LONG", "", "", "", "", "NON_NULLABLE", "REQUIRED", "")
#arcpy.AddField_management(arcpy.env.workspace + "\\station", "LOCNAME_EN", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
#arcpy.AddField_management(arcpy.env.workspace + "\\station", "LOCNAME_FR", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(arcpy.env.workspace + "\\station", "LATITUDE", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(arcpy.env.workspace + "\\station", "LONGITUDE", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
#arcpy.AddField_management(arcpy.env.workspace + "\\station", "GUIDELOC_EN", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
#arcpy.AddField_management(arcpy.env.workspace + "\\station", "GUIDELOC_FR", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(arcpy.env.workspace + "\\station", "LAT_DISPLAY", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(arcpy.env.workspace + "\\station", "LONG_DISPLAY", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(arcpy.env.workspace + "\\station", "SPECIES_EN", "TEXT", "", "", "4000", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(arcpy.env.workspace + "\\station", "SPECIES_FR", "TEXT", "", "", "4000", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(arcpy.env.workspace + "\\station", "ADVISORY", "TEXT", "", "", "4000", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(arcpy.env.workspace + "\\station", "ANALYMETHOD", "TEXT", "", "", "4000", "", "NULLABLE", "NON_REQUIRED", "")
f = open (OUTPUT_PATH + "\\StationOtherInfo.txt","w")
f.write("WATERBODYC\tLOCNAME_EN\tLOCNAME_FR\tGUIDELOC_EN\tGUIDELOC_FR\n")
try:
#	with arcpy.da.InsertCursor("station", ("SHAPE@XY", "WATERBODYC", "LOCNAME_EN", "LOCNAME_FR", "LATITUDE", "LONGITUDE", "GUIDELOC_EN", "GUIDELOC_FR", "LAT_DISPLAY", "LONG_DISPLAY", "SPECIES_EN", "SPECIES_FR", "ADVISORY", "ANALYMETHOD")) as cur:
	with arcpy.da.InsertCursor("station", ("SHAPE@XY", "WATERBODYC", "LATITUDE", "LONGITUDE", "LAT_DISPLAY", "LONG_DISPLAY", "SPECIES_EN", "SPECIES_FR", "ADVISORY", "ANALYMETHOD")) as cur:
		#for key in advisoryIndexDict.keys():
		#	cur.insertRow([(0, 0),  advisoryIndexDict[key], key])
		print (len(sites))
		for site in sites:
			#print site
			site_rows = filter(lambda row: row[0] == site, rows)
			#print site_rows
			speciesList = list(set(map(lambda row: row[1], site_rows)))
			result = []
			analysisMethodResult = []
			row0 = site_rows[0]
			locDesc = ["  ", "  "] 
			#print "2"
			if((not(row0[10] is None)) and ("|" in row0[10])):
				locDesc = row0[10].split("|")
			#print "3"
			longitude = -convertLatLng(row0[9])
			latitude = convertLatLng(row0[8])
			#print "4"
			#insertRow = [(longitude, latitude), int(site), row0[6], row0[7], latitude, longitude, locDesc[0], locDesc[1], convertLatLngString(row0[8]), convertLatLngString(row0[9]), getSpeciesNames(speciesList, "EN"), getSpeciesNames(speciesList, "FR")]
			insertRow = [(longitude, latitude), site, latitude, longitude, convertLatLngString(row0[8]), convertLatLngString(row0[9]), getSpeciesNames(speciesList, "EN"), getSpeciesNames(speciesList, "FR")]
			f.write(site + "\t\"" + row0[6] + "\"\t\"" + row0[7] + "\"\t\"" + locDesc[0] + "\"\t\"" + locDesc[1] + "\"\n")
			#print "5"
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
			insertRow = insertRow + ["{" + ",".join(result) + "}", "{" + ",".join(analysisMethodResult) + "}"]
			#print insertRow
			#print row0[6]
			cur.insertRow(insertRow)

except Exception as e:
	print "Exception"
	print e.message
	f.close()
f.close()

arcpy.AddField_management(arcpy.env.workspace + "\\station", "LOCNAME_EN", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(arcpy.env.workspace + "\\station", "LOCNAME_FR", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(arcpy.env.workspace + "\\station", "GUIDELOC_EN", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.AddField_management(arcpy.env.workspace + "\\station", "GUIDELOC_FR", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.MakeFeatureLayer_management(arcpy.env.workspace + "\\station", "station_Layer", "", "", "OBJECTID OBJECTID VISIBLE NONE;Shape Shape VISIBLE NONE;WATERBODYC WATERBODYC VISIBLE NONE;LATITUDE LATITUDE VISIBLE NONE;LONGITUDE LONGITUDE VISIBLE NONE;LAT_DISPLAY LAT_DISPLAY VISIBLE NONE;LONG_DISPLAY LONG_DISPLAY VISIBLE NONE;SPECIES_EN SPECIES_EN VISIBLE NONE;SPECIES_FR SPECIES_FR VISIBLE NONE;ADVISORY ADVISORY VISIBLE NONE;ANALYMETHOD ANALYMETHOD VISIBLE NONE")
arcpy.MakeTableView_management(OUTPUT_PATH + "\\StationOtherInfo.txt", "StationOtherInfo_View", "", "", "WATERBODYC WATERBODYC VISIBLE NONE;LOCNAME_EN LOCNAME_EN VISIBLE NONE;LOCNAME_FR LOCNAME_FR VISIBLE NONE;GUIDELOC_EN GUIDELOC_EN VISIBLE NONE;GUIDELOC_FR GUIDELOC_FR VISIBLE NONE")
arcpy.AddJoin_management("station_Layer", "WATERBODYC", "StationOtherInfo_View", "WATERBODYC", "KEEP_ALL")
arcpy.CalculateField_management("station_Layer", "station.LOCNAME_EN", "[StationOtherInfo.txt.LOCNAME_EN]", "VB", "")
arcpy.CalculateField_management("station_Layer", "station.LOCNAME_FR", "[StationOtherInfo.txt.LOCNAME_FR]", "VB", "")
arcpy.CalculateField_management("station_Layer", "station.GUIDELOC_EN", "[StationOtherInfo.txt.GUIDELOC_EN]", "VB", "")
arcpy.CalculateField_management("station_Layer", "station.GUIDELOC_FR", "[StationOtherInfo.txt.GUIDELOC_FR]", "VB", "")
arcpy.RemoveJoin_management("station_Layer", "")

arcpy.Project_management(arcpy.env.workspace + "\\station", arcpy.env.workspace + "\\GuideLocs", "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]", "NAD_1983_To_WGS_1984_5", "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
arcpy.Delete_management(arcpy.env.workspace + "\\station", "FeatureClass")

arcpy.Project_management(arcpy.env.workspace + "\\advisoryIndexDict", arcpy.env.workspace + "\\advisoryIndexDict_Feature", "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]", "NAD_1983_To_WGS_1984_5", "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
arcpy.Delete_management(arcpy.env.workspace + "\\advisoryIndexDict", "FeatureClass")

arcpy.Project_management(arcpy.env.workspace + "\\lengthCategory", arcpy.env.workspace + "\\lengthCategory_Feature", "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]", "NAD_1983_To_WGS_1984_5", "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
arcpy.Delete_management(arcpy.env.workspace + "\\lengthCategory", "FeatureClass")

arcpy.Project_management(arcpy.env.workspace + "\\analysis", arcpy.env.workspace + "\\analysis_Feature", "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]", "NAD_1983_To_WGS_1984_5", "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
arcpy.Delete_management(arcpy.env.workspace + "\\analysis", "FeatureClass")

arcpy.Project_management(arcpy.env.workspace + "\\species", arcpy.env.workspace + "\\species_Feature", "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]", "NAD_1983_To_WGS_1984_5", "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
arcpy.Delete_management(arcpy.env.workspace + "\\species", "FeatureClass")

# Prepare the msd, mxd, and readme.txt
os.system("copy " + INPUT_PATH + "\\SportFish.msd " + OUTPUT_PATH)
os.system("copy " + INPUT_PATH + "\\SportFish.mxd " + OUTPUT_PATH)
f = open (INPUT_PATH + "\\readme_SportFish.txt","r")
data = f.read()
f.close()
import time
dateString = time.strftime("%Y/%m/%d", time.localtime())
data = data.replace("[DATE]", dateString)
f = open (OUTPUT_PATH + "\\readme_SportFish.txt","w")
f.write(data)
f.close()

# Compress the msd, mxd, readme.txt and file geodatabase together into a zip file named SportFish.zip, which will be send to web service publisher. 
'''target_dir = OUTPUT_PATH + '\\SportFish.gdb'
zip = zipfile.ZipFile(OUTPUT_PATH + '\\SportFish.zip', 'w', zipfile.ZIP_DEFLATED)
rootlen = len(target_dir) + 1
for base, dirs, files in os.walk(target_dir):
   for file in files:
      fn = os.path.join(base, file)
      zip.write(fn, "SportFish.gdb\\" + fn[rootlen:])
zip.write(OUTPUT_PATH + '\\SportFish.msd', "SportFish.msd")
zip.write(OUTPUT_PATH + '\\SportFish.mxd', "SportFish.mxd")
zip.write(OUTPUT_PATH + '\\readme_SportFish.txt', "readme_SportFish.txt")
zip.close()
'''
os.system("del " + OUTPUT_PATH + "\\StationOtherInfo.txt")

elapsed_time = time.time() - start_time
print elapsed_time
