# Databricks notebook source
# MAGIC %md
# MAGIC ### This workbook monitors access tokens and sends an email to DataBricks Admins when they are 10 days or less from expiring
# MAGIC * Created:  6/29/2021
# MAGIC * Author:   Bill Ritchie
# MAGIC  

# COMMAND ----------

# DBTITLE 1,Getting a list of access tokens
import requests
import json
import time
import datetime
import math
import os

DOMAIN = os.environ.get('API_DOMAIN') 

# This token is coming from a Secret Scope
TOKEN = dbutils.secrets.get(scope = "ADM-CREDENTIALS", key = "NONPROD_TOKEN") 

# This gives a JSON-based response containing details for each token in the environment
response = requests.get(
  'https://%s/api/2.0/token-management/tokens' % (DOMAIN),
  headers={'Authorization': 'Bearer %s' % (TOKEN)},
  )

if response.status_code == 200:
  # Puts the JSON data in a dictionary
  json_dict = response.json()
  test_string = json.dumps(json_dict)
  
  # Gets start and stop index to use for processing data in the next cell
  start_index = 0
  stop_index = (test_string.count('token_id')) 

else:
  print("Error getting Token data: %s: %s" % (response.json()["error_code"], response.json()["message"]))

# COMMAND ----------

# DBTITLE 1,Loop through the access token list and  if it fails the expire date validation, add variables to lists
#Initialize token list
token_list = []
#Initialized token comments list
comment_list = []

i = 0

# Process records less than the record count
while i < stop_index:
  
  # Get comment element for the token comment  list
  token_comment = json_dict['token_infos'][i]['comment']
  
  # Get expire date element for the token list
  token_exp_date = json_dict['token_infos'][i]['expiry_time']
  
  # Only process token data for tokens that do not have an "unlimited" expire date (expire date not equal to -1)
  if str(token_exp_date) != "-1":
     
  # --Debug statements
     #print (token_comment)
     #print (token_exp_date)
      
  # Add expire date element to token list    
     token_list.append(str(token_exp_date))
  # Add comment element to comment list 
     comment_list.append(str(token_comment))
    
  i += 1


# COMMAND ----------

# DBTITLE 1,Merge list values into a dictionary
# --Debug statements
#print(token_list)
#print(comment_list)

# Using dictionary comprehension to convert lists to dictionaries
work_dict1 = {token_list[i]: comment_list[i] for i in range(len(token_list))}
work_dict2 = {"m" + token_list[i]: "no_mail" for i in range(len(token_list))}
work_dict3 = {"d" + token_list[i]: "no_date" for i in range(len(token_list))}
 
# --Debug statement
#print ("Resultant dictionary is : " +  str(work_dict1))

# COMMAND ----------

# DBTITLE 1,Get system date-time in milliseconds, then  add email indicator to dictionary
# Convert system date to millisconds (epoch time)
sysdate_in_milliseconds = int(round(time.time() * 1000))

# Get the number of millisecobs for 10 days
ten_days_in_milliseconds = 864000000

# --Debug statements
#print(sysdate_in_milliseconds)
#print(ten_days_in_milliseconds)

# Loop through the dictioary
for key,value in work_dict1.items():
  dict_key = key
  dict_value = value

# Get a value for:  token expire date(in milliseconds) - ten days (in milliseconds)
  test_value = int(dict_key) - ten_days_in_milliseconds

# --Debug statements
  #print(dict_key)
  #print(test_value)

# Covert token expire date (in milli seconds) to a date/time timestamp
  test_date = datetime.datetime.fromtimestamp(int(dict_key) / 1000)

  # --Debug statement
  #print(test_date)
  
# All of this is in milliseconds:  evaluate if [sysdate > (token expire date - 10 days)] AND [sysdate < token expire date]
# If the statement evaluates as "TRUE",  populate the work dictionaries
  if  (sysdate_in_milliseconds > test_value) and (sysdate_in_milliseconds < int(dict_key)):
    
# Add a record to "send mail" dictionary - to indicate there is data for the expired token email   
     work_dict2["m" + dict_key] = "send_mail"
# Add a record to "expire date " dictionary - which has a formatted expire date string
     work_dict3["d" + dict_key] = test_date.strftime("%m/%d/%Y %H:%M:%S")





# COMMAND ----------

# DBTITLE 1,Read the dictionaries and create the token email data
#Initialize token HTML data string
token_data=''

#Intial flag to indicate if expired token email should be sent
send_flag = "N"

#Loop through expired token dictionary
for main_key in work_dict1:
# Evaluate if token data will be included in the expired token email.  If True,  set send flag = "Y" -  whec will tell the send email process to generate an email
  if (work_dict2.get("m" + main_key) ) == "send_mail":
      send_flag = "Y"
      token_data += "<blockquote>" + "Token Comment: " + work_dict1.get(main_key)+ "<br>" + "Expire Date: " + work_dict3.get("d" + main_key) + "<br> <br>" + "</blockquote>"
      
# --Debug statement
#print (token_data)
    

# COMMAND ----------

# DBTITLE 1,Import  Send Email Module
# MAGIC %run Admin/Send-Mail-Module

# COMMAND ----------

# DBTITLE 1,***  Build the Email Title ***
body_html = [
  "<h1>The Tokens listed below will expire soon - Please reset them before they expire.</h1>"
]


# COMMAND ----------

# DBTITLE 1,*** Append token detail to the email body
body_html.extend([str(token_data)])


# COMMAND ----------

# DBTITLE 1,***  Build email metadata ***
# "From" address for email
from_addr = "Databricks.RAC@Rentacenter.com"
# "To address for email"
to_addrs =  ["DataBricks-Admins@rentacenter.com"]
# Subject line for email
ENVIRONMENT = os.environ.get('ENVIRONMENT')
env = ENVIRONMENT
if env != "QA":
   env = ENVIRONMENT.capitalize() 

subject = "Data Bricks " + env +  ": Access Tokens Due to Expire"

# Only set this value = "Y" if you want to display the email body HTML result for debug or other purposes
display_html = "N"

# These values are empty/null
attachments=[]
cc=[]
bcc=[]

# COMMAND ----------

# DBTITLE 1,Send an email
process_email(send_flag,display_html,from_addr, to_addrs, subject, body_html, attachments,cc, bcc)
