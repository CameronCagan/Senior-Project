import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
from typing import Any, List, Dict

class FirebaseManager:
    def __init__(self, service_account_path: str):
        if not firebase_admin._apps: #check if app already initialized
        # Initialize Firebase app
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def get_collection(self, collection_name: str) -> List[Dict[str, Any]]:
        """Fetch all documents from a collection."""
        docs = self.db.collection(collection_name).stream()
        return [doc.to_dict() for doc in docs]
