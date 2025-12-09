"""
Match Data Extraction
=====================
Extracts match data from HTML files and saves to database.
"""

from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from db.database import insert_or_update_match, init_database
from app.helper import print_info, print_success, print_error


def parse_match_time(time_str: str) -> Optional[str]:
    """
    Parse match time and convert to datetime if possible.
    
    Args:
        time_str: Time string (e.g., "15:30", "FT", "HT", "45'")
        
    Returns:
        Formatted datetime string or original time string
    """
    if not time_str or time_str.strip() == "":
        return None
    
    time_str = time_str.strip()
    
    # Check if it's a time format (HH:MM)
    time_pattern = re.compile(r'^(\d{1,2}):(\d{2})$')
    match = time_pattern.match(time_str)
    
    if match:
        hour, minute = match.groups()
        try:
            # Create datetime for today with the given time
            today = datetime.now()
            dt = today.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
            return dt.isoformat()
        except:
            return time_str
    
    return time_str


def extract_match_status(match_element) -> Dict[str, Any]:
    """
    Extract match status information from match element classes.
    
    Args:
        match_element: BeautifulSoup element for the match
        
    Returns:
        Dictionary with status information
    """
    classes = match_element.get('class', [])
    class_str = ' '.join(classes)
    
    status_info = {
        'is_live': 'event__match--live' in class_str or 'event__match--twoLine' in class_str,
        'is_scheduled': 'event__match--scheduled' in class_str,
        'is_finished': 'event__match--finished' in class_str or 'event__match--last' in class_str,
        'is_canceled': False,
        'is_postponed': False,
        'match_status': 'unknown'
    }
    
    # Determine status
    if status_info['is_live']:
        status_info['match_status'] = 'live'
    elif status_info['is_scheduled']:
        status_info['match_status'] = 'scheduled'
    elif status_info['is_finished']:
        status_info['match_status'] = 'finished'
    else:
        status_info['match_status'] = 'unknown'
    
    return status_info


def extract_match_icons(match_element) -> Dict[str, bool]:
    """
    Extract icon information from match element.
    
    Args:
        match_element: BeautifulSoup element for the match
        
    Returns:
        Dictionary with icon flags
    """
    icons = {
        'has_tv_icon': False,
        'has_audio_icon': False,
        'has_info_icon': False
    }
    
    # Check for TV icon
    tv_icon = match_element.find('a', class_='event__icon--tv')
    if tv_icon:
        icons['has_tv_icon'] = True
    
    # Check for audio icon
    audio_icon = match_element.find('a', class_='event__icon--audio')
    if audio_icon:
        icons['has_audio_icon'] = True
    
    # Check for info icon
    info_icon = match_element.find('svg', class_='event__icon--info')
    if info_icon:
        icons['has_info_icon'] = True
    
    return icons


def extract_league_info(league_element) -> Dict[str, Optional[str]]:
    """
    Extract league information from league header element.
    
    Args:
        league_element: BeautifulSoup element for the league header
        
    Returns:
        Dictionary with league information
    """
    league_info = {
        'league_name': None,
        'league_country': None,
        'league_flag_class': None
    }
    
    # Extract league name
    title_elem = league_element.find('a', class_='headerLeague__title')
    if title_elem:
        strong_elem = title_elem.find('strong')
        if strong_elem:
            league_info['league_name'] = strong_elem.get_text(strip=True)
    
    # Extract country/category
    category_elem = league_element.find('span', class_='headerLeague__category-text')
    if category_elem:
        league_info['league_country'] = category_elem.get_text(strip=True)
    
    # Extract flag class
    flag_elem = league_element.find('span', class_=re.compile(r'headerLeague__flag|icon--flag'))
    if flag_elem:
        classes = flag_elem.get('class', [])
        flag_class = [c for c in classes if 'fl_' in c or 'flag' in c]
        if flag_class:
            league_info['league_flag_class'] = ' '.join(flag_class)
    
    return league_info


def extract_match_data(match_element, league_info: Dict[str, Optional[str]]) -> Optional[Dict[str, Any]]:
    """
    Extract all data from a single match element.
    
    Args:
        match_element: BeautifulSoup element for the match
        league_info: Dictionary with league information
        
    Returns:
        Dictionary with match data or None if extraction fails
    """
    try:
        # Extract match ID
        match_id_attr = match_element.get('id', '')
        match_id = match_id_attr.replace('g_1_', '') if match_id_attr.startswith('g_1_') else match_id_attr
        
        if not match_id:
            return None
        
        # Extract match URL
        match_url = None
        link_elem = match_element.find('a', class_='eventRowLink')
        if link_elem:
            match_url = link_elem.get('href', '')
            if match_url and not match_url.startswith('http'):
                match_url = 'https://www.flashscore.pt' + match_url
        
        # Extract match time
        time_elem = match_element.find('div', class_='event__time')
        match_time = time_elem.get_text(strip=True) if time_elem else None
        
        # Extract stage/status text
        stage_elem = match_element.find('div', class_='event__stage')
        match_stage = None
        if stage_elem:
            stage_block = stage_elem.find('div', class_='event__stage--block')
            if stage_block:
                match_stage = stage_block.get_text(strip=True)
            else:
                match_stage = stage_elem.get_text(strip=True)
        
        # Extract home team
        home_participant = match_element.find('div', class_='event__homeParticipant')
        home_team_name = None
        home_team_logo = None
        if home_participant:
            name_elem = home_participant.find('span', class_=re.compile(r'wcl-name|simpleText'))
            if name_elem:
                home_team_name = name_elem.get_text(strip=True)
            logo_elem = home_participant.find('img', {'data-testid': 'wcl-participantLogo'})
            if logo_elem:
                home_team_logo = logo_elem.get('src', '')
        
        # Extract away team
        away_participant = match_element.find('div', class_='event__awayParticipant')
        away_team_name = None
        away_team_logo = None
        if away_participant:
            name_elem = away_participant.find('span', class_=re.compile(r'wcl-name|simpleText'))
            if name_elem:
                away_team_name = name_elem.get_text(strip=True)
            logo_elem = away_participant.find('img', {'data-testid': 'wcl-participantLogo'})
            if logo_elem:
                away_team_logo = logo_elem.get('src', '')
        
        # Extract scores
        home_score = None
        away_score = None
        score_home = match_element.find('span', class_='event__score--home')
        score_away = match_element.find('span', class_='event__score--away')
        
        if score_home:
            score_text = score_home.get_text(strip=True)
            if score_text and score_text != '-':
                try:
                    home_score = int(score_text)
                except ValueError:
                    pass
        
        if score_away:
            score_text = score_away.get_text(strip=True)
            if score_text and score_text != '-':
                try:
                    away_score = int(score_text)
                except ValueError:
                    pass
        
        # Extract status information
        status_info = extract_match_status(match_element)
        
        # Extract icons
        icons = extract_match_icons(match_element)
        
        # Parse half-time and current minute from stage
        half_time = None
        current_minute = None
        if match_stage:
            # Look for HT (half-time) or minute indicators
            if 'HT' in match_stage.upper() or 'Intervalo' in match_stage:
                half_time = 'HT'
            elif re.search(r"(\d+)'", match_stage):
                minute_match = re.search(r"(\d+)'", match_stage)
                if minute_match:
                    current_minute = int(minute_match.group(1))
        
        # Check for canceled/postponed
        if match_stage:
            if 'Cancelado' in match_stage or 'Canceled' in match_stage:
                status_info['is_canceled'] = True
                status_info['match_status'] = 'canceled'
            elif 'Adiado' in match_stage or 'Postponed' in match_stage:
                status_info['is_postponed'] = True
                status_info['match_status'] = 'postponed'
        
        # Build match data dictionary
        match_data = {
            'match_id': match_id,
            'match_url': match_url,
            'league_name': league_info.get('league_name'),
            'league_country': league_info.get('league_country'),
            'league_flag_class': league_info.get('league_flag_class'),
            'match_time': match_time,
            'scheduled_datetime': parse_match_time(match_time),
            'home_team_name': home_team_name,
            'home_team_logo_url': home_team_logo,
            'away_team_name': away_team_name,
            'away_team_logo_url': away_team_logo,
            'home_score': home_score,
            'away_score': away_score,
            'match_status': status_info['match_status'],
            'match_stage': match_stage,
            'is_live': status_info['is_live'],
            'is_scheduled': status_info['is_scheduled'],
            'is_finished': status_info['is_finished'],
            'is_canceled': status_info['is_canceled'],
            'is_postponed': status_info['is_postponed'],
            'has_tv_icon': icons['has_tv_icon'],
            'has_audio_icon': icons['has_audio_icon'],
            'has_info_icon': icons['has_info_icon'],
            'half_time': half_time,
            'current_minute': current_minute
        }
        
        return match_data
        
    except Exception as e:
        print_error(f"Error extracting match data: {e}")
        return None


def extract_all_matches_from_html(html_file_path: str) -> List[Dict[str, Any]]:
    """
    Extract all matches from an HTML file.
    
    Args:
        html_file_path: Path to the HTML file
        
    Returns:
        List of dictionaries containing match data
    """
    print_info(f"Reading HTML file: {html_file_path}")
    
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print_error(f"Error reading HTML file: {e}")
        return []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all soccer sport sections
    soccer_sections = soup.find_all('div', class_='sportName soccer')
    
    all_matches = []
    
    # Process each soccer section
    for soccer_section in soccer_sections:
        # Find all matches in this section
        match_elements = soccer_section.find_all('div', class_='event__match', attrs={'data-event-row': 'true'})
        
        # Find the most recent league header before each match
        for match_elem in match_elements:
            # Find the nearest league header by searching backwards through siblings
            league_info = {
                'league_name': None,
                'league_country': None,
                'league_flag_class': None
            }
            
            # Search backwards through previous siblings
            prev_sibling = match_elem.find_previous_sibling()
            while prev_sibling:
                # Check if this sibling is a league header
                league_header = prev_sibling.find('div', class_='headerLeague')
                if league_header:
                    league_info = extract_league_info(league_header)
                    break
                
                # Also check within the sibling
                if prev_sibling.name == 'div' and 'headerLeague__wrapper' in prev_sibling.get('class', []):
                    league_header = prev_sibling.find('div', class_='headerLeague')
                    if league_header:
                        league_info = extract_league_info(league_header)
                        break
                
                prev_sibling = prev_sibling.find_previous_sibling()
            
            # If no league found in siblings, search up the tree
            if not league_info['league_name']:
                parent = match_elem.parent
                for _ in range(5):  # Limit search depth
                    if parent:
                        league_header = parent.find('div', class_='headerLeague')
                        if league_header:
                            league_info = extract_league_info(league_header)
                            break
                        parent = parent.parent
                    else:
                        break
            
            # Extract match data
            match_data = extract_match_data(match_elem, league_info)
            if match_data:
                all_matches.append(match_data)
    
    # Fallback: if no matches found with the above method, try direct search
    if not all_matches:
        all_match_elements = soup.find_all('div', class_='event__match', attrs={'data-event-row': 'true'})
        
        for match_elem in all_match_elements:
            # Try to find the nearest league header
            parent = match_elem.parent
            league_info = {
                'league_name': None,
                'league_country': None,
                'league_flag_class': None
            }
            
            # Search up the tree for league header
            for _ in range(10):  # Limit search depth
                if parent:
                    league_header = parent.find('div', class_='headerLeague')
                    if league_header:
                        league_info = extract_league_info(league_header)
                        break
                    parent = parent.parent
                else:
                    break
            
            match_data = extract_match_data(match_elem, league_info)
            if match_data:
                all_matches.append(match_data)
    
    print_success(f"Extracted {len(all_matches)} matches from HTML")
    return all_matches


def save_matches_to_database(matches: List[Dict[str, Any]]) -> int:
    """
    Save extracted matches to the database.
    
    Args:
        matches: List of match data dictionaries
        
    Returns:
        Number of successfully saved matches
    """
    print_info(f"Saving {len(matches)} matches to database...")
    
    saved_count = 0
    failed_matches = []
    
    for match_data in matches:
        if insert_or_update_match(match_data):
            saved_count += 1
        else:
            failed_matches.append(match_data.get('match_id', 'unknown'))
    
    if failed_matches:
        print_error(f"Failed to save {len(failed_matches)} matches: {', '.join(failed_matches[:5])}")
        if len(failed_matches) > 5:
            print_error(f"  ... and {len(failed_matches) - 5} more")
    
    print_success(f"Saved {saved_count} out of {len(matches)} matches to database")
    return saved_count


if __name__ == "__main__":
    # Initialize database
    init_database()
    
    # Extract matches from the HTML file
    html_file = "outputs/step-1/after_accept_cookies.html"
    matches = extract_all_matches_from_html(html_file)
    
    # Save to database
    if matches:
        save_matches_to_database(matches)
    else:
        print_error("No matches found to save")

