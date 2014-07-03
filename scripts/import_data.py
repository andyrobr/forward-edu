#!/usr/bin/env python
import sys
from pymongo import MongoClient
import json
import urllib2

#import the school name and address into school_info collections in MongoDB
def school_info():

	#connects to the MongoDB
	client = MongoClient()
	db = client.schools
	school_collection = db.school_info
	report_collection = db.yearly_report

	header = ["School Name"]

	file_name = "2012_2013_HS_PR_Results_2014_01_16.txt"

	school_info = {}
	offset = {}

	#get the name of all high schools
	with open(file_name) as f:

		#iterate through every line in the file
		for index, line in enumerate(f):
			fields = line.split('\t')

			if index == 0: 
				continue

			if index == 1:

				for field in header:
					offset[field] = fields.index(field)

			else:
				school_name = fields[offset['School Name']]
				school_info[school_name.upper()] = True
	
	file_name = "schools.txt"

	header = [
    'Location Name',
    'Primary Address',
    'City',
    'State Code',
    'Zip',
    'Principal Phone Number']
	
	offset = {}

	with open(file_name) as e:
		
		#iterate through every line of the file
		for index, line in enumerate(e):

			fields = line.split('\t')

			# extracts the header and store the index into offset
			if index == 0:

				for field in header:
					offset[field] = fields.index(field)

			#check if the school name is in the school_info dict
			#if it is in the dictionary, it is a high school		
			else:
				school_name = fields[offset['Location Name']].upper()

				school_name = school_name.replace("\"","")

				school_address = fields[offset['Primary Address']]
				school_city = fields[offset['City']]
				school_state = fields[offset['State Code']]
				school_zip = fields[offset['Zip']]
				school_principal_number = fields[offset['Principal Phone Number']]

				if school_name in school_info:
					
					post = {"name": school_name, "address": { "street": school_address, "city" : school_city, "state": school_state, "zip" : school_zip} ,  "principal_phone_number": school_principal_number}
					school_collection.insert(post)
					report_collection.insert(post)

#stores the progress report grade into MongoDB
def progress_report_grade(file_name):

	#connects to MongoDB
	client = MongoClient()
	db = client.schools
	report_collection = db.yearly_report

	header = ["School Name", "Progress Grade"]

	year_number = file_name.split('_')[1]

	if year_number == "2011":
		header = ["School", "Progress Grade"]

	offset = {}

	#iterate through every line and add the progress report into MongoDB
	with open(file_name) as f:

		for index,line in enumerate(f):

			fields = line.split('\t')

			if index == 0:
				continue

			if index == 1:

				for field in header:
					offset[field] = fields.index(field)

			else:

				if year_number == "2011":
					school_name = fields[offset["School"]].upper()
				else:
					school_name = fields[offset['School Name']].upper()
				
				school_progress_grade = fields[offset['Progress Grade']]
				progress_grade = "progress_grade." + year_number
				report_collection.update({"name": school_name}, {"$set": { progress_grade: school_progress_grade}})

#stores the SAT result for each school into their MongoDB document
def sat_result(url, year_number):
	
	#connects to MongoDB
	client = MongoClient()
	db = client.schools
	report_collection = db.yearly_report

	#loads the json object
	sat = urllib2.urlopen(url)
	sat_json = sat.read()
	sat_data = json.loads(sat_json)

	reading = "sat_critical_reading_avg_score" if year_number == 2012 else "critical_reading_mean"
	math = "sat_math_avg_score" if year_number == 2012 else "mathematics_mean"
	writing = "sat_writing_avg_score" if year_number == 2012 else "writing_mean"

	#iterate through every school and add SAT data into MongoDB
	for i in sat_data:
		
		school_name = i["school_name"].upper()
		
		reading_avg = int(i[reading]) if reading in i and i[reading].isdigit() else -1

		math_avg = int(i[math]) if math in i  and i[math].isdigit() else -1
		writing_avg = int(i[writing]) if writing in i and i[math].isdigit() else -1

		sat_result_reading = "sat_result.reading." + str(year_number) 
		sat_result_math = "sat_result.math." + str(year_number)
		sat_result_writing = "sat_result.writing." + str(year_number)

		report_collection.update({"name": school_name},{"$set":{sat_result_reading: reading_avg, sat_result_math: math_avg, sat_result_writing: writing_avg}})


if __name__ == "__main__":

	client = MongoClient()
	db = client.schools
	db.connection.drop_database('schools')

	school_info()    
	progress_report_grade("2010_2011_HS_PR_Results_2013_10_25.txt")
	progress_report_grade("2011_2012_HS_PR_Results_2013_7_10.txt")
	progress_report_grade("2012_2013_HS_PR_Results_2014_01_16.txt") 
	
	sat_result("http://data.cityofnewyork.us/resource/zt9s-n5aj.json", 2010)
	sat_result("http://data.cityofnewyork.us/resource/f9bf-2cp4.json", 2012)
	         
