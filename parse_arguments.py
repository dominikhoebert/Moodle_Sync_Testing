import argparse
def parse():
    parser = argparse.ArgumentParser(
        description="Reads in an EXCEL or CSV file and creates Student Groups in Moodle"
    )
    parser.add_argument(
        "file",
        help="MANDATORY: .xlsx or .csv file",
        type=str
    )
    parser.add_argument(
        "-i", "--course-id",
        help="Moodle course id (can be found in the url)",
        dest="course_id",
        type=int
    )
    parser.add_argument(
        "-t", "--sheet",
        help="Sheet name or number (Excel only)",
        dest="sheet",
        type=str,
        default="0"
    )
    parser.add_argument(
        "-c", "--credentials",
        help="JSON file including url, user, password and service",
        dest="credentials",
        type=str,
    )
    parser.add_argument(
        "-u", "--username",
        help="Moodle username",
        dest="username",
        type=str,
    )
    parser.add_argument(
        "-p", "--password",
        help="Moodle password",
        dest="password",
        type=str,
    )
    parser.add_argument(
        "-s", "--servicename",
        help="Moodle Servce Name",
        dest="servicename",
        type=str,
    )
    parser.add_argument(
        "-l", "--url",
        help="Moodle Server URL",
        dest="url",
        type=str
    )
    parser.add_argument(
        "-n", "--col-name",
        help="Column Name of Moodle ID or Email",
        dest="col_name",
        type=str,
    )
    parser.add_argument(
        "-g", "--group-col",
        help="Column Name of Group name",
        dest="group_col",
        type=str,
    )
    parser.add_argument(
        "-a", "--add-students",
        help="automatically add students to course when set",
        dest="add_students",
        action="store_true",
    )
    parser.add_argument(
        "-r", "--preview",
        help="Previews students and groups without actually doing anything",
        dest="preview",
        action="store_true",
    )
    parser.add_argument(
        "-o", "--no-output",
        help="hide output",
        dest="no_output",
        action="store_true",
    )
    parser.add_argument(
        "-d", "--dialog",
        help="dialog mode, no arguments needed",
        dest="dialog",
        action="store_true",
    )
    args = parser.parse_args()
    return args