from kafka import KafkaConsumer
import json

# Kafka Configuration
KAFKA_TOPIC = 'data'
KAFKA_SERVER = 'localhost:9092'  # Adjust this if your Kafka server is on a different host or port

def main():
    # Create a Kafka consumer
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        auto_offset_reset='earliest',  # Start reading at the earliest message
        enable_auto_commit=True,        # Automatically commit offsets
        group_id='my-group',            # Consumer group ID
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))  # Deserialize JSON messages
    )

    print(f"Listening for messages on topic '{KAFKA_TOPIC}'...")

    try:
        for message in consumer:
            print(f"Received message: {message.value}")
            # You can perform additional processing on the message here
    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        # Clean up
        consumer.close()

if __name__ == "__main__":
    main()
