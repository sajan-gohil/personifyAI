import logging
import sys

import pathway as pw
import yaml
from dotenv import load_dotenv
from pathway.udfs import DiskCache, ExponentialBackoffRetryStrategy
from pathway.xpacks.llm import embedders, llms, parsers, splitters
from pathway.xpacks.llm.question_answering import BaseRAGQuestionAnswerer
from pathway.xpacks.llm.vector_store import VectorStoreServer

# To use advanced features with Pathway Scale, get your free license key from
# https://pathway.com/features and paste it below.
# To use Pathway Community, comment out the line below.
# pw.set_license_key("demo-license-key-with-telemetry")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

load_dotenv()

def get_data_sources(kafka_topic):
    rdkafka_settings = {
        "bootstrap.servers": "localhost:9092",
        "security.protocol": "plaintext",
        "group.id": "0",
        "session.timeout.ms": "6000",
        # "sasl.username": "username",
        # "sasl.password": "********",
    }

    source = pw.io.kafka.read(
        rdkafka_settings,
        topic=kafka_topic,
        # schema=InputSchema,
        # format="csv",
        # autocommit_duration_ms=1000
    )
    return source

def run():
    # with open(config_file) as config_f:
    #     configuration = yaml.safe_load(config_f)

    embedder = embedders.OpenAIEmbedder(
        model="text-embedding-3-small",
        cache_strategy=DiskCache(),
    )

    chat = llms.OpenAIChat(
        model="gpt-4o-mini",
        retry_strategy=ExponentialBackoffRetryStrategy(max_retries=3),
        cache_strategy=DiskCache(),
        temperature=0.1,
    )
    kafka_source = get_data_sources("data2")
    print("got source", flush=True)
    doc_store = VectorStoreServer(
        kafka_source,  # pw.io.kafka.read
        embedder=embedder,  #  embedders.OpenAIEmbedder
        splitter=splitters.TokenCountSplitter(max_tokens=400),
        parser=parsers.ParseUnstructured(),
    )
    print("starting app", flush=True)
    doc_store.run_server(host="0.0.0.0", port="8090", with_cache=False, terminate_on_error=True)
    print("started app", flush=True)
    # rag_app = BaseRAGQuestionAnswerer(llm=chat, indexer=doc_store)
    # rag_app.build_server(host="0.0.0.0", port="8090")
    # rag_app.run_server(with_cache=True, terminate_on_error=False)


if __name__ == "__main__":
    run()