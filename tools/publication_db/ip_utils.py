# ip_utils.py
"""
Utility functions for getting IP address information
"""

import socket
import requests
from typing import Optional, Dict

def get_local_ip() -> str:
    """
    Get the local IP address of the device
    
    Returns:
        str: Local IP address (e.g., "192.168.1.100")
    """
    try:
        # Create a socket connection to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        # Connect to a public DNS server (doesn't actually send data)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"  # Fallback to localhost

def get_public_ip() -> Optional[str]:
    """
    Get the public IP address of the device (requires internet)
    
    Returns:
        str or None: Public IP address or None if unavailable
    """
    try:
        # Try multiple services in case one is down
        services = [
            "https://api.ipify.org?format=text",
            "https://icanhazip.com",
            "https://ident.me"
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=3)
                if response.status_code == 200:
                    return response.text.strip()
            except:
                continue
        
        return None
    except Exception:
        return None

def get_ip_info() -> Dict[str, str]:
    """
    Get both local and public IP addresses
    
    Returns:
        dict: Dictionary with 'local' and 'public' IP addresses
    """
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    return {
        'local': local_ip,
        'public': public_ip if public_ip else "Not available",
        'display': public_ip if public_ip else local_ip  # Use public if available, else local
    }

def format_ip_display(ip_info: Dict[str, str]) -> str:
    """
    Format IP information for display
    
    Args:
        ip_info: Dictionary from get_ip_info()
    
    Returns:
        str: Formatted string for display
    """
    if ip_info['public'] != "Not available":
        return f"{ip_info['public']} (Public)"
    else:
        return f"{ip_info['local']} (Local)"
