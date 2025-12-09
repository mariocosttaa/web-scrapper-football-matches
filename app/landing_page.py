"""
Landing Page API
================
API endpoint that returns match data from database in JSON format.
Single responsibility: Only returns data, no HTML generation.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from db.database import get_all_matches, get_matches_by_status, count_matches
from datetime import datetime


app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

