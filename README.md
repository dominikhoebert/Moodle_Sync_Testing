# Moodle_Sync_Testing
 
Script reads in Excel or CSV with Students (and their emails or Mooodle IDs) and groupnames.
Script looks for Students in the course and adds them if they are not already in the course.
Then creates the groups and adds the students to the groups.

## Help

usage: main.py [-h] [-i COURSE_ID] [-t SHEET] [-c CREDENTIALS] [-u USERNAME]  
               [-p PASSWORD] [-s SERVICENAME] [-l URL] [-m MOODLEID_COL]  
               [-e EMAIL_COL] [-g GROUP_COL] [-a] [-r] [-o] [-d]  
               file  

Reads in an EXCEL or CSV file and creates Student Groups in Moodle  

positional arguments:  
  file                  MANDATORY: .xlsx or .csv file  

options:  
  -h, --help            show this help message and exit  
  -i COURSE_ID, --course-id COURSE_ID
                        Moodle course id (can be found in the url)  
  -t SHEET, --sheet SHEET
                        Sheet name or number (Excel only)  
  -c CREDENTIALS, --credentials CREDENTIALS
                        JSON file including url, user, password and service  
  -u USERNAME, --username USERNAME
                        Moodle username  
  -p PASSWORD, --password PASSWORD
                        Moodle password  
  -s SERVICENAME, --servicename SERVICENAME
                        Moodle Servce Name  
  -l URL, --url URL     Moodle Server URL  
  -m MOODLEID_COL, --moodle-id-col MOODLEID_COL
                        Column Name of Moodle ID  
  -e EMAIL_COL, --email-col EMAIL_COL
                        Column Name of Email  
  -g GROUP_COL, --group-col GROUP_COL
                        Column Name of Group name  
  -a, --add-students    automatically add students to course when set  
  -r, --preview         Previews students and groups without actually doing
                        anything  
  -o, --no-output       hide output  
  -d, --dialog          dialog mode, no arguments needed  



## TODO

- check for existing groups (needs core_group_get_course_groups)
- Docker image
