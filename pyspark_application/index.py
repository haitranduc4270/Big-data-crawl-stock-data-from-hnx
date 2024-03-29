from constant.constant import kafka_bootstrap_servers, kafka_topic, elasticsearch_time_format
import os.path
from os import path
import json
from dependencies import spark, kafka_consumer
from services import service
from services.company import get_company_info
from datetime import datetime, timedelta
from dependencies.mongo import save_df_to_mongodb


def start_app():
    spark_sess = spark.start_spark()

    kafka_consumer_instance = (kafka_consumer
                               .start_kafka_consumer(kafka_bootstrap_servers, kafka_topic))

    while 1:
        # Nếu chưa có file chứa thông tin các công ty trên sàn của ngày hôm đó thì lấy và ghi vào data/stock.json
        if not path.exists('data/stock.json'):
            get_company_info()
        else:
            with open('data/stock.json', 'r') as openfile:
                stock_info = json.load(openfile)
            if datetime.now() + timedelta(hours=7) > datetime.strptime(
                    stock_info['time_stamp'], elasticsearch_time_format):
                get_company_info()

            else:
                print('Listen to kafka')
                for msg in kafka_consumer_instance:
                    service.start(
                        msg, stock_info['data'], spark_sess, save_df_to_mongodb)


if __name__ == '__main__':
    try:
        print('Pyspark application stared')
        start_app()
    except Exception as e:
        print(e)
