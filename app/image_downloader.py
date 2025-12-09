import os
import urllib.request
import urllib.parse
import hashlib
from typing import Optional

# Base directory for images in public folder
PUBLIC_IMAGE_DIR = "public/images"

def get_local_image_path(url: str, folder: str, custom_filename: Optional[str] = None) -> Optional[str]:
    """
    Download an image from a URL and save it locally.
    Returns the relative path to be used in the frontend (e.g., /images/teams/filename.png).
    
    Args:
        url: The URL of the image to download.
        folder: The subfolder to save the image in (e.g., 'teams', 'leagues').
        
    Returns:
        str: Relative path to the image, or None if failed.
    """
    if not url or not url.startswith('http'):
        return None
        
    try:
        # Create directory if it doesn't exist
        save_dir = os.path.join(PUBLIC_IMAGE_DIR, folder)
        os.makedirs(save_dir, exist_ok=True)
        
        # Generate filename
        # Try to get extension from URL, default to .png
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        ext = os.path.splitext(path)[1]
        if not ext:
            ext = '.png'

        if custom_filename:
            # Sanitize custom filename
            safe_name = "".join([c for c in custom_filename if c.isalnum() or c in ('-', '_')]).strip()
            filename = f"{safe_name}{ext}"
        else:
            # Generate a unique filename based on the URL hash
            url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
            filename = f"{url_hash}{ext}"
            
        file_path = os.path.join(save_dir, filename)
        
        # Check if file already exists
        if not os.path.exists(file_path):
            # Download the image
            # Add headers to mimic a browser to avoid 403s
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                with open(file_path, 'wb') as f:
                    f.write(response.read())
            print(f"⬇️  Downloaded image: {url} -> {file_path}")
        
        # Return relative path for frontend (remove public/)
        # public/images/teams/xyz.png -> /images/teams/xyz.png
        return f"/images/{folder}/{filename}"
        
    except Exception as e:
        print(f"⚠️  Failed to download image {url}: {e}")
        return None
