# app.py - Flask Backend

from flask import Flask, request, jsonify
from flask_cors import CORS
import run  # Import the run.py module

# =========== Initialize Flask ===========
app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# =========== API Routes ===========
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    db_status = run.get_database_status()
    return jsonify({
        "status": "healthy",
        "database": db_status
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                "error": "Message cannot be empty"
            }), 400
        
        # Check if database is initialized
        db_status = run.get_database_status()
        if db_status['status'] != 'ready':
            return jsonify({
                "error": "Database not initialized. Please run preprocess.py first.",
                "response": "⚠️ The placement database is not ready yet. Please contact the administrator."
            }), 500
        
        # Generate response using run.py functions
        answer = run.answer_with_gemini(user_message)
        
        return jsonify({
            "response": answer,
            "status": "success"
        })
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            "error": str(e),
            "response": "❌ Sorry, I encountered an error processing your request. Please try again.",
            "status": "error"
        }), 500

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    """Get sample questions for users"""
    suggestions = [
        "Tell me about the interview process of fidelity investments",
        "What companies visited for placements in Mechanical department?",
        "how many rounds of interview for citi bank?",
        "explain the interview process for comcast?",
        "What package does citi bank offers?",
    ]
    return jsonify({
        "suggestions": suggestions,
        "status": "success"
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    db_status = run.get_database_status()
    return jsonify({
        "total_chunks": db_status.get('total_chunks', 0),
        "collection_name": db_status.get('collection_name', 'N/A'),
        "status": db_status.get('status', 'unknown')
    })

# =========== Run Server ===========
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 OneIT Placement Chatbot - Flask Backend")
    print("="*60)
    print("✅ Backend running on http://localhost:5000")
    print("📊 Database status:", run.get_database_status())
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)