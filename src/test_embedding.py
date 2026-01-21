from openai import AzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("OPENAI_KEY"),
    azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
    api_version="2024-02-15-preview"
)

print("Using deployment:", os.getenv("EMBEDDING_MODEL"))

response = client.embeddings.create(
    model=os.getenv("EMBEDDING_MODEL"),
    input=["hello world"]
)

print(len(response.data[0].embedding))
