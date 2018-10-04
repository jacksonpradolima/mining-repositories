import pymysql.cursors
import utils.GitHubUtils as GitHubUtils
import utils.JsonUtils as JsonUtils

from itertools import groupby
from operator import itemgetter

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='aizeejae',
                             db='refactoring',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        sql = """SELECT distinct `ProjectName` FROM `view_details`"""
        cursor.execute(sql)
        dataset = cursor.fetchall()

        # Filter the repositories that contains Travis CI
        repos_travis = [
            x['ProjectName'] for x in dataset if GitHubUtils.is_travis_project(x["ProjectName"].replace("_", "/"))]

        # repos_travis = [x['ProjectName'] for x in dataset]

        # Filter the database with repositories that contanis Travis CI
        sql = """SELECT `Repository` AS repository,
                        `CommitID` AS sha1,
                        `CommitterName` AS author,
                        `CommitDate` AS time,
                        `RefactoringType` AS type,
                        `RefactoringDetail` AS description
                 FROM `view_details`
                 WHERE `ProjectName` IN ({}) ORDER BY `Repository`, `CommitID`""".format(
            ','.join("'{}'".format(x) for x in repos_travis))

        cursor.execute(sql)
        dataset = cursor.fetchall()

        result = []
        grouper = itemgetter("repository", "sha1")
        for k, v in groupby(sorted(dataset, key=grouper), grouper):
            json_dict = {}
            data = []
            for i in v:
                json_dict["id"] = 0
                json_dict["repository"] = i["repository"]
                json_dict["sha1"] = i["sha1"]
                json_dict["author"] = i["author"]
                json_dict["time"] = i["time"]

                # I can have multiple refactoring for a repository/commit
                tmp_dict = {}
                tmp_dict["type"] = i["type"]
                tmp_dict["description"] = i["description"]
                data.append(tmp_dict)

            # Save the refactoring found
            json_dict["refactorings"] = data

            # Save the repository/commit info
            result.append(json_dict)

        # Save the dataset in json format
        JsonUtils.save_data("data/refactorings_kessentini_travis.json", result)
finally:
    connection.close()
