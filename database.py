import firebase_admin
from firebase_admin import credentials, firestore
import os

if not firebase_admin._apps:
    cred_path = "serviceAccountKey.json"
    if os.path.exists(cred_path):
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            print(f"Firebase initialization error: {e}")

db = firestore.client() if firebase_admin._apps else None

class ATMDatabase:
    def __init__(self, user_doc_id=None):
        self.db = db
        self.user_doc_id = user_doc_id

    def create_account(self, name, pin, initial_balance, use_face_id):
        if not self.db:
            return False, "Database not connected (Missing serviceAccountKey.json).", None
        
        try:
            users_ref = self.db.collection("atm_accounts")
            
            existing_docs = list(users_ref.stream())
            next_label = len(existing_docs)

            new_doc_ref = users_ref.document()
            new_doc_ref.set({
                "name": name,
                "pin": pin,
                "balance": float(initial_balance),
                "face_id_enabled": use_face_id,
                "face_label": next_label,
                "history": [f"Account created with Rs. {float(initial_balance):,.2f}"]
            })
            return True, new_doc_ref.id, next_label
        except Exception as e:
            return False, str(e), None

    def find_user_by_pin(self, entered_pin):
        if not self.db:
            return None, None

        docs = self.db.collection("atm_accounts").where("pin", "==", entered_pin).stream()
        for doc in docs:
            return doc.id, doc.to_dict()
        return None, None

    def get_data(self):
        if not self.db or not self.user_doc_id:
            return {"name": "User", "balance": 0.0, "face_id_enabled": False, "history": []}
        doc = self.db.collection("atm_accounts").document(self.user_doc_id).get()
        return doc.to_dict() if doc.exists else {}

    def update_balance(self, new_balance, history_msg):
        if self.db and self.user_doc_id:
            ref = self.db.collection("atm_accounts").document(self.user_doc_id)
            data = self.get_data()
            history = data.get("history", [])
            history.append(history_msg)
            ref.update({
                "balance": new_balance,
                "history": history
            })

    def change_pin(self, new_pin):
        if self.db and self.user_doc_id:
            ref = self.db.collection("atm_accounts").document(self.user_doc_id)
            ref.update({"pin": new_pin})
