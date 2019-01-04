#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# ./list_your_courses.py
#
# with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program
#
# Can also be called with an alternative configuration file:
# ./list_your_courses.py --config config-test.json
#
# 
# G. Q. Maguire Jr.
#
# 2017.02.27
# revised on 2019.01.04
#

import requests, time
import pprint
import optparse
import sys
import json

#############################
###### EDIT THIS STUFF ######
#############################

global baseUrl	# the base URL used for access to Canvas
global header	# the header for all HTML requests
global payload	# place to store additionally payload when needed for options to HTML requests

# Based upon the options to the program, initialize the variables used to access Canvas gia HTML requests
def initialize(options):
       global baseUrl, header, payload

       # styled based upon https://martin-thoma.com/configuration-files-in-python/
       if options.config_filename:
              config_file=options.config_filename
       else:
              config_file='config.json'

       with open(config_file) as json_data_file:
              configuration = json.load(json_data_file)
              access_token=configuration["canvas"]["access_token"]
              baseUrl="https://"+configuration["canvas"]["host"]+"/api/v1/"

       header = {'Authorization' : 'Bearer ' + access_token}
       payload = {}


def list_your_courses():
       courses_found_thus_far=[]
       # Use the Canvas API to get the list of all of your courses
       # GET /api/v1/courses

       url = baseUrl+'courses/'
       if Verbose_Flag:
              print("url: {}".format(url))

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              print("result of getting courses: {}".format(r.text))

       if r.status_code == requests.codes.ok:
              page_response=r.json()

       for p_response in page_response:  
              courses_found_thus_far.append(p_response)

       # the following is needed when the reponse has been paginated
       # i.e., when the response is split into pieces - each returning only some of the list of modules
       # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
       while r.links['current']['url'] != r.links['last']['url']:  
              r = requests.get(r.links['next']['url'], headers=header)  
              if Verbose_Flag:
                     print("result of getting courses for a paginated response: {}".format(r.text))
              page_response = r.json()  
              for p_response in page_response:  
                     courses_found_thus_far.append(p_response)

       return courses_found_thus_far

def main():
       global Verbose_Flag

       parser = optparse.OptionParser()

       parser.add_option('-v', '--verbose',
                         dest="verbose",
                         default=False,
                         action="store_true",
                         help="Print lots of output to stdout"
       )
       parser.add_option("--config", dest="config_filename",
                  help="read configuration from FILE", metavar="FILE")

       options, remainder = parser.parse_args()

       Verbose_Flag=options.verbose
       if Verbose_Flag:
              print("ARGV      : {}".format(sys.argv[1:]))
              print("VERBOSE   : {}".format(options.verbose))
              print("REMAINING : {}".format(remainder))
              print("Configuration file : {}".format(options.config_filename))

       initialize(options)

       output=list_your_courses()
       if (output):
              pprint.pprint(output, indent=4)

if __name__ == "__main__": main()

