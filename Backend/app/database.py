from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
APPNAME = os.getenv("APPNAME")

uri = f"mongodb+srv://{USER}:{PASSWORD}@{HOST}/?appName={APPNAME}"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi("1"))

db = client["testgen_ai"]


def get_db_health():
    # Send a ping to confirm a successful connection
    try:
        client.admin.command("ping")
        return {"status": "connected", "database": "booking_db"}
    except Exception as e:
        return {"status": "disconnected", "error": str(e)}
