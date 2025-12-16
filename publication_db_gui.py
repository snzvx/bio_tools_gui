# publication_db_gui.py
"""
Publication Database GUI Module - UPDATED
No mandatory fields + PDF upload and search functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import tempfile

# Import database module
try:
    from publication_db import PublicationDatabase

    DB_AVAILABLE = True
except ImportError:
    try:
        import sys

        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from publication_db import PublicationDatabase

        DB_AVAILABLE = True
    except ImportError:
        print("Warning: PublicationDatabase module not found.")
        DB_AVAILABLE = False


class PublicationDatabaseGUI(tk.Frame):
    def __init__(self, parent, main_app=None):
        """
        Initialize publication database GUI

        Args:
            parent: Parent widget
            main_app: Reference to main application for scrollbar integration
        """
        super().__init__(parent, bg="#305CDE")
        self.parent = parent
        self.main_app = main_app  # Reference to main application

        # Initialize database
        if DB_AVAILABLE:
            self.db = PublicationDatabase()
        else:
            self.db = None

        self.back_button_image = None
        self.load_back_button_image()

        # Track navigation history
        self.navigation_history = []

        # Store current publication being edited
        self.editing_pub_id = None

        # Store uploaded PDF data
        self.current_pdf_data = None
        self.current_pdf_filename = None

        self.setup_ttk_style()

        # Main container - will use main app's scrollbar
        self.main_container = tk.Frame(self, bg="#305CDE")
        self.main_container.pack(fill="both", expand=True)

        # Initialize all frame containers
        self.main_view_container = tk.Frame(self.main_container, bg="#305CDE")
        self.submission_container = tk.Frame(self.main_container, bg="#305CDE")
        self.detail_container = tk.Frame(self.main_container, bg="#305CDE")
        self.edit_container = tk.Frame(self.main_container, bg="#305CDE")

        # Create frames
        self.create_main_view_frame()
        self.create_submission_frame()

        # Show main view by default
        self.show_main_view()

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

    def load_back_button_image(self):
        """Load the back button image"""
        try:
            from pathlib import Path
            current_dir = Path(__file__).parent.parent.parent.parent
            image_path = current_dir / "assets" / "back-button-md.png"

            if image_path.exists():
                img = Image.open(image_path)
                img = img.resize((30, 30), Image.Resampling.LANCZOS)
                self.back_button_image = ImageTk.PhotoImage(img)
                print("✓ Back button image loaded successfully")
            else:
                print(f"Note: Back button image not found at {image_path}")
        except ImportError:
            print("Note: PIL/Pillow not installed.")
        except Exception as e:
            print(f"Note: Could not load back button image: {e}")

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
        """Create main publication database view - NO INTERNAL SCROLLBAR"""

        # Title
        title_label = tk.Label(
            self.main_view_container,
            text="Publication DB",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#305CDE"
        )
        title_label.pack(pady=(20, 15))

        # Description
        desc_text = (
            "Create and manage a personal publication database, which serves as a "
            "digital repository for articles and references of scientific literature."
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

        submission_text_frame = tk.Frame(submission_frame, bg="#305CDE")
        submission_text_frame.pack(anchor="w", fill=tk.X)

        submission_desc = tk.Label(
            submission_text_frame,
            text="Submit publications with any combination of fields. All fields are optional.",
            font=("Arial", 10),
            fg="white",
            bg="#305CDE",
            wraplength=500,
            justify=tk.LEFT,
            anchor="w"
        )
        submission_desc.pack(side=tk.LEFT, anchor="w")

        click_here_label = tk.Label(
            submission_text_frame,
            text="Click here",
            font=("Arial", 10, "bold"),
            fg="#4CAF50",
            bg="#305CDE",
            cursor="hand2"
        )
        click_here_label.pack(side=tk.LEFT)

        def on_enter(e):
            click_here_label.config(font=("Arial", 10, "bold", "underline"))

        def on_leave(e):
            click_here_label.config(font=("Arial", 10, "bold"))

        click_here_label.bind("<Button-1>", lambda e: self.navigate_to("submission"))
        click_here_label.bind("<Enter>", on_enter)
        click_here_label.bind("<Leave>", on_leave)

        submission_desc2 = tk.Label(
            submission_text_frame,
            text=" to submit a publication.",
            font=("Arial", 10),
            fg="white",
            bg="#305CDE",
            anchor="w"
        )
        submission_desc2.pack(side=tk.LEFT, anchor="w")

        # Separator
        separator = tk.Frame(self.main_view_container, bg="white", height=2)
        separator.pack(fill=tk.X, padx=60, pady=20)

        # Search Engine Section
        search_title = tk.Label(
            self.main_view_container,
            text="Search Engine",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#305CDE"
        )
        search_title.pack(pady=(10, 10))

        search_desc = tk.Label(
            self.main_view_container,
            text=(
                "To effectively find specific articles or references you can search for articles by using keywords, authors, or publication year.\n\n"
                "Now with PDF search capability - search for PDF files by filename."
            ),
            font=("Arial", 10),
            fg="white",
            bg="#305CDE",
            wraplength=600,
            justify=tk.CENTER
        )
        search_desc.pack(pady=(0, 15), padx=40)

        # Search type selection
        search_type_frame = tk.Frame(self.main_view_container, bg="#305CDE")
        search_type_frame.pack(fill=tk.X, padx=60, pady=(0, 10))

        tk.Label(
            search_type_frame,
            text="Search Type:",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#305CDE"
        ).pack(side=tk.LEFT)

        self.search_type = tk.StringVar(value="manual")

        manual_radio = tk.Radiobutton(
            search_type_frame,
            text="Manual Search",
            variable=self.search_type,
            value="manual",
            font=("Arial", 10),
            fg="white",
            bg="#305CDE",
            selectcolor="#305CDE",
            activebackground="#305CDE",
            activeforeground="white"
        )
        manual_radio.pack(side=tk.LEFT, padx=(20, 10))

        pdf_radio = tk.Radiobutton(
            search_type_frame,
            text="PDF Search",
            variable=self.search_type,
            value="pdf",
            font=("Arial", 10),
            fg="white",
            bg="#305CDE",
            selectcolor="#305CDE",
            activebackground="#305CDE",
            activeforeground="white"
        )
        pdf_radio.pack(side=tk.LEFT, padx=(10, 0))

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

        search_button = tk.Button(
            search_container,
            text="Search",
            command=self.perform_search,
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

        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        # Show All Publications button
        show_all_button = tk.Button(
            self.main_view_container,
            text="Show All Publications",
            command=self.show_all_publications,
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

        # Results display area - Hidden by default
        results_label = tk.Label(
            self.main_view_container,
            text="Search Results:",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#305CDE",
            anchor="w"
        )
        self.results_label_ref = results_label
        self.results_label_ref.pack(anchor="w", padx=60, pady=(10, 5))
        self.results_label_ref.pack_forget()  # Hidden initially

        results_frame = tk.Frame(self.main_view_container, bg="#305CDE")
        self.results_frame_ref = results_frame
        self.results_frame_ref.pack(fill=tk.BOTH, expand=True, padx=60, pady=(0, 20))
        self.results_frame_ref.pack_forget()  # Hidden initially

        # Results container - will use main app's scrollbar
        self.results_container = tk.Frame(self.results_frame_ref, bg="white")
        self.results_container.pack(fill=tk.BOTH, expand=True)

    def create_submission_frame(self):
        """Create simplified publication submission form with PDF upload - NO MANDATORY FIELDS"""

        # Header with back button and PDF upload
        header_frame = tk.Frame(self.submission_container, bg="#305CDE")
        header_frame.pack(fill=tk.X, pady=(10, 10))

        # Back button
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

        # Title
        tk.Label(
            header_frame,
            text="Submit Publication",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#305CDE"
        ).pack(side=tk.LEFT, expand=True)

        # PDF Upload button (top right)
        pdf_button = tk.Button(
            header_frame,
            text="📁 Upload PDF",
            command=self.upload_pdf,
            bg="#FF9800",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=5
        )
        pdf_button.pack(side=tk.RIGHT, padx=20)

        # PDF status label
        self.pdf_status_label = tk.Label(
            header_frame,
            text="No PDF uploaded",
            font=("Arial", 9),
            fg="#FFD54F",
            bg="#305CDE"
        )
        self.pdf_status_label.pack(side=tk.RIGHT, padx=(0, 10))

        # Form container
        form_container = tk.Frame(self.submission_container, bg="#305CDE")
        form_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        self.form_entries = {}

        # Fields - ALL OPTIONAL (no asterisks)
        fields = [
            ("Author(s):", "authors", 2),
            ("Publication Year:", "publication_year", 1),
            ("Article Title:", "article_title", 1),
            ("Journal Name:", "journal_name", 1),
            ("Volume:", "volume", 1),
            ("Issue:", "issue", 1),
            ("Page Range:", "page_range", 1),
            ("Abstract:", "abstract", 6),
        ]

        for label_text, field_name, height in fields:
            label = tk.Label(
                form_container,
                text=label_text,
                font=("Arial", 11, "bold"),
                fg="white",
                bg="#305CDE",
                anchor="w"
            )
            label.pack(anchor="w", pady=(10, 5))

            if height == 1:
                entry = tk.Entry(
                    form_container,
                    font=("Arial", 10),
                    bg="white",
                    fg="black",
                    relief=tk.FLAT,
                    bd=2
                )
                entry.pack(fill=tk.X, ipady=6)
                self.form_entries[field_name] = entry
            else:
                text_widget = tk.Text(
                    form_container,
                    font=("Arial", 10),
                    bg="white",
                    fg="black",
                    relief=tk.FLAT,
                    bd=2,
                    height=height,
                    wrap=tk.WORD
                )
                text_widget.pack(fill=tk.X)
                self.form_entries[field_name] = text_widget

        # Save button
        save_button = tk.Button(
            form_container,
            text="Save Publication",
            command=self.save_publication,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10
        )
        save_button.pack(pady=(20, 10))

        # Clear button
        clear_button = tk.Button(
            form_container,
            text="Clear Form",
            command=self.clear_form,
            bg="#E0E0E0",
            fg="#333333",
            font=("Arial", 10),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=8
        )
        clear_button.pack(pady=(5, 20))

    def upload_pdf(self):
        """Handle PDF file upload"""
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'rb') as file:
                    self.current_pdf_data = file.read()
                self.current_pdf_filename = os.path.basename(file_path)
                self.pdf_status_label.config(
                    text=f"PDF: {self.current_pdf_filename}",
                    fg="#4CAF50"
                )
                messagebox.showinfo("Success", f"PDF '{self.current_pdf_filename}' uploaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload PDF: {str(e)}")

    def show_edit_frame(self, pub):
        """Show edit form populated with publication data - NO MANDATORY FIELDS"""
        # Clear existing edit container
        for widget in self.edit_container.winfo_children():
            widget.destroy()

        # Hide other frames
        self.hide_all_frames()

        # Header with back button
        header_frame = tk.Frame(self.edit_container, bg="#305CDE")
        header_frame.pack(fill=tk.X, pady=(10, 10))

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
            text="Edit Publication",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#305CDE"
        ).pack(side=tk.LEFT, expand=True)

        # Form container
        form_container = tk.Frame(self.edit_container, bg="#305CDE")
        form_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        edit_entries = {}

        # Fields - ALL OPTIONAL (no asterisks)
        fields = [
            ("Author(s):", "authors", 2),
            ("Publication Year:", "publication_year", 1),
            ("Article Title:", "article_title", 1),
            ("Journal Name:", "journal_name", 1),
            ("Volume:", "volume", 1),
            ("Issue:", "issue", 1),
            ("Page Range:", "page_range", 1),
            ("Abstract:", "abstract", 6),
        ]

        for label_text, field_name, height in fields:
            label = tk.Label(
                form_container,
                text=label_text,
                font=("Arial", 11, "bold"),
                fg="white",
                bg="#305CDE",
                anchor="w"
            )
            label.pack(anchor="w", pady=(10, 5))

            if height == 1:
                entry = tk.Entry(
                    form_container,
                    font=("Arial", 10),
                    bg="white",
                    fg="black",
                    relief=tk.FLAT,
                    bd=2
                )
                entry.pack(fill=tk.X, ipady=6)
                edit_entries[field_name] = entry
            else:
                text_widget = tk.Text(
                    form_container,
                    font=("Arial", 10),
                    bg="white",
                    fg="black",
                    relief=tk.FLAT,
                    bd=2,
                    height=height,
                    wrap=tk.WORD
                )
                text_widget.pack(fill=tk.X)
                edit_entries[field_name] = text_widget

        # Populate form with publication data
        if pub['authors']:
            edit_entries['authors'].insert("1.0", pub['authors'])
        if pub['publication_year']:
            edit_entries['publication_year'].insert(0, str(pub['publication_year']))
        if pub['article_title']:
            edit_entries['article_title'].insert(0, pub['article_title'])
        if pub['journal_name']:
            edit_entries['journal_name'].insert(0, pub['journal_name'])
        if pub['volume']:
            edit_entries['volume'].insert(0, pub['volume'])
        if pub['issue']:
            edit_entries['issue'].insert(0, pub['issue'])
        if pub['page_range']:
            edit_entries['page_range'].insert(0, pub['page_range'])
        if pub.get('abstract'):
            edit_entries['abstract'].insert("1.0", pub['abstract'])

        # Button frame
        button_frame = tk.Frame(form_container, bg="#305CDE")
        button_frame.pack(pady=20)

        # Save button
        save_button = tk.Button(
            button_frame,
            text="Save Changes",
            command=lambda: self.update_publication(pub['id'], edit_entries),
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10
        )
        save_button.pack(side=tk.LEFT, padx=10)

        # Cancel button
        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=self.navigate_back,
            bg="#E0E0E0",
            fg="#333333",
            font=("Arial", 11),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10
        )
        cancel_button.pack(side=tk.LEFT, padx=10)

        # Show the edit frame
        self.edit_container.pack(fill="both", expand=True)

    def update_publication(self, pub_id, entries):
        """Update publication in database - NO MANDATORY FIELDS"""
        # Get form data
        authors = entries['authors'].get("1.0", tk.END).strip()
        publication_year = entries['publication_year'].get().strip()
        article_title = entries['article_title'].get().strip()
        journal_name = entries['journal_name'].get().strip()
        volume = entries['volume'].get().strip()
        issue = entries['issue'].get().strip()
        page_range = entries['page_range'].get().strip()
        abstract = entries['abstract'].get("1.0", tk.END).strip()

        # Validate year if provided
        if publication_year:
            try:
                year = int(publication_year)
                if year < 1900 or year > 2100:
                    messagebox.showerror(
                        "Invalid Year",
                        "Please enter a valid publication year (1900-2100) or leave empty"
                    )
                    return
            except ValueError:
                messagebox.showerror(
                    "Invalid Year",
                    "Please enter a valid publication year (1900-2100) or leave empty"
                )
                return

        # Update in database
        if self.db:
            try:
                success = self.db.update_publication(
                    pub_id=pub_id,
                    authors=authors if authors else None,
                    publication_year=int(publication_year) if publication_year else None,
                    article_title=article_title if article_title else None,
                    journal_name=journal_name if journal_name else None,
                    volume=volume if volume else None,
                    issue=issue if issue else None,
                    page_range=page_range if page_range else None,
                    abstract=abstract if abstract else None
                )
                if success:
                    messagebox.showinfo("Success", "Publication updated successfully!")
                    # Navigate back to detail view
                    updated_pub = self.db.get_publication(pub_id)
                    if updated_pub:
                        self.navigate_to("detail", updated_pub)
                else:
                    messagebox.showerror("Error", "Failed to update publication")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update publication:\n{str(e)}")
        else:
            messagebox.showerror("Error", "Database not available")

    def save_publication(self):
        """Handle publication submission - NO MANDATORY FIELDS"""
        # Get form data
        authors = self.form_entries['authors'].get("1.0", tk.END).strip()
        publication_year = self.form_entries['publication_year'].get().strip()
        article_title = self.form_entries['article_title'].get().strip()
        journal_name = self.form_entries['journal_name'].get().strip()
        volume = self.form_entries['volume'].get().strip()
        issue = self.form_entries['issue'].get().strip()
        page_range = self.form_entries['page_range'].get().strip()
        abstract = self.form_entries['abstract'].get("1.0", tk.END).strip()

        # Validate year if provided
        if publication_year:
            try:
                year = int(publication_year)
                if year < 1900 or year > 2100:
                    messagebox.showerror(
                        "Invalid Year",
                        "Please enter a valid publication year (1900-2100) or leave empty"
                    )
                    return
            except ValueError:
                messagebox.showerror(
                    "Invalid Year",
                    "Please enter a valid publication year (1900-2100) or leave empty"
                )
                return

        # Check if at least one field is filled
        if not any([authors, publication_year, article_title, journal_name, volume, issue, page_range, abstract,
                    self.current_pdf_data]):
            messagebox.showwarning(
                "Empty Form",
                "Please fill in at least one field or upload a PDF file."
            )
            return

        # Save to database
        if self.db:
            try:
                pub = self.db.add_publication(
                    authors=authors if authors else None,
                    publication_year=int(publication_year) if publication_year else None,
                    article_title=article_title if article_title else None,
                    journal_name=journal_name if journal_name else None,
                    volume=volume if volume else None,
                    issue=issue if issue else None,
                    page_range=page_range if page_range else None,
                    abstract=abstract if abstract else None,
                    pdf_data=self.current_pdf_data,
                    pdf_filename=self.current_pdf_filename
                )
                messagebox.showinfo(
                    "Success",
                    f"Publication submitted successfully!\n\n"
                    f"ID: {pub['id']}\n"
                    f"Title: {article_title if article_title else 'No title'}\n"
                    f"PDF: {'Yes' if self.current_pdf_data else 'No'}"
                )
                self.clear_form()
                self.navigate_to("main_view")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save publication:\n{str(e)}")
        else:
            messagebox.showerror("Error", "Database not available")

    def clear_form(self):
        """Clear all form fields and PDF data"""
        for field_name, widget in self.form_entries.items():
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            else:
                widget.delete(0, tk.END)

        # Clear PDF data
        self.current_pdf_data = None
        self.current_pdf_filename = None
        self.pdf_status_label.config(text="No PDF uploaded", fg="#FFD54F")

    def format_publication(self, pub):
        """
        Format publication for display
        """
        parts = []

        # Add available fields
        if pub['authors']:
            parts.append(pub['authors'])

        if pub['publication_year']:
            parts.append(str(pub['publication_year']))

        if pub['article_title']:
            parts.append(pub['article_title'])

        if pub['journal_name']:
            parts.append(pub['journal_name'])

        # Build volume/issue/page range section
        citation_parts = []
        if pub['volume']:
            vol_str = pub['volume']
            if pub['issue']:
                vol_str += f"({pub['issue']})"
            citation_parts.append(vol_str)

        if pub['page_range']:
            citation_parts.append(pub['page_range'])

        # Join all parts
        if parts:
            formatted = ". ".join(parts) + "."
            if citation_parts:
                formatted += f" {':'.join(citation_parts)}."
        else:
            formatted = f"Publication #{pub['id']} (No details provided)"

        return formatted

    def perform_search(self):
        """Perform search based on query and search type"""
        query = self.search_entry.get().strip()
        search_type = self.search_type.get()

        if not query:
            messagebox.showwarning("Empty Search", "Please enter a search term")
            return

        if self.db:
            results = self.db.search_publications(query, search_type)
            self.display_results(results, query, search_type)
        else:
            messagebox.showerror("Error", "Database not available")

    def show_all_publications(self):
        """Show all publications"""
        if self.db:
            results = self.db.get_all_publications()
            self.display_results(results, "All Publications", "manual")
        else:
            messagebox.showerror("Error", "Database not available")

    def display_results(self, results, query, search_type):
        """Display search results as clickable formatted labels"""
        # Clear previous results
        for widget in self.results_container.winfo_children():
            widget.destroy()

        # Show results section
        self.results_label_ref.pack(anchor="w", padx=60, pady=(10, 5))
        self.results_frame_ref.pack(fill=tk.BOTH, expand=True, padx=60, pady=(0, 20))

        if not results:
            no_results_label = tk.Label(
                self.results_container,
                text=f"No results found for: '{query}' (Search type: {search_type})",
                font=("Arial", 10),
                fg="white",
                bg="#305CDE",
                padx=10,
                pady=10,
                anchor="w",
                justify=tk.LEFT
            )
            no_results_label.pack(anchor="w", fill=tk.X)
        else:
            # Header
            header_label = tk.Label(
                self.results_container,
                text=f"Found {len(results)} result(s) for '{query}' (Search type: {search_type}):\n",
                font=("Arial", 10, "bold"),
                fg="white",
                bg="#305CDE",
                padx=10,
                pady=5,
                anchor="w",
                justify=tk.LEFT
            )
            header_label.pack(anchor="w", fill=tk.X)

            # Display each result as a clickable label
            for idx, pub in enumerate(results, 1):
                formatted_text = self.format_publication(pub)

                # Create a frame for each result
                result_frame = tk.Frame(self.results_container, bg="#305CDE", pady=5)
                result_frame.pack(anchor="w", fill=tk.X, padx=10)

                # Number label
                number_label = tk.Label(
                    result_frame,
                    text=f"{idx}.",
                    font=("Arial", 9, "bold"),
                    fg="white",
                    bg="#305CDE",
                    anchor="nw"
                )
                number_label.pack(side=tk.LEFT, anchor="n", padx=(0, 5))

                # Publication details as a clickable label (hyperlink style)
                result_label = tk.Label(
                    result_frame,
                    text=formatted_text,
                    font=("Arial", 9, "underline"),
                    fg="#4CAF50",  # Green color for hyperlink
                    bg="#305CDE",
                    anchor="w",
                    justify=tk.LEFT,
                    wraplength=500,
                    cursor="hand2"  # Change cursor to hand pointer
                )
                result_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

                # Bind click event to show detailed view
                result_label.bind("<Button-1>", lambda e, p=pub: self.navigate_to("detail", p))

                # Hover effects
                result_label.bind("<Enter>", lambda e, lbl=result_label: lbl.config(fg="#66BB6A"))
                result_label.bind("<Leave>", lambda e, lbl=result_label: lbl.config(fg="#4CAF50"))

                # Action buttons frame
                button_frame = tk.Frame(result_frame, bg="#305CDE")
                button_frame.pack(side=tk.RIGHT, padx=(10, 0))

                # PDF Download button (if PDF exists)
                if pub.get('pdf_data') is not None:
                    pdf_button = tk.Button(
                        button_frame,
                        text="📥 PDF",
                        command=lambda p=pub: self.download_pdf(p),
                        bg="#FF9800",
                        fg="white",
                        font=("Arial", 8, "bold"),
                        cursor="hand2",
                        relief=tk.FLAT,
                        bd=0,
                        padx=8,
                        pady=2
                    )
                    pdf_button.pack(side=tk.LEFT, padx=(0, 5))

                # Edit button
                edit_button = tk.Button(
                    button_frame,
                    text="Edit",
                    command=lambda p=pub: self.navigate_to("edit", p),
                    bg="#2196F3",
                    fg="white",
                    font=("Arial", 8, "bold"),
                    cursor="hand2",
                    relief=tk.FLAT,
                    bd=0,
                    padx=10,
                    pady=3
                )
                edit_button.pack(side=tk.LEFT, padx=(0, 5))

                # Delete button
                delete_button = tk.Button(
                    button_frame,
                    text="Delete",
                    command=lambda p=pub: self.delete_publication_confirm(p),
                    bg="#F44336",
                    fg="white",
                    font=("Arial", 8, "bold"),
                    cursor="hand2",
                    relief=tk.FLAT,
                    bd=0,
                    padx=10,
                    pady=3
                )
                delete_button.pack(side=tk.LEFT)

                # Optional: Add a subtle separator between results
                if idx < len(results):
                    separator = tk.Frame(self.results_container, bg="#1E3A8A", height=1)
                    separator.pack(fill=tk.X, padx=20, pady=3)

    def download_pdf(self, pub):
        """Download PDF file from database"""
        if self.db:
            save_path = filedialog.asksaveasfilename(
                title="Save PDF As",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=pub.get('pdf_filename', f"publication_{pub['id']}.pdf")
            )

            if save_path:
                try:
                    exported_path = self.db.export_pdf(pub['id'], save_path)
                    if exported_path:
                        messagebox.showinfo("Success", f"PDF downloaded successfully!\nSaved to: {exported_path}")
                    else:
                        messagebox.showerror("Error", "Failed to download PDF. File may not exist.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to download PDF: {str(e)}")

    def show_publication_detail(self, pub):
        """Show detailed view of a publication in a new frame"""
        # Hide other frames
        self.hide_all_frames()

        # Clear any existing content
        for widget in self.detail_container.winfo_children():
            widget.destroy()

        # Header with back button
        header_frame = tk.Frame(self.detail_container, bg="#305CDE")
        header_frame.pack(fill=tk.X, pady=(10, 10))

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

        # Content area - now with blue background
        content_frame = tk.Frame(self.detail_container, bg="#305CDE")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # Title - formatted publication citation
        title_text = self.format_publication(pub)
        title_label = tk.Label(
            content_frame,
            text=title_text,
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#305CDE",
            wraplength=700,
            justify=tk.LEFT,
            anchor="w"
        )
        title_label.pack(fill=tk.X, padx=20, pady=(10, 20))

        # Separator line
        separator = tk.Frame(content_frame, bg="white", height=2)
        separator.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Display publication details in a cleaner format
        details = [
            ("Authors:", pub['authors'] if pub['authors'] else "Not provided"),
            ("Publication Year:", pub['publication_year'] if pub['publication_year'] else "Not provided"),
            ("Article Title:", pub['article_title'] if pub['article_title'] else "Not provided"),
            ("Journal Name:", pub['journal_name'] if pub['journal_name'] else "Not provided"),
            ("Volume:", pub['volume'] if pub['volume'] else "Not provided"),
            ("Issue:", pub['issue'] if pub['issue'] else "Not provided"),
            ("Page Range:", pub['page_range'] if pub['page_range'] else "Not provided"),
        ]

        # Add Abstract if available
        if pub.get('abstract'):
            details.append(("Abstract:", pub['abstract']))
        else:
            details.append(("Abstract:", "Not provided"))

        # Add PDF info if available
        if pub.get('pdf_filename'):
            details.append(("PDF File:", pub['pdf_filename']))
        else:
            details.append(("PDF File:", "No PDF uploaded"))

        for label_text, value in details:
            detail_row = tk.Frame(content_frame, bg="#305CDE")
            detail_row.pack(fill=tk.X, padx=20, pady=8)

            tk.Label(
                detail_row,
                text=label_text,
                font=("Arial", 11, "bold"),
                fg="#4CAF50",
                bg="#305CDE",
                anchor="w",
                width=18
            ).pack(side=tk.LEFT, anchor="nw")

            value_label = tk.Label(
                detail_row,
                text=str(value),
                font=("Arial", 10),
                fg="white",
                bg="#305CDE",
                anchor="w",
                justify=tk.LEFT,
                wraplength=500
            )
            value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Metadata section (Created/Updated dates)
        metadata_separator = tk.Frame(content_frame, bg="white", height=1)
        metadata_separator.pack(fill=tk.X, padx=20, pady=(20, 10))

        metadata_info = [
            ("Created Date:", pub['created_date']),
            ("Updated Date:", pub['updated_date'])
        ]

        for label_text, value in metadata_info:
            meta_row = tk.Frame(content_frame, bg="#305CDE")
            meta_row.pack(fill=tk.X, padx=20, pady=5)

            tk.Label(
                meta_row,
                text=label_text,
                font=("Arial", 9),
                fg="#B0BEC5",
                bg="#305CDE",
                anchor="w",
                width=18
            ).pack(side=tk.LEFT, anchor="nw")

            tk.Label(
                meta_row,
                text=str(value),
                font=("Arial", 9),
                fg="#B0BEC5",
                bg="#305CDE",
                anchor="w",
                justify=tk.LEFT
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Action buttons
        button_frame = tk.Frame(content_frame, bg="#305CDE")
        button_frame.pack(pady=30)

        # PDF Download button (if PDF exists)
        if pub.get('pdf_data') is not None:
            pdf_button = tk.Button(
                button_frame,
                text="📥 Download PDF",
                command=lambda: self.download_pdf(pub),
                bg="#FF9800",
                fg="white",
                font=("Arial", 10, "bold"),
                cursor="hand2",
                relief=tk.FLAT,
                bd=0,
                padx=20,
                pady=10
            )
            pdf_button.pack(side=tk.LEFT, padx=10)

        tk.Button(
            button_frame,
            text="Edit",
            command=lambda: self.navigate_to("edit", pub),
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            padx=25,
            pady=10
        ).pack(side=tk.LEFT, padx=10)

        tk.Button(
            button_frame,
            text="Delete",
            command=lambda: self.delete_publication_confirm(pub),
            bg="#F44336",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            padx=25,
            pady=10
        ).pack(side=tk.LEFT, padx=10)

        # Show the detail frame
        self.detail_container.pack(fill="both", expand=True)

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
        self.submission_container.pack(fill="both", expand=True)

    def delete_publication_confirm(self, pub):
        """Confirm and delete publication"""
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this publication?\n\n"
            f"Title: {pub['article_title'] if pub['article_title'] else 'No title'}\n"
            f"Authors: {pub['authors'] if pub['authors'] else 'Not provided'}"
        )

        if result and self.db:
            if self.db.delete_publication(pub['id']):
                messagebox.showinfo("Success", "Publication deleted successfully!")
                self.navigate_to("main_view")
            else:
                messagebox.showerror("Error", "Failed to delete publication.")

    def on_frame_show(self):
        """Called when this frame becomes visible in the main application"""
        # If your main app has a method to update scroll region, call it here
        if hasattr(self.main_app, 'update_scroll_region'):
            self.main_app.update_scroll_region()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Publication Database")
    root.geometry("800x700")
    root.configure(bg="#305CDE")

    app = PublicationDatabaseGUI(root)
    app.pack(fill="both", expand=True)

    root.mainloop()