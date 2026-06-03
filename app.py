import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), 'listings_db.json')

def get_default_listings():
    """Returns the updated rich multi-feature schema defaults for Sanad ecosystem mapping."""
    return [
        {
            "id": 1,
            "provider": "Zayed Heritage Group",
            "category": "projects",
            "type": "Product",
            "title": "Al Bateen Community Garden Initiative",
            "description": "Collaborative urban planting project constructing traditional green spaces. Seeking material drop-offs and architectural shade setup layouts.",
            "price": "Target: 500kg Soil",
            "location_zone": "24.4562,54.3484",
            "is_student": "false"
        },
        {
            "id": 2,
            "provider": "Emirati Youth Red Crescent",
            "category": "volunteer",
            "type": "Service",
            "title": "Senior Companion Care & Story Archiving",
            "description": "Volunteers needed to visit elders, coordinate weekly social majlis discussions, and document oral local histories.",
            "price": "4 Slots Open",
            "location_zone": "24.4820,54.3580",
            "is_student": "true"
        },
        {
            "id": 3,
            "provider": "Fatima Al Suwaidi",
            "category": "skills",
            "type": "Service",
            "title": "Traditional Sadu Weaving Masterclass",
            "description": "Learn the precise geometries and historical storytelling styles behind authentic UNESCO-listed heritage embroidery art methods.",
            "price": "AED 50/session",
            "location_zone": "24.4680,54.3644",
            "is_student": "false"
        },
        {
            "id": 4,
            "provider": "Khalid Al Mansoori",
            "category": "news",
            "type": "Service",
            "title": "New Cultural District Transit Lane Opening",
            "description": "Community alert for neighborhood residents: Dedicated pedestrian corridors and clean transport tracks are going live around the local plaza area.",
            "price": "Community Alert",
            "location_zone": "24.4322,54.6044",
            "is_student": "false"
        }
    ]

def load_stored_listings():
    defaults = get_default_listings()
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(defaults, f, indent=4)
        return defaults
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                raise ValueError("Empty file payload matrix.")
            data = json.loads(content)
            if not data or len(data) == 0:
                with open(DATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump(defaults, f, indent=4)
                return defaults
            return data
    except Exception:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(defaults, f, indent=4)
        return defaults

def save_listings_to_disk(listings_data):
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
        item_cat = str(item.get('category', 'projects')).lower().strip()
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
        return jsonify({"success": False, "error": "Missing parameters."}), 400
    
    current_collection = load_stored_listings()
    new_id = max([item.get('id', 0) for item in current_collection]) + 1 if current_collection else 1
    
    new_node = {
        "id": new_id,
        "provider": incoming_data.get('provider'),
        "category": incoming_data.get('category', 'projects'),
        "type": incoming_data.get('type', 'Service'),
        "title": incoming_data.get('title'),
        "description": incoming_data.get('description', ''),
        "price": incoming_data.get('price', 'Community Asset'),
        "location_zone": incoming_data.get('location_zone', '24.4539,54.3773'),
        "is_student": str(incoming_data.get('is_student', 'false')).lower()
    }
    
    current_collection.append(new_node)
    save_listings_to_disk(current_collection)
    return jsonify({"success": True, "id": new_id})

if __name__ == '__main__':
    app.run(debug=True)