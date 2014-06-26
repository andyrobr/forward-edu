#!/usr/bin/env python
import sys
from pymongo import MongoClient


#connects to the MongoDB
client = MongoClient()
db = client.schools
collection = db.school_info


if len(sys.argv) == 1:
    print('Usage: %s schools.csv' % sys.argv[0])
    sys.exit(1)


headers = ["SCHOOL NAME"]

headers2 = [
    'Location Code',
    'Location Name',
    'Location Category Description',
    'Primary Address',
    'City',
    'State Code',
    'Zip',
    'Principal Phone Number'
]


offset = {}
school_info = {}

#opens the first file
with open(sys.argv[1]) as f:


    count  = 0;
    for index, line in enumerate(f):
        fields = line.split('\t')
        
        if index == 0:

            for field in headers:
               offset[field] = fields.index(field)
        
        #store all the school names into a school_info dictionary
        else:
            count +=1
            school_name = fields[offset['SCHOOL NAME']]
            school_name = school_name.lower()
            school_info[school_name] = True

offset = {}

#opens the second file
with open(sys.argv[2]) as e:
    count = 0
    for index, line in enumerate(e):

        fields = line.split('\t')

        if index == 0:

            for field in headers2:
                offset[field] = fields.index(field)
    
        #check if the school name is in the school_info dictionary
        #if it is in the dictionary, store it into MongoDB
        else:
            school_name = fields[offset['Location Name']]
            school_name = school_name.lower()
            school_address = fields[offset['Primary Address']]
            phone_number = fields[offset['Principal Phone Number']]

            if school_name in school_info:

                post = {"School_Name" : school_name, "School_Address" : school_address, "Principal_Phone_Number" : phone_number}
                
                collection.insert(post)

                    #count +=1
                school_info[school_name] = school_address
                    #print '%s        %s' %(school_name, school_address)

'''                
for i in school_info:

    if school_info[i] == True:

        print i, school_info[i]
'''
