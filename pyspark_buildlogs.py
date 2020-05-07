import os
import pyspark
import requests
import tarfile
import utils.context as context
import zipfile

from clint.textui import progress
from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.session import SparkSession
from pyspark.sql.types import *


def extract_file(path, to_directory='.'):
    if path.endswith('.zip'):
        opener, mode = zipfile.ZipFile, 'r'
    elif path.endswith('.tar.gz') or path.endswith('.tgz'):
        opener, mode = tarfile.open, 'r:gz'
    elif path.endswith('.tar.bz2') or path.endswith('.tbz'):
        opener, mode = tarfile.open, 'r:bz2'
    else:
        raise ValueError(
            "Could not extract {} as no appropriate extractor is found".format(path))

    cwd = os.getcwd()
    os.chdir(to_directory)

    try:
        file = opener(path, mode)
        try:
            file.extractall()
        finally:
            file.close()
    finally:
        os.chdir(cwd)


sc = context.create_sc()
sqlContext = SQLContext(sc)
spark = SparkSession(sqlContext)

buildlogsdir = "/mnt/NAS/japlima/mining-repositories/raw_data/buildlogs"
if not os.path.exists(buildlogsdir):
    os.makedirs(buildlogsdir)

refactorings_enabled = sqlContext.read.csv(
    "/mnt/NAS/japlima/mining-repositories/raw_data/travistorrent_8_2_2017_java_projects_refactorings.csv", header="true", inferSchema="true")

# Make the data available as a SQL table
refactorings_enabled.registerTempTable("refactorings_enabled")

result = sqlContext.sql(
    "select distinct gh_project_name AS repo from refactorings_enabled").toPandas()

for index, row in result.iterrows():
    repo = row['repo']

    url = "https://travistorrent.testroots.org/buildlogs/20-12-2016/{}.tgz".format(
        repo.replace("/", "%40"))

    response = requests.head(url)

    # if link is valid download the file
    if response.status_code == 200:
        repoL = repo.replace("/", "@")
        buildlogfile = "{}/{}.tgz".format(buildlogsdir, repoL)

        if not os.path.exists(buildlogfile) and not os.path.exists("/mnt/NAS/japlima/mining-repositories/raw_data/buildlogs/"+repoL):
            print("\n[DOWNLOADING] {} build logs".format(repo))

            r = requests.get(url, stream=True)

            with open(buildlogfile, 'wb') as f:
                total_length = int(r.headers.get('content-length'))
                for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
                    if chunk:
                        f.write(chunk)
                        f.flush()

            extract_file(
                buildlogfile, "/mnt/NAS/japlima/mining-repositories/raw_data/buildlogs")

            if os.path.exists(buildlogfile):
                os.remove(buildlogfile)
            print("\n")
        else:
            print("[SKIPPING]", repo, "- build logs already exists")
    else:
        print("[SKIPPING]", repo, "- url not found")
