# This script reads a table named FISH_ADVISORY to generate a file geodatabase. 
import sys, arcpy, os, zipfile, time
reload(sys)
sys.setdefaultencoding("latin-1")

import cx_Oracle
from datetime import date
start_time = time.time()
def createFeatureClass(featureName, featureData, featureFieldList, featureInsertCursorFields):
	print "Create " + featureName + " feature class"
	featureNameNAD83 = featureName + "_NAD83"
	featureNameNAD83Path = arcpy.env.workspace + "\\"  + featureNameNAD83
	arcpy.CreateFeatureclass_management(arcpy.env.workspace, featureNameNAD83, "POINT", "", "DISABLED", "DISABLED", "", "", "0", "0", "0")
	# Process: Define Projection
	arcpy.DefineProjection_management(featureNameNAD83Path, "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
	# Process: Add Fields	
	for featrueField in featureFieldList:
		arcpy.AddField_management(featureNameNAD83Path, featrueField[0], featrueField[1], featrueField[2], featrueField[3], featrueField[4], featrueField[5], featrueField[6], featrueField[7], featrueField[8])
	# Process: Append the records
	cntr = 1
	try:
		with arcpy.da.InsertCursor(featureNameNAD83, featureInsertCursorFields) as cur:
			for rowValue in featureData:
				cur.insertRow(rowValue)
				cntr = cntr + 1
	except Exception as e:
		print "\tError: " + featureName + ": " + e.message
	# Change the projection to web mercator
	arcpy.Project_management(featureNameNAD83Path, arcpy.env.workspace + "\\" + featureName, "PROJCS['WGS_1984_Web_Mercator_Auxiliary_Sphere',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Mercator_Auxiliary_Sphere'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',0.0],PARAMETER['Standard_Parallel_1',0.0],PARAMETER['Auxiliary_Sphere_Type',0.0],UNIT['Meter',1.0]]", "NAD_1983_To_WGS_1984_5", "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")
	arcpy.FeatureClassToShapefile_conversion([featureNameNAD83Path], OUTPUT_PATH + "\\Shapefile")
	arcpy.Delete_management(featureNameNAD83Path, "FeatureClass")
	print "Finish " + featureName + " feature class."

def createTextFile(fileName, rows, featureFieldList):
	f = open (fileName,"w")
	f.write("\t".join(map(lambda field: field[0], featureFieldList)) + "\r\n")
	f.write("\r\n".join(map(lambda row: "\t".join(map(lambda item: str(item), row[1:])), rows)))
	f.close()

OUTPUT_PATH = "output"
INPUT_PATH = "input"
if arcpy.Exists(OUTPUT_PATH + "\\SportFish.gdb"):
	os.system("rmdir " + OUTPUT_PATH + "\\SportFish.gdb /s /q")
os.system("del " + OUTPUT_PATH + "\\*SportFish*.*")
os.system("del " + OUTPUT_PATH + "\\Shapefile\\*SportFish.*")
arcpy.CreateFileGDB_management(OUTPUT_PATH, "SportFish", "9.3")
arcpy.env.workspace = OUTPUT_PATH + "\\SportFish.gdb"

# Read password file to get the password. 
file = open("password.txt")
password = file.readline()
file.close()
file = open("username.txt")
username = file.readline()
file.close()

connection = cx_Oracle.connect(username + '/' + password + '@sde')
cursor = connection.cursor()

speciesEnglishURLDict = {}
speciesFrenchURLDict = {}
file = open(INPUT_PATH + '\\Species_URLs.txt', 'r')
i = 0
for line in file:
	i = i + 1
	if i == 1:
		continue
	items = line.strip().split('\t')
	if items[2] == 'English':
		if len(items) == 4:
			speciesEnglishURLDict[items[1]] = items[3]
		else:
			speciesEnglishURLDict[items[1]] = ""
	else:
		if len(items) == 4:
			speciesFrenchURLDict[items[1]] = items[3]
		else:
			speciesFrenchURLDict[items[1]] = ""

# Generate SPECIES feature class. 
featureName = "SPECIES"
featureFieldList = [["SPECIES_CODE", "TEXT", "", "", "", "", "NON_NULLABLE", "REQUIRED", ""], ["SPECNAME", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""], ["NOM_D_ESPECE", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""], ["SPECIES_URL_EN", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""], ["SPECIES_URL_FR", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""]]
featureInsertCursorFields = tuple(["SHAPE@XY"] + map(lambda field: field[0], featureFieldList))
cursor.execute('SELECT SPECIES_CODE, SPECNAME, NOM_D_ESPECE FROM FISH_ADVISORY')
rows = map(lambda row: [(0, 0), "" if (row[0] is None) else row[0], "" if (row[1] is None) else row[1], "" if (row[2] is None) else row[2]] + [speciesEnglishURLDict.get(row[0],''), speciesFrenchURLDict.get(row[0],'')], list(set(cursor.fetchall())))
#print len(rows)
createFeatureClass(featureName, rows, featureFieldList, featureInsertCursorFields)
speciesDict = {}
for row in rows:
	speciesDict[row[1]] = [row[2], row[3]]
createTextFile(OUTPUT_PATH + "\\TXT\\" + featureName + ".txt", rows, featureFieldList)


# Generate ADVISORIES feature class. 
featureName = "ADVISORIES"
featureFieldList = [["GUIDE_WATERBODY_CODE", "TEXT", "", "", "", "", "NON_NULLABLE", "REQUIRED", ""], ["SPECIES_CODE", "TEXT", "", "", "", "", "NON_NULLABLE", "REQUIRED", ""], ["POPULATION_TYPE_ID", "LONG", "", "", "", "", "NON_NULLABLE", "REQUIRED", ""], ["LENGTH_CATEGORY_ID", "LONG", "", "", "", "", "NON_NULLABLE", "REQUIRED", ""], ["ADV_LEVEL", "LONG", "", "", "", "", "NON_NULLABLE", "REQUIRED", ""], ["ADV_CAUSE_ID", "LONG", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""]]
featureInsertCursorFields = tuple(["SHAPE@XY"] + map(lambda field: field[0], featureFieldList))
cursor.execute('SELECT GUIDE_WATERBODY_CODE, SPECIES_CODE, POPULATION_TYPE_ID, LENGTH_CATEGORY_ID, ADV_LEVEL, ADV_CAUSE_ID FROM FISH_ADVISORY')
rows = map(lambda row: [(0, 0)] + list(row), cursor.fetchall())
createFeatureClass(featureName, rows, featureFieldList, featureInsertCursorFields)
createTextFile(OUTPUT_PATH + "\\TXT\\" + featureName + ".txt", rows, featureFieldList)

# Generate POPULATION_TYPE feature class. 
featureName = "POPULATION_TYPE"
featureFieldList = [["POPULATION_TYPE_ID", "LONG", "", "", "", "", "NON_NULLABLE", "REQUIRED", ""], ["POPULATION_TYPE_DESC", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""]]
featureInsertCursorFields = tuple(["SHAPE@XY"] + map(lambda field: field[0], featureFieldList))
cursor.execute('SELECT POPULATION_TYPE_ID, POPULATION_TYPE_DESC FROM FISH_ADVISORY')
rows = map(lambda row: [(0, 0)] + list(row), list(set(cursor.fetchall())))
createFeatureClass(featureName, rows, featureFieldList, featureInsertCursorFields)
createTextFile(OUTPUT_PATH + "\\TXT\\" + featureName + ".txt", rows, featureFieldList)

# Generate LENGTH_CATEGORY feature class. 
featureName = "LENGTH_CATEGORY"
featureFieldList = [["LENGTH_CATEGORY_ID", "LONG", "", "", "", "", "NON_NULLABLE", "REQUIRED", ""], ["LENGTH_CATEGORY_LABEL", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""]]
featureInsertCursorFields = tuple(["SHAPE@XY"] + map(lambda field: field[0], featureFieldList))
cursor.execute('SELECT LENGTH_CATEGORY_ID, LENGTH_CATEGORY_LABEL FROM FISH_ADVISORY')
rows = map(lambda row: [(0, 0)] + list(row), list(set(cursor.fetchall())))
createFeatureClass(featureName, rows, featureFieldList, featureInsertCursorFields)
createTextFile(OUTPUT_PATH + "\\TXT\\" + featureName + ".txt", rows, featureFieldList)

# Generate ADV_CAUSE feature class. 
featureName = "ADV_CAUSE"
featureFieldList = [["ADV_CAUSE_ID", "LONG", "", "", "", "", "NON_NULLABLE", "REQUIRED", ""], ["ADV_CAUSE_DESC", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""]]
featureInsertCursorFields = tuple(["SHAPE@XY"] + map(lambda field: field[0], featureFieldList))
cursor.execute('SELECT ADV_CAUSE_ID, ADV_CAUSE_DESC FROM FISH_ADVISORY WHERE ADV_CAUSE_ID IS NOT NULL')
rows = map(lambda row: [(0, 0)] + list(row), list(set(cursor.fetchall())))
createFeatureClass(featureName, rows, featureFieldList, featureInsertCursorFields)
createTextFile(OUTPUT_PATH + "\\TXT\\" + featureName + ".txt", rows, featureFieldList)

# Generate GUIDELOCATIONS feature class. 
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
def getLocationDescription(location, language):
	locDesc = ["  ", "  "] 
	if((not(location is None)) and ("|" in location)):
		locDesc = location.split("|")
	if (language == "EN"):
		return locDesc[0]
	else:
		return locDesc[1]

cursor.execute('SELECT GUIDE_WATERBODY_CODE, SPECIES_CODE FROM FISH_ADVISORY')
rows = cursor.fetchall()
waterbodySpeciesDict = {}
for row in rows:
	if row[0] in waterbodySpeciesDict:
		waterbodySpeciesDict[row[0]].append(row[1])
	else:
		waterbodySpeciesDict[row[0]] = [row[1]]
featureName = "GUIDELOCATIONS"
featureFieldList = [["WATERBODYC", "LONG", "", "", "", "", "NON_NULLABLE", "REQUIRED", ""], ["LATITUDE", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""], ["LONGITUDE", "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""], ["LAT_DISPLAY", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""], ["LONG_DISPLAY", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""], ["SPECIES_EN", "TEXT", "", "", "4000", "", "NULLABLE", "NON_REQUIRED", ""], ["SPECIES_FR", "TEXT", "", "", "4000", "", "NULLABLE", "NON_REQUIRED", ""], ["LOCNAME_EN", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""], ["LOCNAME_FR", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""], ["GUIDELOC_EN", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""], ["GUIDELOC_FR", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", ""]]
featureInsertCursorFields = tuple(["SHAPE@XY"] + map(lambda field: field[0], featureFieldList))
cursor.execute('SELECT GUIDE_WATERBODY_CODE, GUIDE_LOCNAME_ENG, GUIDE_LOCNAME_FR, LATITUDE, LONGITUDE, GUIDE_LOCDESC FROM FISH_ADVISORY')
rows = map(lambda row: [(-convertLatLng(row[4]), convertLatLng(row[3]))] + [row[0], convertLatLng(row[3]), -convertLatLng(row[4]), convertLatLngString(row[3]), convertLatLngString(row[4]), getSpeciesNames(waterbodySpeciesDict[row[0]], "EN"), getSpeciesNames(waterbodySpeciesDict[row[0]], "FR"), row[1], row[2], getLocationDescription(row[5], "EN"), getLocationDescription(row[5], "FR")], list(set(cursor.fetchall())))
createFeatureClass(featureName, rows, featureFieldList, featureInsertCursorFields)
print len(rows)
featureFieldList = featureFieldList[:5] + featureFieldList[7:]
rows = map(lambda row: row[:6] + row[8:], rows)
createTextFile(OUTPUT_PATH + "\\TXT\\" + featureName + ".txt", rows, featureFieldList)

# Process: Add Attribute Index
arcpy.AddIndex_management(arcpy.env.workspace + "\\GUIDELOCATIONS", "SPECIES_EN;SPECIES_FR;LOCNAME_EN;LOCNAME_FR", "GUIDELOCATIONSIndex", "NON_UNIQUE", "NON_ASCENDING")
arcpy.AddIndex_management(arcpy.env.workspace + "\\ADVISORIES", "GUIDE_WATERBODY_CODE", "ADVISORIESIndex", "NON_UNIQUE", "NON_ASCENDING")
arcpy.AddIndex_management(arcpy.env.workspace + "\\SPECIES", "SPECIES_CODE", "SPECIESIndex", "NON_UNIQUE", "NON_ASCENDING")

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
target_dir = OUTPUT_PATH + '\\TXT'
zip = zipfile.ZipFile(OUTPUT_PATH + '\\SportFish.TXT.zip', 'w', zipfile.ZIP_DEFLATED)
rootlen = len(target_dir) + 1
for base, dirs, files in os.walk(target_dir):
   for file in files:
      fn = os.path.join(base, file)
      zip.write(fn, "TXT\\" + fn[rootlen:])
zip.close()

# Compress the msd, mxd, readme.txt and file geodatabase together into a zip file named SportFish.zip, which will be send to web service publisher. 
target_dir = OUTPUT_PATH + '\\SportFish.gdb'
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


# Generate Data download file . 
"\t".join
cursor.execute('SELECT GUIDE_WATERBODY_CODE, GUIDE_LOCNAME_ENG, GUIDE_LOCNAME_FR, LATITUDE, LONGITUDE, SPECIES_CODE, SPECNAME, NOM_D_ESPECE, POPULATION_TYPE_ID, POPULATION_TYPE_DESC, LENGTH_CATEGORY_ID, LENGTH_CATEGORY_LABEL, ADV_LEVEL, ADV_CAUSE_ID, ADV_CAUSE_DESC, GUIDE_YEAR, GUIDE_LOCDESC FROM FISH_ADVISORY')
rows = map(lambda row: map(lambda item: ("\"" + item + "\"") if (isinstance(item, str)) else ("" if (item is None) else str(int(item))), list(row)), cursor.fetchall())
rows = map(lambda row: row[:3] + [(row[3] + "00") if (len(row[3]) == 4) else ((row[3] + "0") if (len(row[3]) == 5) else (row[3]))] + row[4:], rows)
rows = map(lambda row: row[:4] + [(row[4] + "00") if (len(row[4]) == 4) else ((row[4] + "0") if (len(row[4]) == 5) else (row[4]))] + row[5:], rows)
rows = map(lambda row: "\t".join(row), rows)

f = open (OUTPUT_PATH + "\FishGuide.txt","w")
f.write("GUIDE_WATERBODY_CODE\tGUIDE_LOCNAME_ENG\tGUIDE_LOCNAME_FR\tLATITUDE\tLONGITUDE\tSPECIES_CODE\tSPECNAME\tNOM_D_ESPECE\tPOPULATION_TYPE_ID\tPOPULATION_TYPE_DESC\tLENGTH_CATEGORY_ID\tLENGTH_CATEGORY_LABEL\tADV_LEVEL\tADV_CAUSE_ID\tADV_CAUSE_DESC\tGUIDE_YEAR\tGUIDE_LOCDESC\n")
f.write("\n".join(rows))
f.close()

elapsed_time = time.time() - start_time
print elapsed_time
