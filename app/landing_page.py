"""
Landing Page API & Web Server
==============================
Flask application that serves:
1. REST API endpoints for match data
2. Static frontend files (public/index.html)
"""

import os
from flask import Flask, jsonify, send_from_directory, send_file
from flask_cors import CORS
from db.database import get_all_matches, get_matches_by_status, count_matches
from datetime import datetime

# Get the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')

app = Flask(__name__, static_folder=PUBLIC_DIR)
CORS(app)  # Enable CORS for frontend requests


@app.route('/favicon.ico')
def favicon_ico():
    """Serve favicon.ico (fallback for older browsers)."""
    return send_from_directory(PUBLIC_DIR, 'favicon.svg', mimetype='image/svg+xml')


@app.route('/favicon.svg')
def favicon_svg():
    """Serve favicon.svg."""
    return send_from_directory(PUBLIC_DIR, 'favicon.svg', mimetype='image/svg+xml')


@app.route('/api/matches', methods=['GET'])
def get_matches():
    """
    Get all matches from database.
    
    Returns:
        JSON response with all matches
    """
    try:
        matches = get_all_matches()
        
        # Group matches by status
        matches_by_status = {
            'live': [],
            'scheduled': [],
            'finished': [],
            'canceled': [],
            'postponed': [],
            'unknown': []
        }
        
        for match in matches:
            status = match.get('match_status', 'unknown')
            if status in matches_by_status:
                matches_by_status[status].append(match)
            else:
                matches_by_status['unknown'].append(match)
        
        return jsonify({
            'success': True,
            'total_matches': len(matches),
            'matches': matches,
            'matches_by_status': {
                'live': len(matches_by_status['live']),
                'scheduled': len(matches_by_status['scheduled']),
                'finished': len(matches_by_status['finished']),
                'canceled': len(matches_by_status['canceled']),
                'postponed': len(matches_by_status['postponed']),
            },
            'data': matches_by_status,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/matches/live', methods=['GET'])
def get_live_matches():
    """Get only live matches."""
    try:
        matches = get_matches_by_status('live')
        return jsonify({
            'success': True,
            'count': len(matches),
            'matches': matches,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/matches/scheduled', methods=['GET'])
def get_scheduled_matches():
    """Get only scheduled matches."""
    try:
        matches = get_matches_by_status('scheduled')
        return jsonify({
            'success': True,
            'count': len(matches),
            'matches': matches,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/matches/finished', methods=['GET'])
def get_finished_matches():
    """Get only finished matches."""
    try:
        matches = get_matches_by_status('finished')
        return jsonify({
            'success': True,
            'count': len(matches),
            'matches': matches,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about matches."""
    try:
        total = count_matches()
        live = len(get_matches_by_status('live'))
        scheduled = len(get_matches_by_status('scheduled'))
        finished = len(get_matches_by_status('finished'))
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'live': live,
                'scheduled': scheduled,
                'finished': finished
            },
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'MarFutGames API',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/')
def index():
    """Serve the main landing page."""
    return send_from_directory(PUBLIC_DIR, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from public directory."""
    return send_from_directory(PUBLIC_DIR, path)


def run_server(host='0.0.0.0', port=5000, debug=False):
    """
    Run the Flask server.
    
    Args:
        host: Host to bind to (default: 0.0.0.0)
        port: Port to bind to (default: 5000)
        debug: Enable debug mode (default: False)
    """
    print(f"🚀 Starting MarFutGames server...")
    print(f"   🌐 Frontend: http://localhost:{port}/")
    print(f"   🔌 API: http://localhost:{port}/api/matches")
    print(f"   ❤️  Health: http://localhost:{port}/api/health")
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    run_server(debug=True)

