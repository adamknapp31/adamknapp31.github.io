from kafka import KafkaConsumer
from collect_telemetry import *

def setup_kafka_consumer():
    consumer = KafkaConsumer(
        'movielog24',
        bootstrap_servers=['localhost:9092'],
        enable_auto_commit=True
    )

    return consumer

def preprocess_data(data):
    # data preprocessing logic here
    data = data.strip().split(',')
    return data  # For simplicity, we'll just return the data as is

def main():
    consumer = setup_kafka_consumer()
    count = 0
    while True:
        try:
            for message in consumer:
                count += 1
                value = message.value.decode()
                preprocessed_data = preprocess_data(value)
                log_data(preprocessed_data)

                if count % 100000 == 0:
                    print(f"Processed {count} messages")
        except KeyboardInterrupt:
            consumer.close()
            print("Closing Kafka Consumer...")
            break

if __name__ == "__main__":
    main()