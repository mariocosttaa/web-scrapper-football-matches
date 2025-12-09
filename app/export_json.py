"""
JSON Export Utility
===================
Exports match data from database to JSON format.
"""

import json
import os
from datetime import datetime
from db.database import get_all_matches, get_matches_by_status, count_matches
from app.helper import print_info, print_success, print_error


def export_matches_to_json(output_file: str = None, status: str = None) -> str:
    """
    Export matches from database to JSON file.
    
    Args:
        output_file: Path to output JSON file (default: matches_YYYY-MM-DD_HH-MM-SS.json)
        status: Optional status filter ('live', 'scheduled', 'finished', etc.)
        
    Returns:
        Path to the created JSON file
    """
    # Get matches from database
    if status:
        matches = get_matches_by_status(status)
        print_info(f"Exporting {len(matches)} matches with status '{status}'")
    else:
        matches = get_all_matches()
        print_info(f"Exporting {len(matches)} matches")
    
    # Generate output filename if not provided
    if not output_file:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        status_suffix = f"_{status}" if status else ""
        output_file = f"outputs/matches{status_suffix}_{timestamp}.json"
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
    
    # Convert matches to JSON-serializable format
    json_data = {
        "export_date": datetime.now().isoformat(),
        "total_matches": len(matches),
        "status_filter": status if status else "all",
        "matches": []
    }
    
    for match in matches:
        # Convert sqlite3.Row to dict and handle None values
        match_dict = {}
        for key in match.keys():
            value = match[key]
            # Convert boolean integers to actual booleans
            if isinstance(value, int) and key.startswith(('is_', 'has_')):
                match_dict[key] = bool(value)
            else:
                match_dict[key] = value
        json_data["matches"].append(match_dict)
    
    # Write to JSON file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
        
        print_success(f"Exported {len(matches)} matches to: {output_file}")
        return output_file
        
    except Exception as e:
        print_error(f"Error exporting to JSON: {e}")
        raise


def export_matches_summary_to_json(output_file: str = None) -> str:
    """
    Export a summary of matches grouped by status.
    
    Args:
        output_file: Path to output JSON file
        
    Returns:
        Path to the created JSON file
    """
    all_matches = get_all_matches()
    total_count = count_matches()
    
    # Group by status
    by_status = {}
    for match in all_matches:
        status = match.get('match_status', 'unknown')
        if status not in by_status:
            by_status[status] = []
        by_status[status].append({
            'match_id': match.get('match_id'),
            'home_team': match.get('home_team_name'),
            'away_team': match.get('away_team_name'),
            'score': f"{match.get('home_score', '-')} - {match.get('away_score', '-')}",
            'match_time': match.get('match_time'),
            'league': match.get('league_name')
        })
    
    # Generate output filename if not provided
    if not output_file:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = f"outputs/matches_summary_{timestamp}.json"
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
    
    json_data = {
        "export_date": datetime.now().isoformat(),
        "total_matches": total_count,
        "summary": {
            status: {
                "count": len(matches),
                "matches": matches
            }
            for status, matches in by_status.items()
        }
    }
    
    # Write to JSON file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
        
        print_success(f"Exported summary to: {output_file}")
        return output_file
        
    except Exception as e:
        print_error(f"Error exporting summary: {e}")
        raise

