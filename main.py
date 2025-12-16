from gui.frame_manager import BioToolsApp
from tkinter import ttk, font as tkfont
import tkinter as tk
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Optimize for better font rendering (works in both WSL and Windows)
os.environ['GDK_BACKEND'] = 'x11'
os.environ['GDK_SCALE'] = '1'
os.environ['GDK_DPI_SCALE'] = '1'
os.environ['FREETYPE_PROPERTIES'] = 'truetype:interpreter-version=38'

def setup_fonts(root):
    """Configure better fonts for the application"""

    # Define font families in order of preference
    font_families = [
        'Segoe UI',        # Windows native
        'Ubuntu',          # Good for Linux
        'DejaVu Sans',     # Fallback
        'Liberation Sans',  # Final fallback
        'Arial'            # Universal fallback
    ]

    # Get available fonts
    available_fonts = tkfont.families()
    selected_font = 'TkDefaultFont'

    # Find first available font
    for font_family in font_families:
        if font_family in available_fonts:
            selected_font = font_family
            break

    # Set default fonts with good sizes
    default_font = (selected_font, 10)
    bold_font = (selected_font, 11, 'bold')
    heading_font = (selected_font, 14, 'bold')
    small_font = (selected_font, 10)

    # Apply to all widgets
    root.option_add('*Font', default_font)
    root.option_add('*Button*Font', bold_font)
    root.option_add('*Label*Font', default_font)
    root.option_add('*Entry*Font', default_font)
    root.option_add('*Text*Font', small_font)
    root.option_add('*Listbox*Font', default_font)
    root.option_add('*Menu*Font', default_font)

    print(f"✓ Using font: {selected_font}")

    return selected_font

def setup_theme(root):
    """Set up better visual theme"""
    try:
        style = ttk.Style()
        # Use a modern theme (works on both Windows and Linux)
        available_themes = style.theme_names()

        # Preference order
        preferred_themes = ['clam', 'alt', 'default', 'classic']

        for theme in preferred_themes:
            if theme in available_themes:
                style.theme_use(theme)
                print(f"✓ Using theme: {theme}")
                break

        # Customize colors for better appearance
        root.option_add('*Background', '#f0f0f0')
        root.option_add('*Foreground', '#000000')

    except Exception as e:
        print(f"Warning: Could not set theme: {e}")

def enable_dpi_awareness():
    """Enable DPI awareness on Windows for crisp rendering"""
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
        print("✓ DPI awareness enabled (Windows)")
    except:
        # Not on Windows or DPI setting failed - that's fine
        pass

def main():
    """Main application entry point"""

    # Enable DPI awareness (Windows only, ignored on Linux)
    enable_dpi_awareness()

    # Debug Tk initialization (your existing debug code)
    _old_tk = tk.Tk

    def debug_tk(*a, **k):
        import traceback
        print("DEBUG: tk.Tk() was called here:")
        traceback.print_stack(limit=5)
        root = _old_tk(*a, **k)

        # Apply font and theme improvements to the root window
        setup_fonts(root)
        setup_theme(root)

        return root

    tk.Tk = debug_tk

    # Create and run the application
    try:
        print("Starting Bio Tools GUI...")
        app = BioToolsApp()
        app.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
