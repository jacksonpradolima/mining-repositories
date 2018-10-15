import pyspark

# Filter snapshot
travisStreamRaw = sqlContext.read.csv(
    "/mnt/NAS/japlima/mining-repositories/raw_data/travistorrent_8_2_2017.csv", header="true", inferSchema="true")
travisStreamRaw.registerTempTable("travis_all")

# Filter using sql projects that are not Java projects
sfJava = sqlContext.sql(
    """SELECT * FROM travis_all WHERE lower(gh_lang) = "java" """).toPandas()

# Save the filter in a new file
sfJava.to_csv("/mnt/NAS/japlima/mining-repositories/raw_data/travistorrent_8_2_2017_java_projects.csv",
              sep=',', encoding='utf-8')
