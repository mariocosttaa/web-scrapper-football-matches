"""
Test Module - Run with: python -m test
===================================
Test the extraction functionality using the existing HTML file.
This test uses app code directly to avoid code duplication.
It extracts matches and exports to JSON without saving to database.
"""

import json
import os
from datetime import datetime
from app.extract_matches import extract_all_matches_from_html
from app.helper import print_info, print_success, print_error


def export_matches_to_json_direct(matches, output_file: str) -> str:
    """
    Export matches directly to JSON file (without database).
    Uses the same format as app.export_json but works with match dicts directly.
    
    Args:
        matches: List of match dictionaries
        output_file: Path to output JSON file
        
    Returns:
        Path to the created JSON file
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
    
    # Convert matches to JSON-serializable format
    json_data = {
        "export_date": datetime.now().isoformat(),
        "total_matches": len(matches),
        "status_filter": "all",
        "matches": matches
    }
    
    # Write to JSON file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
        
        print_success(f"Exported {len(matches)} matches to: {output_file}")
        return output_file
        
    except Exception as e:
        print_error(f"Error exporting to JSON: {e}")
        raise


def export_matches_summary_direct(matches, output_file: str) -> str:
    """
    Export a summary of matches grouped by status (without database).
    
    Args:
        matches: List of match dictionaries
        output_file: Path to output JSON file
        
    Returns:
        Path to the created JSON file
    """
    # Group by status
    by_status = {}
    for match in matches:
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
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else ".", exist_ok=True)
    
    json_data = {
        "export_date": datetime.now().isoformat(),
        "total_matches": len(matches),
        "summary": {
            status: {
                "count": len(match_list),
                "matches": match_list
            }
            for status, match_list in by_status.items()
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


def test_extraction():
    """
    Test extraction from existing HTML file.
    Uses app code directly - extracts matches and exports to JSON without database.
    """
    print("\n" + "="*60)
    print("TEST: Match Extraction from HTML")
    print("="*60)
    print_info("Using app code directly (no database)")
    
    # Try multiple possible HTML file locations
    html_files = [
        "test/output-code.html",  # User's test file (put your HTML code here)
        "outputs/step-1/after_accept_cookies.html",  # Fallback from actual scraper run
    ]
    
    html_file = None
    for file_path in html_files:
        try:
            with open(file_path, 'r'):
                html_file = file_path
                break
        except FileNotFoundError:
            continue
    
    if not html_file:
        print_error(f"HTML file not found. Tried: {', '.join(html_files)}")
        print_info("Please run the scraper first to generate the HTML file")
        return False
    
    print_info(f"Using HTML file: {html_file}")
    
    try:
        # Extract matches using app code
        print_info("Extracting matches from HTML...")
        matches = extract_all_matches_from_html(html_file)
        
        if not matches:
            print_error("No matches found in HTML file")
            return False
        
        print_success(f"Extracted {len(matches)} matches")
        
        # Export to JSON to test/output/ folder (no database)
        print_info("Exporting to JSON (test/output/)...")
        os.makedirs("test/output", exist_ok=True)
        
        json_file = export_matches_to_json_direct(matches, "test/output/matches.json")
        
        # Also export summary
        summary_file = export_matches_summary_direct(matches, "test/output/matches_summary.json")
        
        # Print sample match
        if matches:
            print("\n" + "="*60)
            print("SAMPLE MATCH:")
            print("="*60)
            sample = matches[0]
            print(f"  Match ID: {sample.get('match_id')}")
            print(f"  League: {sample.get('league_country')} - {sample.get('league_name')}")
            print(f"  Teams: {sample.get('home_team_name')} vs {sample.get('away_team_name')}")
            print(f"  Time: {sample.get('match_time')}")
            print(f"  Status: {sample.get('match_status')}")
            print(f"  Score: {sample.get('home_score')} - {sample.get('away_score')}")
            print(f"  URL: {sample.get('match_url')}")
        
        print("\n" + "="*60)
        print_success("Test completed successfully!")
        print_info(f"JSON files saved to: test/output/")
        print("="*60)
        return True
        
    except Exception as e:
        print_error(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_extraction()

