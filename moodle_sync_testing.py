import pandas as pd

from moodle_sync import MoodleSync
from pandas import DataFrame
from datetime import datetime
import random


class MoodleSyncTesting(MoodleSync):
    def __init__(self, url: str, username: str, password: str, service: str, course_id: int, students: DataFrame,
                 column_name: str, group_column_name: str):
        super().__init__(url, username, password, service)
        self.course_id = course_id
        self.students_original = students
        self.students = self.students_original
        self.column_name = column_name
        self.group_column_name = group_column_name
        self.right_on = self.get_right_on()
        self.group_names_to_id = None

    def get_right_on(self):
        if self.is_id_column():
            return "id_joined"
        elif self.is_email_column():
            return "email_joined"
        else:
            return None

    def join_enrolled_students(self):
        enrolled_students_df = self.get_enrolled_students(self.course_id)
        self.students = self.students_original.merge(enrolled_students_df, left_on=self.column_name,
                                                     right_on=self.right_on, how="left")

    def is_email_column(self) -> bool:
        return self.column_name in self.students.columns and self.students[self.column_name].str.contains("@").any()

    def is_id_column(self) -> bool:
        return self.column_name in self.students.columns and self.students[self.column_name].dtype == "int64"

    def clean_students(self):
        self.students = self.students[self.students["id_joined"].notnull()]
        self.students = self.students[self.students[self.group_column_name].notnull()]
        self.students = self.students[self.students[self.group_column_name] != ""]

    @property
    def group_names(self):
        return self.students[self.group_column_name].unique()

    def create_groups(self):
        groups = []
        group_ids = {}
        date_string = datetime.now().strftime("%Y%m%d")
        for g in self.group_names:
            group_id = date_string + str(random.randrange(100, 999))
            group_ids[g] = group_id
            groups.append(
                {"courseid": self.course_id, "name": g, "description": "", "idnumber": group_id})

        response = self.create_group(groups)
        self.group_names_to_id = {}
        for g in response:
            self.group_names_to_id[g["name"]] = g["id"]

    def add_students_to_groups(self):
        members = []
        for group_name, group_id in self.group_names_to_id.items():
            for index, row in self.students[self.students[self.group_column_name] == group_name].iterrows():
                members.append({"groupid": group_id, "userid": int(row["id_joined"])})

        self.add_students_to_group(members)

    def enroll_students_for_groups(self):
        not_enrolled_df = self.students[self.students["id_joined"].isnull()]
        if len(not_enrolled_df) > 0:
            if self.right_on == 'id_joined':
                not_enrolled_ids = not_enrolled_df[self.column_name].tolist()
            elif self.right_on == 'email_joined':
                emails = not_enrolled_df[self.column_name].tolist()
                response = self.get_user_by_email(emails)
                not_enrolled_ids = [s["id"] for s in response]
            else:
                return
            enrolments = []
            for id in not_enrolled_ids:
                enrolments.append({'roleid': 5, 'userid': id, 'courseid': self.course_id})  # 5 = student
            self.enroll_students(enrolments)


if __name__ == '__main__':
    import json

    with open("data/credentials.json", "r") as f:
        credentials = json.load(f)

    moodle_sync = MoodleSyncTesting(credentials["url"], credentials["user"], credentials["password"],
                                    credentials["service"], course_id=1309, students=pd.read_csv("data/test.csv"),
                                    column_name="email", group_column_name="groupname")

    moodle_sync.join_enrolled_students()
    moodle_sync.enroll_students_for_groups()
    moodle_sync.join_enrolled_students()
    moodle_sync.clean_students()
    moodle_sync.create_groups()
    moodle_sync.add_students_to_groups()