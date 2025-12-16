# publication_db_tool.py
"""
Publication Database Tool - Integration wrapper for BTSA app
This wraps the standalone publication database GUI for integration into the main app
"""

import tkinter as tk
from tkinter import messagebox
import sys
from pathlib import Path

# Add the publication_db directory to path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

print(f"[Publication DB] Loading from: {current_dir}")

try:
    from publication_db import PublicationDatabase
    from publication_db_main import PublicationDatabaseGUI

    DB_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import publication database modules: {e}")
    DB_AVAILABLE = False


class PublicationDatabaseTool(tk.Frame):
    """
    Wrapper class that makes the Publication Database compatible with BTSA's tool system
    """

    def __init__(self, parent):
        super().__init__(parent, bg="#305CDE")

        print("Initializing Publication Database Tool...")

        # Configure the frame to fill the available space
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if DB_AVAILABLE:
            try:
                # Create the actual database GUI inside this frame
                self.db_gui = PublicationDatabaseGUI(self)
                self.db_gui.pack(fill="both", expand=True)
                print("✓ Publication Database GUI loaded successfully")
            except Exception as e:
                print(f"✗ Error creating Publication Database GUI: {e}")
                import traceback
                traceback.print_exc()
                self._create_error_display(str(e))
        else:
            self._create_error_display("Database modules not available")

    def _create_error_display(self, error_msg):
        """Create an error display when the database can't be loaded"""
        error_frame = tk.Frame(self, bg="#305CDE")
        error_frame.pack(fill="both", expand=True, padx=40, pady=40)

        tk.Label(
            error_frame,
            text="⚠ Publication Database Error",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#305CDE"
        ).pack(pady=(20, 10))

        tk.Label(
            error_frame,
            text=f"Failed to load the Publication Database:\n\n{error_msg}",
            font=("Arial", 11),
            fg="lightcoral",
            bg="#305CDE",
            wraplength=500,
            justify="left"
        ).pack(pady=10)

        tk.Label(
            error_frame,
            text="Please ensure all required files are in tools/database/publication_db/:\n"
                 "• publication_db.py\n"
                 "• publication_db_main.py\n"
                 "• publication_db_form.py\n"
                 "• publication_db_results.py",
            font=("Arial", 10),
            fg="white",
            bg="#305CDE",
            justify="left"
        ).pack(pady=10)

    def reset_tool(self):
        """Reset the tool to initial state (called when showing the tool)"""
        if hasattr(self, 'db_gui'):
            try:
                # Return to main view and clear any search results
                self.db_gui.show_main_view()
                print("Publication Database tool reset")
            except Exception as e:
                print(f"Error resetting Publication Database: {e}")

    def clear_all(self):
        """Clear all data (alternative reset method)"""
        self.reset_tool()


# Standalone test code
if __name__ == "__main__":
    print("Testing Publication Database Tool...")

    root = tk.Tk()
    root.title("Publication Database Tool Test")
    root.geometry("900x700")
    root.configure(bg="#305CDE")

    # Create the tool
    tool = PublicationDatabaseTool(root)
    tool.pack(fill="both", expand=True)

    print("Tool created successfully. Starting main loop...")
    root.mainloop()