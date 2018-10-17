import pyspark
import utils.context as context

from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.session import SparkSession
from pyspark.sql.types import *

sc = context.create_sc()
sqlContext = SQLContext(sc)
spark = SparkSession(sqlContext)

# refactorings_enabled = sqlContext.read.csv(
#     "/mnt/NAS/japlima/mining-repositories/raw_data/travistorrent_8_2_2017_java_projects_enabled_refactorings.csv", header="true", inferSchema="true")

# # Make the data available as a SQL table
# refactorings_enabled.registerTempTable("refactorings_enabled")

# result = sqlContext.sql(
#     """select * from refactorings_enabled where lower(gh_project_name)= 'dspace/dspace'""")

# result.show()


refactorings_enabled = sqlContext.read.csv(
    "/mnt/NAS/japlima/mining-repositories/raw_data/travistorrent_8_2_2017_java_projects_refactorings.csv", header="true", inferSchema="true")

# Make the data available as a SQL table
refactorings_enabled.registerTempTable("refactorings_enabled")

refactorings_enabled.show(5, False)

result = sqlContext.sql(
    "select count(distinct gh_project_name) from refactorings_enabled")

# dfAll = spark.createDataFrame(sfP)
# dfAll.registerTempTable("dfAll")

print("Total of java projects found:")
result.show()

print("Soma jobs ids:")
result = sqlContext.sql(
    "select tr_job_id from refactorings_enabled")

result.show()
