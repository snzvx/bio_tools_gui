# tools/database/sequence_db/sequence_db_tool.py
"""
Sequence Database Tool - Integration wrapper for BTSA app
This wraps the standalone sequence database GUI for integration into the main app
"""

import tkinter as tk
from tkinter import messagebox
import sys
from pathlib import Path

# Add the sequence_db directory to path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

print(f"[Sequence DB] Loading from: {current_dir}")

try:
    from sequence_db import SequenceDatabase
    from sequence_db_main import SequenceDatabaseGUI

    DB_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import sequence database modules: {e}")
    DB_AVAILABLE = False


class SequenceDatabaseTool(tk.Frame):
    """
    Wrapper class that makes the Sequence Database compatible with BTSA's tool system
    """

    def __init__(self, parent):
        super().__init__(parent, bg="#305CDE")

        print("Initializing Sequence Database Tool...")

        # Configure the frame to fill the available space
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if DB_AVAILABLE:
            try:
                # Create the actual database GUI inside this frame
                self.db_gui = SequenceDatabaseGUI(self)
                self.db_gui.pack(fill="both", expand=True)
                print("✓ Sequence Database GUI loaded successfully")
            except Exception as e:
                print(f"✗ Error creating Sequence Database GUI: {e}")
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
            text="⚠ Sequence Database Error",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#305CDE"
        ).pack(pady=(20, 10))

        tk.Label(
            error_frame,
            text=f"Failed to load the Sequence Database:\n\n{error_msg}",
            font=("Arial", 11),
            fg="lightcoral",
            bg="#305CDE",
            wraplength=500,
            justify="left"
        ).pack(pady=10)

        tk.Label(
            error_frame,
            text="Please ensure all required files are in tools/sequence_db/:\n"
                 "• sequence_db.py\n"
                 "• sequence_db_main.py\n"
                 "• sequence_db_form.py\n"
                 "• sequence_db_results.py",
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
                print("Sequence Database tool reset")
            except Exception as e:
                print(f"Error resetting Sequence Database: {e}")

    def clear_all(self):
        """Clear all data (alternative reset method)"""
        self.reset_tool()


# Standalone test code
if __name__ == "__main__":
    print("Testing Sequence Database Tool...")

    root = tk.Tk()
    root.title("Sequence Database Tool Test")
    root.geometry("900x700")
    root.configure(bg="#305CDE")

    # Create the tool
    tool = SequenceDatabaseTool(root)
    tool.pack(fill="both", expand=True)

    print("Tool created successfully. Starting main loop...")
    root.mainloop()