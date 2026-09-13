from pymongo import MongoClient
from app.config import MONGODB_URI

client = MongoClient(MONGODB_URI)

db = client["codebase_rag"]

repositories_collection = db["repositories"]
conversations_collection = db["conversations"]
messages_collection = db["messages"]