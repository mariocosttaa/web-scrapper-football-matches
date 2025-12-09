"""
Landing Page Generator
======================
Generates a beautiful HTML landing page displaying match data from the database.
Uses Tailwind CSS for styling and JavaScript for interactivity.
"""

import os
from datetime import datetime
from db.database import get_all_matches, count_matches


def print_info(msg):
    """Print info message."""
    print(f"ℹ️  {msg}")


def print_success(msg):
    """Print success message."""
    print(f"✅ {msg}")


def print_error(msg):
    """Print error message."""
    print(f"❌ {msg}")


def generate_landing_page(output_file: str = "public/index.html") -> str:
    """
    Generate a beautiful landing page HTML file with match data from database.
    
    Args:
        output_file: Path to output HTML file (default: landing-page.html)
        
    Returns:
        Path to the generated HTML file
    """
    print_info(f"Generating landing page: {output_file}")
    
    # Get all matches from database
    try:
        matches = get_all_matches()
        total_matches = len(matches)
        print_info(f"Found {total_matches} matches in database")
    except Exception as e:
        print_error(f"Error fetching matches from database: {e}")
        matches = []
        total_matches = 0
    
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
    
    # Generate HTML
    html_content = generate_html_content(matches, matches_by_status, total_matches)
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print_info(f"Created directory: {output_dir}")
    
    # Write to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print_success(f"Landing page generated: {output_file}")
        return output_file
    except Exception as e:
        print_error(f"Error writing landing page: {e}")
        raise


def generate_html_content(matches, matches_by_status, total_matches):
    """Generate the HTML content for the landing page."""
    
    live_count = len(matches_by_status['live'])
    scheduled_count = len(matches_by_status['scheduled'])
    finished_count = len(matches_by_status['finished'])
    
    # Generate match cards HTML
    live_cards = generate_match_cards(matches_by_status['live'], 'live')
    scheduled_cards = generate_match_cards(matches_by_status['scheduled'], 'scheduled')
    finished_cards = generate_match_cards(matches_by_status['finished'], 'finished')
    
    html = f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MarFutGames - Live Football Matches</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        * {{
            font-family: 'Inter', sans-serif;
        }}
        
        .match-card {{
            transition: all 0.3s ease;
        }}
        
        .match-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }}
        
        .live-pulse {{
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{
                opacity: 1;
            }}
            50% {{
                opacity: .5;
            }}
        }}
        
        .gradient-bg {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        .status-badge {{
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .score-display {{
            font-size: 2rem;
            font-weight: 700;
            line-height: 1;
        }}
    </style>
</head>
<body class="bg-gray-50">
    <!-- Header -->
    <header class="gradient-bg text-white shadow-lg">
        <div class="container mx-auto px-4 py-6">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    <i class="fas fa-futbol text-4xl"></i>
                    <div>
                        <h1 class="text-3xl font-bold">MarFutGames</h1>
                        <p class="text-purple-200 text-sm">Live Football Matches & Scores</p>
                    </div>
                </div>
                <div class="text-right">
                    <div class="text-2xl font-bold">{total_matches}</div>
                    <div class="text-purple-200 text-sm">Total Matches</div>
                </div>
            </div>
        </div>
    </header>

    <!-- Stats Bar -->
    <div class="bg-white shadow-md">
        <div class="container mx-auto px-4 py-4">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="flex items-center space-x-3 p-4 bg-red-50 rounded-lg border-l-4 border-red-500">
                    <div class="bg-red-500 rounded-full p-3">
                        <i class="fas fa-circle text-white text-sm"></i>
                    </div>
                    <div>
                        <div class="text-2xl font-bold text-red-600">{live_count}</div>
                        <div class="text-sm text-gray-600">Live Matches</div>
                    </div>
                </div>
                <div class="flex items-center space-x-3 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                    <div class="bg-blue-500 rounded-full p-3">
                        <i class="fas fa-clock text-white text-sm"></i>
                    </div>
                    <div>
                        <div class="text-2xl font-bold text-blue-600">{scheduled_count}</div>
                        <div class="text-sm text-gray-600">Scheduled</div>
                    </div>
                </div>
                <div class="flex items-center space-x-3 p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
                    <div class="bg-green-500 rounded-full p-3">
                        <i class="fas fa-check-circle text-white text-sm"></i>
                    </div>
                    <div>
                        <div class="text-2xl font-bold text-green-600">{finished_count}</div>
                        <div class="text-sm text-gray-600">Finished</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
        <!-- Live Matches Section -->
        {f'<section class="mb-12" id="live-matches"><h2 class="text-2xl font-bold mb-6 flex items-center"><span class="w-3 h-3 bg-red-500 rounded-full mr-3 live-pulse"></span>Live Matches ({live_count})</h2><div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">{live_cards}</div></section>' if live_count > 0 else ''}
        
        <!-- Scheduled Matches Section -->
        {f'<section class="mb-12" id="scheduled-matches"><h2 class="text-2xl font-bold mb-6 flex items-center"><i class="fas fa-clock text-blue-500 mr-3"></i>Scheduled Matches ({scheduled_count})</h2><div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">{scheduled_cards}</div></section>' if scheduled_count > 0 else ''}
        
        <!-- Finished Matches Section -->
        {f'<section class="mb-12" id="finished-matches"><h2 class="text-2xl font-bold mb-6 flex items-center"><i class="fas fa-check-circle text-green-500 mr-3"></i>Finished Matches ({finished_count})</h2><div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">{finished_cards}</div></section>' if finished_count > 0 else ''}
        
        <!-- Empty State -->
        {f'<div class="text-center py-16"><i class="fas fa-futbol text-6xl text-gray-300 mb-4"></i><h3 class="text-xl font-semibold text-gray-600 mb-2">No matches found</h3><p class="text-gray-500">Run the scraper to populate the database with match data.</p></div>' if total_matches == 0 else ''}
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white mt-12">
        <div class="container mx-auto px-4 py-6">
            <div class="flex flex-col md:flex-row justify-between items-center">
                <div class="mb-4 md:mb-0">
                    <h3 class="text-xl font-bold mb-2">MarFutGames</h3>
                    <p class="text-gray-400 text-sm">Real-time football match data</p>
                </div>
                <div class="text-center md:text-right">
                    <p class="text-gray-400 text-sm">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p class="text-gray-500 text-xs mt-1">Generated automatically from database</p>
                </div>
            </div>
        </div>
    </footer>

    <!-- JavaScript -->
    <script>
        // Auto-refresh every 30 seconds
        setInterval(() => {{
            location.reload();
        }}, 30000);
        
        // Smooth scroll to sections
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}
            }});
        }});
        
        // Add click handlers to match cards
        document.querySelectorAll('.match-card').forEach(card => {{
            card.addEventListener('click', function() {{
                const url = this.dataset.url;
                if (url && url !== 'None') {{
                    window.open(url, '_blank');
                }}
            }});
        }});
    </script>
</body>
</html>"""
    
    return html


def generate_match_cards(matches, status_type):
    """Generate HTML for match cards."""
    if not matches:
        return ""
    
    cards_html = []
    
    for match in matches:
        match_id = match.get('match_id', 'N/A')
        home_team = match.get('home_team_name') or 'TBD'
        away_team = match.get('away_team_name') or 'TBD'
        home_score = match.get('home_score')
        away_score = match.get('away_score')
        match_time = match.get('match_time', '')
        league_name = match.get('league_name', '')
        match_url = match.get('match_url', '')
        current_minute = match.get('current_minute')
        match_stage = match.get('match_stage', '')
        has_tv = match.get('has_tv_icon', False)
        has_audio = match.get('has_audio_icon', False)
        
        # Determine score display
        if home_score is not None and away_score is not None:
            score_display = f"{home_score} - {away_score}"
        elif status_type == 'live' and current_minute:
            score_display = f"{home_score or 0} - {away_score or 0}"
        else:
            score_display = "VS"
        
        # Status badge
        if status_type == 'live':
            status_badge = '<span class="status-badge bg-red-100 text-red-800"><span class="w-2 h-2 bg-red-500 rounded-full mr-2 live-pulse inline-block"></span>LIVE</span>'
            if current_minute:
                status_badge += f' <span class="text-sm text-gray-600 ml-2">{current_minute}\'</span>'
        elif status_type == 'scheduled':
            status_badge = f'<span class="status-badge bg-blue-100 text-blue-800"><i class="fas fa-clock mr-1"></i>{match_time}</span>'
        elif status_type == 'finished':
            status_badge = '<span class="status-badge bg-green-100 text-green-800"><i class="fas fa-check-circle mr-1"></i>FT</span>'
        else:
            status_badge = f'<span class="status-badge bg-gray-100 text-gray-800">{match_time or "TBD"}</span>'
        
        # Icons
        icons_html = ""
        if has_tv:
            icons_html += '<i class="fas fa-tv text-blue-500" title="TV Broadcast"></i> '
        if has_audio:
            icons_html += '<i class="fas fa-volume-up text-green-500" title="Audio"></i> '
        
        # Card color based on status
        if status_type == 'live':
            card_bg = "bg-gradient-to-br from-red-50 to-red-100 border-red-300"
        elif status_type == 'scheduled':
            card_bg = "bg-white border-blue-200"
        else:
            card_bg = "bg-white border-gray-200"
        
        card_html = f"""
        <div class="match-card {card_bg} border-2 rounded-xl p-6 shadow-md cursor-pointer" data-url="{match_url}">
            <!-- League -->
            <div class="text-xs font-semibold text-gray-600 mb-3 flex items-center justify-between">
                <span class="truncate">{league_name or 'Unknown League'}</span>
                <div class="flex space-x-2 ml-2">
                    {icons_html}
                </div>
            </div>
            
            <!-- Teams -->
            <div class="space-y-4 mb-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-2 flex-1 min-w-0">
                        <div class="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                            <i class="fas fa-shield-alt text-gray-500"></i>
                        </div>
                        <span class="font-semibold text-gray-800 truncate">{home_team}</span>
                    </div>
                </div>
                
                <!-- Score -->
                <div class="text-center my-3">
                    <div class="score-display text-gray-800">{score_display}</div>
                    {f'<div class="text-xs text-gray-500 mt-1">{match_stage}</div>' if match_stage and status_type == 'live' else ''}
                </div>
                
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-2 flex-1 min-w-0">
                        <div class="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0">
                            <i class="fas fa-shield-alt text-gray-500"></i>
                        </div>
                        <span class="font-semibold text-gray-800 truncate">{away_team}</span>
                    </div>
                </div>
            </div>
            
            <!-- Status Badge -->
            <div class="flex items-center justify-between pt-3 border-t border-gray-200">
                {status_badge}
                {f'<a href="{match_url}" target="_blank" class="text-blue-600 hover:text-blue-800 text-sm font-medium" onclick="event.stopPropagation()"><i class="fas fa-external-link-alt mr-1"></i>Details</a>' if match_url and match_url != 'None' else ''}
            </div>
        </div>
        """
        
        cards_html.append(card_html)
    
    return "".join(cards_html)


if __name__ == "__main__":
    # Generate landing page
    output_file = generate_landing_page()
    print_success(f"✅ Landing page ready: {output_file}")
    print_info("Open the file in your browser to view the matches!")

