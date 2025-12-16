"""
Main Sequence Database GUI Module
"""

import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import sys
import os

# Try to import PIL for back button image
try:
    from PIL import Image, ImageTk

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available for back button image")

try:
    from sequence_db import SequenceDatabase

    DB_AVAILABLE = True
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from sequence_db import SequenceDatabase

        DB_AVAILABLE = True
    except ImportError:
        print("Warning: SequenceDatabase module not found.")
        DB_AVAILABLE = False

from sequence_db_form import SequenceFormGUI
from sequence_db_results import SequenceResultsGUI


class SequenceDatabaseGUI(tk.Frame):
    def __init__(self, parent):
        """Initialize sequence database GUI"""
        super().__init__(parent, bg="#305CDE")
        self.parent = parent

        if DB_AVAILABLE:
            self.db = SequenceDatabase()
        else:
            self.db = None

        # LOAD BACK BUTTON IMAGE
        self.back_button_image = None
        self._load_back_button_image()

        self.navigation_history = []
        self.setup_ttk_style()

        self.main_container = tk.Frame(self, bg="#305CDE")
        self.main_container.pack(fill="both", expand=True)

        self.main_view_container = tk.Frame(self.main_container, bg="#305CDE")
        self.submission_container = tk.Frame(self.main_container, bg="#305CDE")
        self.detail_container = tk.Frame(self.main_container, bg="#305CDE")
        self.edit_container = tk.Frame(self.main_container, bg="#305CDE")

        # PASS BACK BUTTON IMAGE TO FORM GUI
        self.form_gui = SequenceFormGUI(
            self.submission_container,
            self.db,
            self.back_button_image,
            self.navigate_back,
            self.navigate_to
        )

        self.results_gui = SequenceResultsGUI(
            self.main_view_container,
            self.db,
            self.navigate_to
        )

        self.create_main_view_frame()
        self.show_main_view()

    def _load_back_button_image(self):
        """Load back button image with multiple path strategies"""
        if not PIL_AVAILABLE:
            print("✗ Sequence DB: PIL not available, cannot load back button image")
            return

        # Strategy 1: Try relative to this file (for when run as part of main app)
        try:
            current_file = Path(__file__).resolve()
            print(f"[DEBUG] Current file: {current_file}")

            # Navigate up to find bio_tools_gui root
            # From: bio_tools_gui/tools/database/sequence_db/sequence_db_main.py
            # To:   bio_tools_gui/assets/back-button-md.png
            project_root = current_file.parent.parent.parent.parent
            image_path = project_root / "assets" / "back-button-md.png"

            print(f"[DEBUG] Strategy 1 - Project root: {project_root}")
            print(f"[DEBUG] Strategy 1 - Looking for image at: {image_path}")

            if image_path.exists():
                img = Image.open(image_path)
                img = img.resize((32, 32), Image.Resampling.LANCZOS)
                self.back_button_image = ImageTk.PhotoImage(img)
                print(f"✓ Sequence DB: Back button image loaded from: {image_path}")
                return
        except Exception as e:
            print(f"✗ Sequence DB: Strategy 1 failed: {e}")

        # Strategy 2: Try using sys.path[0] (script directory)
        try:
            if hasattr(sys, 'path') and sys.path:
                script_dir = Path(sys.path[0]).resolve()
                image_path = script_dir / "assets" / "back-button-md.png"

                print(f"[DEBUG] Strategy 2 - Script dir: {script_dir}")
                print(f"[DEBUG] Strategy 2 - Looking for image at: {image_path}")

                if image_path.exists():
                    img = Image.open(image_path)
                    img = img.resize((32, 32), Image.Resampling.LANCZOS)
                    self.back_button_image = ImageTk.PhotoImage(img)
                    print(f"✓ Sequence DB: Back button image loaded from: {image_path}")
                    return
        except Exception as e:
            print(f"✗ Sequence DB: Strategy 2 failed: {e}")

        # Strategy 3: Try current working directory
        try:
            cwd = Path.cwd()
            image_path = cwd / "assets" / "back-button-md.png"

            print(f"[DEBUG] Strategy 3 - CWD: {cwd}")
            print(f"[DEBUG] Strategy 3 - Looking for image at: {image_path}")

            if image_path.exists():
                img = Image.open(image_path)
                img = img.resize((32, 32), Image.Resampling.LANCZOS)
                self.back_button_image = ImageTk.PhotoImage(img)
                print(f"✓ Sequence DB: Back button image loaded from: {image_path}")
                return
        except Exception as e:
            print(f"✗ Sequence DB: Strategy 3 failed: {e}")

        # Strategy 4: Search for assets folder in parent directories
        try:
            current = Path(__file__).resolve().parent
            for _ in range(5):  # Search up to 5 levels up
                assets_path = current / "assets" / "back-button-md.png"
                print(f"[DEBUG] Strategy 4 - Checking: {assets_path}")

                if assets_path.exists():
                    img = Image.open(assets_path)
                    img = img.resize((32, 32), Image.Resampling.LANCZOS)
                    self.back_button_image = ImageTk.PhotoImage(img)
                    print(f"✓ Sequence DB: Back button image loaded from: {assets_path}")
                    return
                current = current.parent
        except Exception as e:
            print(f"✗ Sequence DB: Strategy 4 failed: {e}")

        print("✗ Sequence DB: All strategies failed - back button image not found")
        print(f"   Please ensure back-button-md.png exists in: bio_tools_gui/assets/")
        self.back_button_image = None

    def setup_ttk_style(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')

        style.configure("Vertical.TScrollbar",
                        background="#305CDE",
                        troughcolor="#F5F5F5",
                        bordercolor="#305CDE",
                        arrowcolor="white",
                        relief="flat")

        style.map("Vertical.TScrollbar",
                  background=[('active', '#1976D2'), ('!active', '#305CDE')])

    def navigate_to(self, frame_name, *args):
        """Navigate to a specific frame and track history"""
        current_frame = self.get_current_frame_name()
        if current_frame:
            self.navigation_history.append((current_frame, args))

        if frame_name == "main_view":
            self.show_main_view()
        elif frame_name == "submission":
            self.show_submission_frame()
        elif frame_name == "detail":
            self.show_sequence_detail(args[0])
        elif frame_name == "edit":
            self.show_edit_frame(args[0])

    def navigate_back(self):
        """Navigate back to previous frame"""
        if self.navigation_history:
            previous_frame, args = self.navigation_history.pop()
            if previous_frame == "main_view":
                self.show_main_view()
            elif previous_frame == "submission":
                self.show_submission_frame()
            elif previous_frame == "detail":
                self.show_sequence_detail(args[0])
            elif previous_frame == "edit":
                self.show_edit_frame(args[0])
        else:
            self.show_main_view()

    def get_current_frame_name(self):
        """Get the name of the currently displayed frame"""
        if self.main_view_container.winfo_ismapped():
            return "main_view"
        elif self.submission_container.winfo_ismapped():
            return "submission"
        elif self.detail_container.winfo_ismapped():
            return "detail"
        elif self.edit_container.winfo_ismapped():
            return "edit"
        return None

    def create_main_view_frame(self):
        """Create main sequence database view"""
        title_label = tk.Label(
            self.main_view_container,
            text="Sequence Database",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#305CDE"
        )
        title_label.pack(pady=(20, 15))

        desc_text = (
            "Create and maintain a personal sequence database (DB) that archive "
            "the primary structures of major biological macromolecules, including DNA, RNA, "
            "and proteins; primarily on your specific field of study."
        )
        desc_label = tk.Label(
            self.main_view_container,
            text=desc_text,
            font=("Arial", 10),
            fg="white",
            bg="#305CDE",
            wraplength=600,
            justify=tk.CENTER
        )
        desc_label.pack(pady=(0, 20), padx=40)

        # Submission Section
        submission_frame = tk.Frame(self.main_view_container, bg="#305CDE")
        submission_frame.pack(fill=tk.X, padx=60, pady=(10, 20))

        submission_title = tk.Label(
            submission_frame,
            text="Submission:",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#305CDE",
            anchor="w"
        )
        submission_title.pack(anchor="w", pady=(0, 8))

        user_info_frame = tk.Frame(self.main_view_container, bg="#305CDE")
        user_info_frame.pack(fill=tk.X, padx=60, pady=(10, 0))

        user_info_text = (
            "First you have to provide the following personal information:\n"
            "• Name (user)\n"
            "• Affiliation\n"
            "• Mobile phone number\n\n"
            "BTSA is not liable for errors, inaccuracies, or consequences arising from the information "
            "users provide on that database platform. Users are solely accountable for the data they enter.\n\n"
            "To submit a DNA/RNA/protein sequence data in the database, "
        )

        user_info_label = tk.Label(
            user_info_frame,
            text=user_info_text,
            font=("Arial", 9),
            fg="white",
            bg="#305CDE",
            wraplength=550,
            justify=tk.LEFT,
            anchor="w"
        )
        user_info_label.pack(anchor="w", pady=(5, 0), side=tk.LEFT)

        click_here_label = tk.Label(
            user_info_frame,
            text="click here",
            font=("Arial", 9, "bold", "underline"),
            fg="#4CAF50",
            bg="#305CDE",
            cursor="hand2"
        )
        click_here_label.pack(side=tk.LEFT)

        click_here_label.bind("<Button-1>", lambda e: self.navigate_to("submission"))

        # Separator
        separator = tk.Frame(self.main_view_container, bg="white", height=2)
        separator.pack(fill=tk.X, padx=60, pady=20)

        # Search Engine Section
        search_title = tk.Label(
            self.main_view_container,
            text="Sequence DB Search Engine",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#305CDE"
        )
        search_title.pack(pady=(10, 10))

        search_desc = tk.Label(
            self.main_view_container,
            text="Search for sequences by gene name, protein name, organism name, or accession number.",
            font=("Arial", 10),
            fg="white",
            bg="#305CDE",
            wraplength=600,
            justify=tk.CENTER
        )
        search_desc.pack(pady=(0, 15), padx=40)

        # Search box with button
        search_container = tk.Frame(self.main_view_container, bg="#305CDE")
        search_container.pack(fill=tk.X, padx=60, pady=(0, 20))

        self.search_entry = tk.Entry(
            search_container,
            font=("Arial", 11),
            bg="white",
            fg="black",
            relief=tk.FLAT,
            bd=2
        )
        self.search_entry.pack(fill=tk.X, side=tk.LEFT, expand=True, ipady=8)
        self.search_entry.bind("<Return>", lambda e: self.results_gui.perform_search())

        search_button = tk.Button(
            search_container,
            text="Search",
            command=self.results_gui.perform_search,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=8
        )
        search_button.pack(side=tk.RIGHT, padx=(10, 0))

        clear_button = tk.Button(
            search_container,
            text="Clear",
            command=lambda: self.search_entry.delete(0, tk.END),
            bg="#E0E0E0",
            fg="#333333",
            font=("Arial", 10),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=8
        )
        clear_button.pack(side=tk.RIGHT, padx=(0, 10))

        self.results_gui.parent_container = self.main_view_container
        self.results_gui.search_entry = self.search_entry

        # Show All button
        show_all_button = tk.Button(
            self.main_view_container,
            text="Show All Sequences",
            command=self.results_gui.show_all_sequences,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=8
        )
        show_all_button.pack(pady=(10, 20))

        # Results display area
        results_label = tk.Label(
            self.main_view_container,
            text="Search Results:",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#305CDE",
            anchor="w"
        )
        self.results_gui.results_label_ref = results_label
        self.results_gui.results_label_ref.pack(anchor="w", padx=60, pady=(10, 5))
        self.results_gui.results_label_ref.pack_forget()

        results_frame = tk.Frame(self.main_view_container, bg="#305CDE")
        self.results_gui.results_frame_ref = results_frame
        self.results_gui.results_frame_ref.pack(fill=tk.BOTH, expand=True, padx=60, pady=(0, 20))
        self.results_gui.results_frame_ref.pack_forget()

        self.results_gui.results_container = tk.Frame(self.results_gui.results_frame_ref, bg="white")
        self.results_gui.results_container.pack(fill=tk.BOTH, expand=True)

    def show_sequence_detail(self, seq):
        """Show detailed view of a sequence"""
        self.hide_all_frames()

        for widget in self.detail_container.winfo_children():
            widget.destroy()

        header_frame = tk.Frame(self.detail_container, bg="#305CDE")
        header_frame.pack(fill=tk.X, pady=(10, 10))

        back_btn = tk.Button(
            header_frame,
            text="← Back",
            command=self.navigate_back,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=5
        )
        back_btn.pack(side=tk.LEFT, padx=20)

        tk.Label(
            header_frame,
            text="Sequence Details",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#305CDE"
        ).pack(side=tk.LEFT, expand=True)

        self.results_gui.display_sequence_details(self.detail_container, seq, self.navigate_to,
                                                  self.delete_sequence_confirm)

        self.detail_container.pack(fill="both", expand=True)

    def show_edit_frame(self, seq):
        """Show edit form populated with sequence data"""
        self.hide_all_frames()

        self.form_gui.show_edit_form(self.edit_container, seq, self.update_sequence, self.navigate_back)
        self.edit_container.pack(fill="both", expand=True)

    def update_sequence(self, seq_id, entries):
        """Update sequence in database"""
        success = self.form_gui.update_sequence_data(seq_id, entries)
        if success and self.db:
            updated_seq = self.db.get_sequence(seq_id)
            if updated_seq:
                self.navigate_to("detail", updated_seq)

    def delete_sequence_confirm(self, seq):
        """Confirm and delete sequence"""
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this sequence?\n\n"
            f"Gene: {seq['gene_name'] if seq['gene_name'] else 'Not provided'}\n"
            f"Accession: {seq['accession_number'] if seq['accession_number'] else 'Not provided'}"
        )

        if result and self.db:
            if self.db.delete_sequence(seq['id']):
                messagebox.showinfo("Success", "Sequence deleted successfully!")
                self.navigate_to("main_view")
            else:
                messagebox.showerror("Error", "Failed to delete sequence.")

    def hide_all_frames(self):
        """Hide all frames"""
        self.main_view_container.pack_forget()
        self.submission_container.pack_forget()
        self.detail_container.pack_forget()
        self.edit_container.pack_forget()

    def show_main_view(self):
        """Show main database view"""
        self.hide_all_frames()
        self.main_view_container.pack(fill="both", expand=True)

    def show_submission_frame(self):
        """Show submission form"""
        self.hide_all_frames()
        self.form_gui.create_submission_form()
        self.submission_container.pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Sequence Database")
    root.geometry("800x700")
    root.configure(bg="#305CDE")

    app = SequenceDatabaseGUI(root)
    app.pack(fill="both", expand=True)

    root.mainloop()