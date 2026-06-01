import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# A reliable, persistent file path to act as our local document database
DATA_FILE = os.path.join(os.path.dirname(__file__), 'listings_db.json')

def load_stored_listings():
    """Load listings safely from the persistent database file."""
    # Seed default values with highly specific, distinct coordinates so they never cross wires
    default_placeholders = [
        {
            "id": 1,
            "provider": "Rahul Sharma",
            "category": "services",
            "type": "Service",
            "title": "Class 12 Math & Calculus Tuition",
            "description": "Offering tailored preparation tracks for CBSE Grade 12 Mathematics, focusing on Calculus integration techniques and Matrix determinants.",
            "price": "AED 120/hr",
            "location_zone": "24.4322,54.6044", # Yas Island Sector
            "is_student": "false"
        },
        {
            "id": 2,
            "provider": "Aisha Al Mansoori",
            "category": "heritage",
            "type": "Product",
            "title": "Handcrafted Clay Pottery & Talli Crafts",
            "description": "Authentic, locally sourced Emirati heritage crafts and hand-woven items perfect for traditional community presentation setups.",
            "price": "AED 250",
            "location_zone": "24.4539,54.3773", # Corniche Central Sector
            "is_student": "false"
        }
    ]
    
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_placeholders, f, indent=4)
        return default_placeholders
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default_placeholders

def save_listings_to_disk(listings_data):
    """Write listing collection straight to disk so everyone can see updates live."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(listings_data, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/listings', methods=['GET'])
def get_listings():
    category_filter = request.args.get('category', 'all')
    type_filter = request.args.get('type', 'all')
    
    all_items = load_stored_listings()
    filtered_list = []
    
    for item in all_items:
        # Category tracking condition
        if category_filter != 'all' and item.get('category') != category_filter:
            continue
        # Subvariant asset type tracking condition
        if type_filter != 'all' and item.get('type') != type_filter:
            continue
        filtered_list.append(item)
        
    return jsonify(filtered_list)

@app.route('/api/listings/add', methods=['POST'])
def add_listing():
    incoming_data = request.json
    
    if not incoming_data or not incoming_data.get('provider') or not incoming_data.get('title'):
        return jsonify({"success": False, "error": "Missing essential listing parameters."}), 400
    
    current_collection = load_stored_listings()
    
    # Generate a reliable auto-incrementing ID metric
    new_id = max([item.get('id', 0) for item in current_collection]) + 1 if current_collection else 1
    
    # Append new node data systematically ensuring coordinates are tracked as an isolated pair
    new_node = {
        "id": new_id,
        "provider": incoming_data.get('provider'),
        "category": incoming_data.get('category', 'services'),
        "type": incoming_data.get('type', 'Service'),
        "title": incoming_data.get('title'),
        "description": incoming_data.get('description', ''),
        "price": incoming_data.get('price', 'Contact for Rate'),
        "location_zone": incoming_data.get('location_zone', '24.4539,54.3773'),
        "is_student": incoming_data.get('is_student', 'false')
    }
    
    current_collection.append(new_node)
    save_listings_to_disk(current_collection)
    
    return jsonify({"success": True, "id": new_id})

if __name__ == '__main__':
    app.run(debug=True, port=5000)