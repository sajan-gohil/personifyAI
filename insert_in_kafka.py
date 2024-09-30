import os
import sys
import json
import openai
import datetime
import time
import base64
import requests
import traceback
from kafka import KafkaProducer
from urllib.parse import urlparse
from fetch_reddit_data import get_client, fetch_subreddit
import dotenv
dotenv.load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = openai.OpenAI()

# Kafka Configuration
KAFKA_TOPIC = 'data2'
KAFKA_SERVER = '0.0.0.0:9092'

# Supported image extensions
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']

# Initialize Kafka producer
producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER,
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        file_name = os.path.basename(urlparse(image_url).path)
        with open(file_name, 'wb') as f:
            f.write(response.content)
        return file_name
    return None

def get_image_description(image_path):
    def encode_image(image_path):
      with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    base64_image = encode_image(image_path)
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    payload = {
      "model": "gpt-4o-mini",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "What’s in this image? Give a brief description and comma separated keyword string."
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
              }
            }
          ]
        }
      ],
      "max_tokens": 50
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    # print(response.json())
    try:
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        traceback.print_exc()
        return ""

def process_json_object(json_obj):
    # Check if the 'thumbnail' key exists and ends with an image extension
    thumbnail_url = json_obj.get('thumbnail', '')
    if any(thumbnail_url.endswith(ext) for ext in IMAGE_EXTENSIONS):
        print(f"Downloading image from {thumbnail_url}")
        image_path = download_image(thumbnail_url)
        if image_path:
            print(f"Image downloaded as {image_path}. Generating description.")
            description = get_image_description(image_path)
            json_obj['image_description'] = description
            json_obj['_metadata'] = str(datetime.datetime.now())
            json_obj['timestamp'] = str(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z'))
            # Send the modified JSON object to Kafka

            producer.send(KAFKA_TOPIC, json.dumps(json_obj))
            producer.flush()
            print(f"JSON object with image description sent to Kafka topic '{KAFKA_TOPIC}'")

            # Clean up the downloaded image
            os.remove(image_path)
        else:
            print(f"Failed to download image from {thumbnail_url}")
    else:
        print("No valid thumbnail found or unsupported image format")

if __name__ == "__main__":
    # Example JSON object
    reddit_client = get_client()
    data = fetch_subreddit(reddit_client, "sneakers")
    for i in data:
        time.sleep(2)
        # print(data[2])
        process_json_object(i)