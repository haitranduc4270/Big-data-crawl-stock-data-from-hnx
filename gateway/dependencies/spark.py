import __main__

from os import environ, listdir, path
import json
from pyspark import SparkFiles
from pyspark.sql import SparkSession


def start_spark(app_name='my_spark_app', master='local[*]', jar_packages=[],
                files=[], spark_config={}):

    # detect execution environment
    flag_repl = not (hasattr(__main__, '__file__'))
    flag_debug = 'DEBUG' in environ.keys()

    if not (flag_repl or flag_debug):
        # get Spark session factory
        spark_builder = (
            SparkSession
            .builder
            .appName(app_name))
    else:
        # get Spark session factory
        spark_builder = (
            SparkSession
            .builder
            .master(master)
            .appName(app_name))

        # create Spark JAR packages string
        spark_jars_packages = ','.join(list(jar_packages))
        spark_builder.config('spark.jars.packages', spark_jars_packages)

        spark_files = ','.join(list(files))
        spark_builder.config('spark.files', spark_files)

        # add other config params
        for key, val in spark_config.items():
            spark_builder.config(key, val)

    # create session and retrieve Spark logger object
    spark_sess = spark_builder.getOrCreate()

    # get config file if sent to cluster with --files
    spark_files_dir = SparkFiles.getRootDirectory()
    config_files = [filename
                    for filename in listdir(spark_files_dir)
                    if filename.endswith('config.json')]

    if config_files:
        path_to_config_file = path.join(spark_files_dir, config_files[0])
        with open(path_to_config_file, 'r') as config_file:
            config_dict = json.load(config_file)
    else:
        config_dict = None

    return spark_sess, config_dict
