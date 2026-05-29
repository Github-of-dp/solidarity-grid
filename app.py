import os
from flask import Flask, render_template, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

# CONFIGURATION: Connected live to your personal Supabase project
SUPABASE_URL = "https://gpljplpjuwfbffawxxns.supabase.co"
SUPABASE_KEY = "sb_publishable_KCQg3VEcFKBbYrf3XZthTw_8SgA6N6J"

# Initialize live Supabase Client connection cluster
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/')
def home():
    try:
        # Fetch initial live feed rows ordered from newest to oldest timestamp
        response = supabase.table("listings").select("*").order("created_at", descending=True).execute()
        initial_listings = response.data
    except Exception as e:
        print(f"Error fetching rows from Supabase: {e}")
        initial_listings = []
        
    return render_template('index.html', listings=initial_listings)

@app.route('/api/listings', methods=['GET'])
def get_listings():
    category = request.args.get('category', 'all')
    listing_type = request.args.get('type', 'all')
    
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
    
    try:
        response = supabase.table("listings").insert(new_row).execute()
        return jsonify({"success": True, "item": response.data[0]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Bind server to 0.0.0.0 and dynamic environment PORT for cloud host integration
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)