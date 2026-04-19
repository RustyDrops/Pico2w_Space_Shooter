import functions_framework
from google.cloud import firestore
import json

# Initialize Firestore client
db = firestore.Client()

@functions_framework.http
def leaderboard_proxy(request):
    """
    HTTP Cloud Function to handle leaderboard operations.
    - POST: Submit a new score {"name": "ABC", "score": 100}
    - GET: Retrieve Top 5 scores
    """
    # Set CORS headers for the preflight request
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    if request.method == 'POST':
        try:
            request_json = request.get_json(silent=True)
            if not request_json:
                return ({"error": "JSON required"}, 400, headers)
            
            name = request_json.get('name', '???')[:3].upper() # Limit to 3 chars
            score = int(request_json.get('score', 0))
            
            # Save to Firestore
            doc_ref = db.collection('highscores').document()
            doc_ref.set({
                'name': name,
                'score': score,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            
            return ({"status": "success", "message": f"Saved score for {name}"}, 200, headers)
        except Exception as e:
            return ({"error": str(e)}, 500, headers)

    elif request.method == 'GET':
        try:
            # Query top 5 scores
            scores_ref = db.collection('highscores')
            query = scores_ref.order_by('score', direction=firestore.Query.DESCENDING).limit(5)
            results = query.stream()
            
            leaderboard = []
            for doc in results:
                data = doc.to_dict()
                leaderboard.append({
                    "name": data.get('name', '???'),
                    "score": data.get('score', 0)
                })
            
            return ({"leaderboard": leaderboard}, 200, headers)
        except Exception as e:
            return ({"error": str(e)}, 500, headers)

    return ({"error": "Method not allowed"}, 405, headers)
