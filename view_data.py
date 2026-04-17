from pymongo import MongoClient
import sys

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "stock_market"
COLLECTION_NAME = "price_history"

def view_latest_data():
    try:
        client = MongoClient(MONGO_URI)
        client.admin.command('ping')
        collection = client[DB_NAME][COLLECTION_NAME]
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        sys.exit(1)
        
    # Get total count
    count = collection.count_documents({})
    print(f"Total records in database: {count}")
    
    print("\nLatest 10 records across all indexes:")
    # Sort by timestamp descending
    cursor = collection.find().sort("timestamp", -1).limit(10)
    
    try:
        import pandas as pd
        records = list(cursor)
        df = pd.DataFrame(records)
        if not df.empty:
             # _id is MongoDB's object id, we usually don't need to display it
             if '_id' in df.columns:
                 df = df.drop(columns=['_id'])
             print(df.to_string(index=False))
        else:
             print("No records found.")
    except ImportError:
        # Fallback if pandas is not installed
        for doc in cursor:
            print(f"[{doc['timestamp']}] {doc['index_name']}: {doc['price']}")

if __name__ == "__main__":
    view_latest_data()
