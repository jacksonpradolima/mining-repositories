import pyspark
import utils.context as context  # init the main variables

from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.functions import col
from pyspark.sql.functions import lower
from pyspark.sql.session import SparkSession
from pyspark.sql.types import *

sc = context.create_sc()
sqlContext = SQLContext(sc)
spark = SparkSession(sqlContext)

# Read Travis Snapshot
# travisStreamRaw = sqlContext.read.csv("/mnt/NAS/japlima/mining-repositories/raw_data/travistorrent_8_2_2017.csv", header = "true", inferSchema = "true")

# travisStreamRaw.registerTempTable("travis_all")

# # Filter Travis Snapshot looking for Java repositories using sql
# sfJava = sqlContext.sql("""SELECT * FROM travis_all WHERE lower(gh_lang) = "java" """).toPandas()

# Save the filter in a new file (Temp)
# sfJava.to_csv("/mnt/NAS/japlima/mining-repositories/raw_data/travistorrent_8_2_2017_java_projects.csv", index=False)

travis = sqlContext.read.csv(
    "/mnt/NAS/japlima/mining-repositories/raw_data/travistorrent_8_2_2017_java_projects.csv", header="true", inferSchema="true")

# # Make the data available as a SQL table
travis.registerTempTable("travis_java")

refactorings = sqlContext.read.json(
    "/mnt/NAS/japlima/mining-repositories/raw_data/data_refactorings.json", multiLine=True)

# this creates a view of the json dataset
refactorings.createOrReplaceTempView("refactorings")

# get the projects that we have the refactorings
refac_projs = sqlContext.sql(
    """SELECT DISTINCT LOWER(REPLACE(REPLACE(repository, 'https://github.com/', ''), '.git', '')) gh_project
     FROM refactorings""")

refac_projs.registerTempTable("refac_projs")

# filter the Snapshot
refactorings_enabled = sqlContext.sql(
    """SELECT t.* FROM travis_java t, refac_projs r WHERE lower(t.gh_project_name) = r.gh_project""").toPandas()

# Remove strange column
refactorings_enabled = refactorings_enabled.drop(['_c0'], axis=1)

# save without index ("_c0")
refactorings_enabled.to_csv(
    "/mnt/NAS/japlima/mining-repositories/raw_data/travistorrent_8_2_2017_java_projects_refactorings.csv", index=False)
