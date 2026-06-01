import os
from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# CONFIGURATION: Connected live to your personal Supabase project
SUPABASE_URL = "https://gpljplpjuwfbffawxxns.supabase.co"
SUPABASE_KEY = "sb_publishable_KCQg3VEcFKBbYrf3XZthTw_8SgA6N6J"

# Initialize live Supabase Client connection cluster with safety fallbacks
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Initialization Error: Could not connect to Supabase client: {e}")
    supabase = None

# Local emergency backup data to display if the database table is completely empty or building
fallback_listings = [
    {
        "id": 1,
        "provider": "Aisha M.",
        "badge": "Verified Resident",
        "category": "heritage",
        "type": "Product",
        "title": "Authentic Emirati Luqaimat Catering",
        "description": "Freshly made traditional crunchy sweet dumplings with date syrup for family gatherings and weekend events.",
        "distance": "0.5 km away",
        "tag": "Cultural Cuisine",
        "price": "AED 45"
    },
    {
        "id": 2,
        "provider": "Rahul K.",
        "badge": "Verified Student Volunteer",
        "category": "services",
        "type": "Service",
        "title": "Grade 10 Mathematics Tutoring",
        "description": "Offering tailored intensive revision sessions for school curriculum. Flexible hours over weekends.",
        "distance": "1.2 km away",
        "tag": "Education",
        "price": "Free / Volunteer"
    }
]

@app.route('/')
def home():
    listings = []
    if supabase:
        try:
            # Fetch initial live feed rows ordered from newest to oldest timestamp
            response = supabase.table("listings").select("*").order("created_at", descending=True).execute()
            listings = response.data
        except Exception as e:
            print(f"Live database read exception encountered: {e}")
            listings = fallback_listings
    else:
        listings = fallback_listings
        
    return render_template('index.html', listings=listings)

@app.route('/api/listings', methods=['GET'])
def get_listings():
    category = request.args.get('category', 'all')
    listing_type = request.args.get('type', 'all')
    
    if not supabase:
        # Filter fallback if client didn't boot
        filtered = fallback_listings
        if category != 'all': filtered = [l for l in filtered if l['category'] == category]
        if listing_type != 'all': filtered = [l for l in filtered if l['type'] == listing_type]
        return jsonify(filtered)
        
    try:
        query = supabase.table("listings").select("*").order("created_at", descending=True)
        
        # Apply strict live filters based on user selection toggles
        if category != 'all':
            query = query.eq('category', category)
        if listing_type != 'all':
            query = query.eq('type', listing_type)
            
        response = query.execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/listings/add', methods=['POST'])
def add_listing():
    data = request.json
    
    # Determine user badge status depending on checkbox input state
    badge_status = "Verified Student Volunteer" if data.get('is_student') == 'true' else "Verified Resident"
    
    new_row = {
        "provider": data.get('provider', 'Guest Neighbor'),
        "badge": badge_status,
        "category": data.get('category', 'services'),
        "type": data.get('type', 'Service'),
        "title": data.get('title', 'Untitled Offering'),
        "description": data.get('description', ''),
        "distance": "0.4 km away",
        "tag": "Community Support" if data.get('category') == 'services' else "Heritage Craft",
        "price": data.get('price', 'Free')
    }
    
    if not supabase:
        # Simulate local sandbox array append if live DB connection is missing
        fallback_listings.insert(0, new_row)
        return jsonify({"success": True, "item": new_row})
        
    try:
        response = supabase.table("listings").insert(new_row).execute()
        return jsonify({"success": True, "item": response.data[0]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)