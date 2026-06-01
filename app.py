import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Persistent file-based document tracking ledger
DATA_FILE = os.path.join(os.path.dirname(__file__), 'listings_db.json')

def get_default_listings():
    """Returns the core default listings to ensure data structure stability."""
    return [
        {
            "id": 1,
            "provider": "Rahul Sharma",
            "category": "services",
            "type": "Service",
            "title": "Class 12 Math & Calculus Tuition",
            "description": "Offering tailored preparation tracks for CBSE Grade 12 Mathematics, focusing on Calculus integration techniques and Matrix determinants.",
            "price": "AED 120/hr",
            "location_zone": "24.4322,54.6044", # Yas Island
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
            "location_zone": "24.4680,54.3644", # Corniche Area
            "is_student": "false"
        }
    ]

def load_stored_listings():
    """Load listings safely, self-healing the database if empty or missing."""
    defaults = get_default_listings()
    
    # If file doesn't exist, build it with default values
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(defaults, f, indent=4)
        return defaults
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:  # File is empty string
                raise ValueError("Empty file")
            data = json.loads(content)
            
            # FORCE SELF-HEAL: If the file exists but has 0 listings, force reload defaults
            if not data or len(data) == 0:
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(defaults, f, indent=4)
                return defaults
            return data
    except Exception:
        # Fallback and fix if file is corrupted or unreadable
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(defaults, f, indent=4)
        return defaults

def save_listings_to_disk(listings_data):
    """Write listing collection straight to disk so data is never lost."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(listings_data, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/listings', methods=['GET'])
def get_listings():
    category_filter = request.args.get('category', 'all').lower().strip()
    type_filter = request.args.get('type', 'all').lower().strip()
    
    all_items = load_stored_listings()
    filtered_list = []
    
    for item in all_items:
        # Match categories safely (case-insensitive fallback)
        item_cat = str(item.get('category', 'services')).lower().strip()
        item_type = str(item.get('type', 'Service')).lower().strip()
        
        if category_filter != 'all' and item_cat != category_filter:
            continue
        if type_filter != 'all' and item_type != type_filter:
            continue
            
        filtered_list.append(item)
        
    return jsonify(filtered_list)

@app.route('/api/listings/add', methods=['POST'])
def add_listing():
    incoming_data = request.json
    if not incoming_data or not incoming_data.get('provider') or not incoming_data.get('title'):
        return jsonify({"success": False, "error": "Missing essential parameters."}), 400
    
    current_collection = load_stored_listings()
    new_id = max([item.get('id', 0) for item in current_collection]) + 1 if current_collection else 1
    
    new_node = {
        "id": new_id,
        "provider": incoming_data.get('provider'),
        "category": incoming_data.get('category', 'services'),
        "type": incoming_data.get('type', 'Service'),
        "title": incoming_data.get('title'),
        "description": incoming_data.get('description', ''),
        "price": incoming_data.get('price', 'Contact for Rate'),
        "location_zone": incoming_data.get('location_zone', '24.4539,54.3773'),
        "is_student": str(incoming_data.get('is_student', 'false')).lower()
    }
    
    current_collection.append(new_node)
    save_listings_to_disk(current_collection)
    return jsonify({"success": True, "id": new_id})

if __name__ == '__main__':
    # Using clean restart handling
    app.run(debug=True, port=5000)