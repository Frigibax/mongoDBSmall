from flask import Flask, render_template, jsonify
from pymongo import MongoClient

app = Flask(__name__)
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "stock_market"
COLLECTION_NAME = "price_history"

def get_db_collection():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME][COLLECTION_NAME]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/history')
def api_history():
    collection = get_db_collection()
    # Major indexes we track
    indexes = ["S&P 500", "Dow Jones", "NASDAQ", "FTSE 100", "Nikkei 225", "BSE SENSEX", "NIFTY 50"]
    data = {}
    
    for idx in indexes:
        # Get latest 30 points, sort descending by time to grab the most recent
        cursor = collection.find({"index_name": idx}).sort("timestamp", -1).limit(30)
        points = list(cursor)
        
        # Reverse to get chronological order (oldest -> newest) for the chart
        points.reverse()
        data[idx] = [
            {"time": point["timestamp"].strftime("%H:%M:%S"), "price": point["price"]}
            for point in points
        ]
        
    return jsonify(data)

if __name__ == '__main__':
    # Run the server accessible on localhost
    app.run(debug=True, port=5000)
