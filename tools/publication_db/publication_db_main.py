"""
Main Publication Database GUI Module
MODIFIED: Fixed white background to blue theme
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
    from publication_db import PublicationDatabase
    DB_AVAILABLE = True
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from publication_db import PublicationDatabase
        DB_AVAILABLE = True
    except ImportError:
        print("Warning: PublicationDatabase module not found.")
        DB_AVAILABLE = False

from publication_db_form import PublicationFormGUI
from publication_db_results import PublicationResultsGUI
from publication_db_pdf_viewer import PDFViewerGUI


class PublicationDatabaseGUI(tk.Frame):
    def __init__(self, parent, main_app=None):
        """
        Initialize publication database GUI

        Args:
            parent: Parent widget
            main_app: Optional reference to main application (for compatibility)
        """
        super().__init__(parent, bg="#305CDE")
        self.parent = parent
        self.main_app = main_app

        if DB_AVAILABLE:
            self.db = PublicationDatabase()
        else:
            self.db = None

        self.back_button_image = None
        self._load_back_button_image()

        self.navigation_history = []
        self.setup_ttk_style()

        self.main_container = tk.Frame(self, bg="#305CDE")
        self.main_container.pack(fill="both", expand=True)

        # Initialize containers
        self.main_view_container = tk.Frame(self.main_container, bg="#305CDE")
        self.submission_container = tk.Frame(self.main_container, bg="#305CDE")
        self.detail_container = tk.Frame(self.main_container, bg="#305CDE")
        self.edit_container = tk.Frame(self.main_container, bg="#305CDE")
        self.pdf_viewer_container = tk.Frame(self.main_container, bg="#305CDE")

        # Initialize GUI components
        self.form_gui = PublicationFormGUI(
            self.submission_container,
            self.db,
            self.back_button_image,
            self.navigate_back,
            self.navigate_to
        )

        self.results_gui = PublicationResultsGUI(
            self.main_view_container,
            self.db,
            self.navigate_to
        )

        # Initialize PDF viewer
        self.pdf_viewer = PDFViewerGUI(
            self.pdf_viewer_container,
            self.back_button_image,
            self.navigate_back
        )

        self.create_main_view_frame()
        self.show_main_view()

    def _load_back_button_image(self):
        """Load back button image with multiple path strategies"""
        if not PIL_AVAILABLE:
            print("✗ Publication DB: PIL not available, cannot load back button image")
            return

        try:
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent
            image_path = project_root / "assets" / "back-button-md.png"

            if image_path.exists():
                img = Image.open(image_path)
                img = img.resize((32, 32), Image.Resampling.LANCZOS)
                self.back_button_image = ImageTk.PhotoImage(img)
                print(f"✓ Publication DB: Back button image loaded from: {image_path}")
                return
        except Exception as e:
            print(f"✗ Publication DB: Strategy 1 failed: {e}")

        try:
            if hasattr(sys, 'path') and sys.path:
                script_dir = Path(sys.path[0]).resolve()
                image_path = script_dir / "assets" / "back-button-md.png"

                if image_path.exists():
                    img = Image.open(image_path)
                    img = img.resize((32, 32), Image.Resampling.LANCZOS)
                    self.back_button_image = ImageTk.PhotoImage(img)
                    print(f"✓ Publication DB: Back button image loaded from: {image_path}")
                    return
        except Exception as e:
            print(f"✗ Publication DB: Strategy 2 failed: {e}")

        try:
            cwd = Path.cwd()
            image_path = cwd / "assets" / "back-button-md.png"

            if image_path.exists():
                img = Image.open(image_path)
                img = img.resize((32, 32), Image.Resampling.LANCZOS)
                self.back_button_image = ImageTk.PhotoImage(img)
                print(f"✓ Publication DB: Back button image loaded from: {image_path}")
                return
        except Exception as e:
            print(f"✗ Publication DB: Strategy 3 failed: {e}")

        print("✗ Publication DB: All strategies failed - back button image not found")
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
            self.show_publication_detail(args[0])
        elif frame_name == "edit":
            self.show_edit_frame(args[0])
        elif frame_name == "pdf_viewer":
            self.show_pdf_viewer(args[0])

    def navigate_back(self):
        """Navigate back to previous frame"""
        if self.navigation_history:
            previous_frame, args = self.navigation_history.pop()
            if previous_frame == "main_view":
                self.show_main_view()
            elif previous_frame == "submission":
                self.show_submission_frame()
            elif previous_frame == "detail":
                self.show_publication_detail(args[0])
            elif previous_frame == "edit":
                self.show_edit_frame(args[0])
            elif previous_frame == "pdf_viewer":
                self.show_pdf_viewer(args[0])
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
        elif self.pdf_viewer_container.winfo_ismapped():
            return "pdf_viewer"
        return None

    def create_main_view_frame(self):
        """Create main publication database view"""
        title_label = tk.Label(
            self.main_view_container,
            text="Publication Database",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#305CDE"
        )
        title_label.pack(pady=(20, 15))

        desc_text = (
            "Create and manage a personal publication database (DB), which serves as a digital repository "
            "for articles and references of existing scientific literature, mostly on your research area of interest."
        )
        desc_label = tk.Label(
            self.main_view_container,
            text=desc_text,
            font=("Arial", 10),
            fg="white",
            bg="#305CDE",
            wraplength=700,
            justify=tk.CENTER
        )
        desc_label.pack(pady=(0, 20), padx=20)

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

        info_frame = tk.Frame(self.main_view_container, bg="#305CDE")
        info_frame.pack(fill=tk.X, padx=60, pady=(10, 0))

        info_text = "To submit a publication, you'll need the journal, year, title, author, abstract, and you can upload PDF file for the publication. "

        info_label = tk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 9),
            fg="white",
            bg="#305CDE",
            wraplength=600,
            justify=tk.LEFT,
            anchor="w"
        )
        info_label.pack(anchor="w", pady=(5, 0), side=tk.LEFT)

        click_here_label = tk.Label(
            info_frame,
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

        # Search Box Section
        search_title = tk.Label(
            self.main_view_container,
            text="Search box",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#305CDE"
        )
        search_title.pack(pady=(10, 10))

        search_desc = tk.Label(
            self.main_view_container,
            text=(
                "To effectively find specific articles or references you can search for articles by using "
                "keywords, authors, publication year, or any field in the database. "
                "Results will display the article title."
            ),
            font=("Arial", 10),
            fg="white",
            bg="#305CDE",
            wraplength=700,
            justify=tk.CENTER
        )
        search_desc.pack(pady=(0, 15), padx=20)

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

        # FIXED: Changed background from white to blue
        self.results_gui.results_container = tk.Frame(self.results_gui.results_frame_ref, bg="#305CDE")
        self.results_gui.results_container.pack(fill=tk.BOTH, expand=True)

    def show_pdf_viewer(self, pub):
        """Show PDF viewer for a publication"""
        if not pub.get('pdf_data'):
            messagebox.showerror("Error", "No PDF available for this publication")
            return

        self.hide_all_frames()

        # Show PDF using the viewer
        self.pdf_viewer.show_pdf(pub['pdf_data'], pub.get('pdf_filename', 'document.pdf'))

        self.pdf_viewer_container.pack(fill="both", expand=True)

    def show_publication_detail(self, pub):
        """Show detailed view of a publication with View PDF button"""
        self.hide_all_frames()

        for widget in self.detail_container.winfo_children():
            widget.destroy()

        header_frame = tk.Frame(self.detail_container, bg="#305CDE")
        header_frame.pack(fill=tk.X, pady=(10, 10))

        # Use image back button if available
        if self.back_button_image:
            back_btn = tk.Button(
                header_frame,
                image=self.back_button_image,
                command=self.navigate_back,
                bg="#305CDE",
                fg="white",
                cursor="hand2",
                relief=tk.FLAT,
                bd=0,
                padx=5,
                pady=5
            )
            back_btn.image = self.back_button_image
        else:
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
            text="Publication Details",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#305CDE"
        ).pack(side=tk.LEFT, expand=True)

        # Modified to pass view_pdf_callback
        self.results_gui.display_publication_details(
            self.detail_container,
            pub,
            self.navigate_to,
            self.delete_publication_confirm,
            self.back_button_image,
            view_pdf_callback=lambda p: self.navigate_to("pdf_viewer", p)
        )

        self.detail_container.pack(fill="both", expand=True)

    def show_edit_frame(self, pub):
        """Show edit form populated with publication data"""
        self.hide_all_frames()

        self.form_gui.show_edit_form(self.edit_container, pub, self.update_publication, self.navigate_back)
        self.edit_container.pack(fill="both", expand=True)

    def update_publication(self, pub_id, entries):
        """Update publication in database"""
        success = self.form_gui.update_publication_data(pub_id, entries)
        if success and self.db:
            updated_pub = self.db.get_publication(pub_id)
            if updated_pub:
                self.navigate_to("detail", updated_pub)

    def delete_publication_confirm(self, pub):
        """Confirm and delete publication"""
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this publication?\n\n"
            f"Title: {pub['title'] if pub['title'] else 'Not provided'}"
        )

        if result and self.db:
            if self.db.delete_publication(pub['id']):
                messagebox.showinfo("Success", "Publication deleted successfully!")
                self.navigate_to("main_view")
            else:
                messagebox.showerror("Error", "Failed to delete publication.")

    def hide_all_frames(self):
        """Hide all frames"""
        self.main_view_container.pack_forget()
        self.submission_container.pack_forget()
        self.detail_container.pack_forget()
        self.edit_container.pack_forget()
        self.pdf_viewer_container.pack_forget()

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
    root.title("Publication Database")
    root.geometry("800x700")
    root.configure(bg="#305CDE")

    app = PublicationDatabaseGUI(root)
    app.pack(fill="both", expand=True)

    root.mainloop()