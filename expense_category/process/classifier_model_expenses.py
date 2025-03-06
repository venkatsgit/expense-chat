from db import get_db
import requests
from config import HUGGINGFACEHUB_API_TOKEN, FACEBOOK_BART_LARGE_MNLI_CLASSIFIER_URL


class ExpenseClassifier:
    def __init__(self, user_id, file_id,classifier):
        self.user_id = user_id
        self.file_id = file_id
        self.processed_description = {}
        self.row_query_limit = 10
        self.unique_description_count = 0
        self.labels = [
            "food", "transportation", "shopping", "health", "entertainment",
            "rent",  "investment"
        ]
        self.classifier = classifier

    def process_table_data(self):

        descriptions = self.get_unique_descriptions()

        batch = []
        for desc in descriptions:
            if desc in self.processed_description:
                continue
            batch.append(desc)
            if len(batch) == self.row_query_limit:
                self.classify_and_store(batch)
                self.update_database(batch)
                batch = []

        if batch:
            self.classify_and_store(batch)
            self.update_database(batch)

    def get_unique_descriptions(self):
        query = """
            SELECT DISTINCT description 
            FROM expense_insights.expenses
            WHERE user_id = %s AND file_id = %s
            AND (category IS NULL OR category = '')
        """
        db, cursor = None, None
        try:
            db, cursor = get_db()
            cursor.execute(query, (self.user_id, self.file_id))
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching descriptions: {e}")
            return []


    def classify_and_store(self,batch):
        try:
            results = self.classifier(batch, self.labels)
            for desc, result in zip(batch, results):
                predicted_label = result['labels'][0]
                self.processed_description[desc] = predicted_label
                print(f"Processed: {desc} -> {predicted_label}")

        except Exception as e:
            print(f"Error during classification: {e}")
    def classify_and_store_api(self, batch):
        try:
            payload = {
                'inputs': batch,
                'parameters': {
                    'candidate_labels': self.labels
                }
            }
            headers = {
                'Authorization': 'Bearer  ' + HUGGINGFACEHUB_API_TOKEN
            }
            model_response = requests.post(
                FACEBOOK_BART_LARGE_MNLI_CLASSIFIER_URL, headers=headers, json=payload)

            if model_response.status_code == 200:
                model_response_json = model_response.json()
                for desc, model_response_json in zip(batch, model_response_json):
                    predicted_label = model_response_json['labels'][0]
                    self.processed_description[desc] = predicted_label
                    print(f"Processed: {desc} -> {predicted_label}")
            else:
                print(f"Error during classification: {emodel_response.text}")

        except Exception as e:
            print(f"Error during classification: {e}")

    def update_database(self, batch):
        if not batch:
            return

        query = """
            UPDATE expense_insights.expenses 
            SET category = %s
            WHERE user_id = %s AND file_id = %s AND description = %s
            AND (category IS NULL OR category = '')
        """

        db, cursor = None, None
        try:
            db, cursor = get_db()
            update_values = [
                (self.processed_description[desc],
                 self.user_id, self.file_id, desc)
                for desc in batch
            ]
            cursor.executemany(query, update_values)
            db.commit()
        except Exception as e:
            print(f"Error updating database: {e}")
            db.rollback()
