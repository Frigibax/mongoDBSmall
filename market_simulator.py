import time
import random
from datetime import datetime
from pymongo import MongoClient
import sys

# Connection URI to local MongoDB
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "stock_market"
COLLECTION_NAME = "price_history"

# Initial starting points for our indexes
# Including major global indexes and Indian indexes (BSE SENSEX, NIFTY 50)
INDEXES = {
    "S&P 500": 5000.0,
    "Dow Jones": 38000.0,
    "NASDAQ": 16000.0,
    "FTSE 100": 8000.0,
    "Nikkei 225": 40000.0,
    "BSE SENSEX": 73000.0,  # Indian Index
    "NIFTY 50": 22000.0     # Indian Index
}

def get_db_collection():
    try:
        client = MongoClient(MONGO_URI)
        # Check connection
        client.admin.command('ping')
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        return collection
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        print("Please ensure MongoDB is installed and running on localhost:27017.")
        sys.exit(1)

def populate_initial_data(collection):
    print("Clearing existing data and populating initial seed data...")
    # Optional: Clear old records for a fresh start so we can easily track the current run
    collection.delete_many({}) 
    
    initial_records = []
    now = datetime.utcnow()
    for index_name, price in INDEXES.items():
        doc = {
            "index_name": index_name,
            "price": price,
            "timestamp": now
        }
        initial_records.append(doc)
    
    if initial_records:
        collection.insert_many(initial_records)
        print("Initial data populated successfully.\n")

def simulate_price_updates(collection):
    print("Starting live price simulation. Press Ctrl+C to stop.")
    try:
        # Keep track of current prices to apply small percentage changes
        current_prices = INDEXES.copy()
        
        while True:
            updates = []
            now = datetime.utcnow()
            
            for index_name, current_price in current_prices.items():
                # Generate a random percentage change between -0.5% and +0.5%
                change_percent = random.uniform(-0.005, 0.005)
                new_price = current_price * (1 + change_percent)
                # Round to 2 decimal places for typical stock prices
                new_price = round(new_price, 2)
                
                # Update current price tracking
                current_prices[index_name] = new_price
                
                doc = {
                    "index_name": index_name,
                    "price": new_price,
                    "timestamp": now
                }
                updates.append(doc)
            
            if updates:
                collection.insert_many(updates)
                print(f"[{now.strftime('%H:%M:%S')}] Inserted {len(updates)} updates.")
                for doc in updates:
                    print(f"   - {doc['index_name']:<12}: {doc['price']}")
                print("-" * 35)
                
            # Wait 3 seconds before generating the next set of updates
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")

if __name__ == "__main__":
    collection = get_db_collection()
    populate_initial_data(collection)
    simulate_price_updates(collection)
