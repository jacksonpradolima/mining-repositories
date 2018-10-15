import pyspark

# Read Travis CI - Java Projects
travis = sqlContext.read.csv(
    "/mnt/NAS/japlima/mining-repositories/raw_data/travistorrent_8_2_2017_java_projects.csv", header="true", inferSchema="true")

# Make the data available as a SQL table
travis.registerTempTable("travis_java")

# Read refactorings
refactorings = sqlContext.read.json(
    "/mnt/NAS/japlima/mining-repositories/raw_data/data_refactorings.json", multiLine=True)

# this creates a view of the json dataset
refactorings.createOrReplaceTempView("refactorings")

# Filter the projects that we have the refactorgins
refactorings_enabled = sqlContext.sql(
    """SELECT * FROM travis_java WHERE lower(gh_project_name) in (SELECT DISTINCT LOWER(REPLACE(REPLACE(repository, 'https://github.com/', ''), '.git', '')) gh_project FROM refactorings)""").toPandas()
dfrefactorings = spark.createDataFrame(refactorings_enabled)
dfrefactorings.registerTempTable("refactorings_enabled")

# Save the filter in a new file
refactorings_enabled.to_csv(
    "/mnt/NAS/japlima/mining-repositories/raw_data/travistorrent_8_2_2017_java_projects_enabled_refactorings.csv", sep=',', encoding='utf-8')
