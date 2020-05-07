import pyspark

from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.types import *


def create_sc():
    sc_conf = SparkConf()
    sc_conf.setAppName("travis-mining")
    sc_conf.set('spark.cores.max', '40')
    sc_conf.set("spark.driver.memory", "50g")
    sc_conf.set("spark.driver.maxResultSize", "3g")
    sc_conf.set('spark.executor.memory', '8g')
    sc_conf.set('spark.executor.cores', '4')
    sc_conf.set('spark.logConf', True)
    sc_conf.set("spark.memory.offHeap.enabled", True)
    sc_conf.set("spark.memory.offHeap.size", "16g")
    sc_conf.set("spark.speculation", False)

    # print(sc_conf.getAll())

    # In Jupyter you have to stop the current context first
    # sc.stop()
    sc = SparkContext.getOrCreate(conf=sc_conf)

    return sc
