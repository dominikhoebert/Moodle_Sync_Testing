import moodle_api
import pandas as pd

"""
[SSL: CERTIFICATE_VERIFY_FAILED] Error: https://stackoverflow.com/questions/51925384/unable-to-get-local-issuer-certificate-when-using-requests-in-python
Install certifi; copy cacert.pem aus certifi folder
"""


class MoodleSync:
    def __init__(self, url: str, key: str):
        moodle_api.URL = url
        moodle_api.KEY = key

    def get_recent_courses(self):
        response = moodle_api.call('core_course_get_recent_courses')
        return {c['fullname']: {'id': c['id']} for c in response}

    def get_course_modules(self, course_id):
        response = moodle_api.call('core_course_get_contents', courseid=course_id)
        modules = {}
        for section in response:
            for module in section['modules']:
                if 'modname' in module:
                    if module['modname'] == 'assign':
                        modules[module['name']] = {'id': module['id']}
        return modules

    def get_gradereport_of_course(self, course_id):
        response = moodle_api.call('gradereport_user_get_grade_items', courseid=course_id)
        graditems = {}
        for graditem in response['usergrades'][0]['gradeitems']:
            graditems[graditem['itemname']] = graditem['id']

        df = pd.DataFrame(columns=['userfullname', 'userid'] + list(graditems.keys()))

        for student in response['usergrades']:
            grades = {'userfullname': student['userfullname'], "userid": student['userid']}
            for gradeitem in student['gradeitems']:
                grades[gradeitem['itemname']] = gradeitem['gradeformatted']
            df = df.append(grades, ignore_index=True)

        df = df.rename(columns={None: 'Kurs', 'userfullname': 'Schüler'})
        return df

    def get_student_info(self, userlist):
        """
        Takes an array of dict with key userid=int, courseid=int
        Returns a DataFrame with user info id, fullname, email, groups (all groups as joined str)

        :param userlist:
        :return DataFrame:
        """
        response = moodle_api.call('core_user_get_course_user_profiles', userlist=userlist)
        user_df = pd.DataFrame(columns=['id', 'fullname', 'email', 'groups'])
        for student in response:
            groups_list = []
            for group in student["groups"]:
                groups_list.append(group["name"])
            groups = ""
            if len(groups_list) > 0:
                groups = ",".join(groups_list)
            user_df = user_df.append(
                {"id": student["id"], "fullname": student["fullname"], "email": student["email"], "groups": groups},
                ignore_index=True)

        return user_df
