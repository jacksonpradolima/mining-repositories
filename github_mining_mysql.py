import pymysql.cursors

from github import Github


def is_travis_project(slug):
    try:
        repo = g.get_repo(slug)
        content = repo.get_contents(".travis.yml")
        # print(content.url)
        return True
    except Exception as e:
        return False


# Github instance using an access token
g = Github("b43b59e5a8d621516c3653b52b30f3df112a0f11")

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='aizeejae',
                             db='refactoring',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

try:
    with connection.cursor() as cursor:
        # Read a single record
        # sql = "SELECT distinct `ProjectName`, `UrlProject` FROM `view_details` WHERE `ProjectName` like '%{0}%'".format("aws")
        sql = "SELECT distinct `ProjectName`, `UrlProject` FROM `view_details` LIMIT 10"
        cursor.execute(sql)
        result = cursor.fetchall()  # fetchall
        # print(result)

        split_project = [p["ProjectName"].split("_") for p in result]

        for sp in split_project:
            print(
                "UserName: {} - ProjectName: {} - Travis? {}".format(sp[0], sp[1], is_travis_project("{}/{}".format(sp[0], sp[1]))))
finally:
    connection.close()
