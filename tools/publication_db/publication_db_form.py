# publication_db_form.py
"""
Publication Database Form GUI Module
FIXED: Better error handling and null checks
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import os


class PublicationFormGUI:
    def __init__(self, parent_container, db, back_button_image, navigate_back_callback, navigate_to_callback):
        """Initialize the form GUI component"""
        self.parent_container = parent_container
        self.db = db
        self.back_button_image = back_button_image
        self.navigate_back = navigate_back_callback
        self.navigate_to = navigate_to_callback

        self.form_entries = {}
        self.current_pdf_data = None
        self.current_pdf_filename = None
        self.pdf_status_label = None

    def create_submission_form(self):
        """Create publication submission form"""
        for widget in self.parent_container.winfo_children():
            widget.destroy()

        header_frame = tk.Frame(self.parent_container, bg="#305CDE")
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
            text="Submit Publication",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#305CDE"
        ).pack(side=tk.LEFT, expand=True)

        pdf_button = tk.Button(
            header_frame,
            text="📄 Upload PDF",
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

        self.pdf_status_label = tk.Label(
            header_frame,
            text="No PDF uploaded",
            font=("Arial", 9),
            fg="#FFD54F",
            bg="#305CDE"
        )
        self.pdf_status_label.pack(side=tk.RIGHT, padx=(0, 10))

        form_container = tk.Frame(self.parent_container, bg="#305CDE")
        form_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        self.form_entries = {}

        # Publication Information (in requested order)
        fields = [
            ("Journal Name:", "journal_name", 1),
            ("Publication Year:", "publication_year", 1),
            ("Volume:", "volume", 1),
            ("Page Range:", "page_range", 1),
            ("Title:", "title", 2),
            ("Authors:", "authors", 2),
            ("Abstract:", "abstract", 6),
        ]

        for label_text, field_name, height in fields:
            label = tk.Label(form_container, text=label_text, font=("Arial", 11, "bold"),
                             fg="white", bg="#305CDE", anchor="w")
            label.pack(anchor="w", pady=(10, 5))

            if height == 1:
                entry = tk.Entry(form_container, font=("Arial", 10), bg="white",
                                 fg="black", relief=tk.FLAT, bd=2)
                entry.pack(fill=tk.X, ipady=6)
                self.form_entries[field_name] = entry
            else:
                text_widget = tk.Text(form_container, font=("Arial", 10), bg="white",
                                      fg="black", relief=tk.FLAT, bd=2, height=height, wrap=tk.WORD)
                text_widget.pack(fill=tk.X)
                self.form_entries[field_name] = text_widget

        # Buttons
        button_frame = tk.Frame(form_container, bg="#305CDE")
        button_frame.pack(pady=(20, 10))

        save_button = tk.Button(
            button_frame,
            text="Save",
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
        save_button.pack(side=tk.LEFT, padx=10)

        clear_button = tk.Button(
            button_frame,
            text="Clear",
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
        clear_button.pack(side=tk.LEFT, padx=10)

    def show_edit_form(self, edit_container, pub, update_callback, navigate_back_callback):
        """Show edit form populated with publication data"""
        for widget in edit_container.winfo_children():
            widget.destroy()

        header_frame = tk.Frame(edit_container, bg="#305CDE")
        header_frame.pack(fill=tk.X, pady=(10, 10))

        # Back button
        if self.back_button_image:
            back_btn = tk.Button(
                header_frame,
                image=self.back_button_image,
                command=navigate_back_callback,
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
                command=navigate_back_callback,
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

        form_container = tk.Frame(edit_container, bg="#305CDE")
        form_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        edit_entries = {}

        fields = [
            ("Journal Name:", "journal_name", 1),
            ("Publication Year:", "publication_year", 1),
            ("Volume:", "volume", 1),
            ("Page Range:", "page_range", 1),
            ("Title:", "title", 2),
            ("Authors:", "authors", 2),
            ("Abstract:", "abstract", 6),
        ]

        for label_text, field_name, height in fields:
            label = tk.Label(form_container, text=label_text, font=("Arial", 11, "bold"),
                             fg="white", bg="#305CDE", anchor="w")
            label.pack(anchor="w", pady=(10, 5))

            if height == 1:
                entry = tk.Entry(form_container, font=("Arial", 10), bg="white",
                                 fg="black", relief=tk.FLAT, bd=2)
                entry.pack(fill=tk.X, ipady=6)
                edit_entries[field_name] = entry
            else:
                text_widget = tk.Text(form_container, font=("Arial", 10), bg="white",
                                      fg="black", relief=tk.FLAT, bd=2, height=height, wrap=tk.WORD)
                text_widget.pack(fill=tk.X)
                edit_entries[field_name] = text_widget

        # Populate with existing data
        if pub.get('journal_name'):
            edit_entries['journal_name'].insert(0, str(pub['journal_name']))
        if pub.get('publication_year'):
            edit_entries['publication_year'].insert(0, str(pub['publication_year']))
        if pub.get('volume'):
            edit_entries['volume'].insert(0, str(pub['volume']))
        if pub.get('page_range'):
            edit_entries['page_range'].insert(0, str(pub['page_range']))
        if pub.get('title'):
            edit_entries['title'].insert("1.0", str(pub['title']))
        if pub.get('authors'):
            edit_entries['authors'].insert("1.0", str(pub['authors']))
        if pub.get('abstract'):
            edit_entries['abstract'].insert("1.0", str(pub['abstract']))

        # Buttons
        button_frame = tk.Frame(form_container, bg="#305CDE")
        button_frame.pack(pady=20)

        save_button = tk.Button(
            button_frame,
            text="Save Changes",
            command=lambda: update_callback(pub['id'], edit_entries),
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

        cancel_button = tk.Button(
            button_frame,
            text="Cancel",
            command=navigate_back_callback,
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
                if self.pdf_status_label:
                    self.pdf_status_label.config(
                        text=f"PDF: {self.current_pdf_filename}",
                        fg="#4CAF50"
                    )
                messagebox.showinfo("Success", f"PDF '{self.current_pdf_filename}' uploaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload PDF: {str(e)}")

    def save_publication(self):
        """Handle publication submission with better error handling"""
        try:
            # Get form data - handle both Entry and Text widgets
            journal_name = self.form_entries['journal_name'].get().strip()
            publication_year = self.form_entries['publication_year'].get().strip()
            volume = self.form_entries['volume'].get().strip()
            page_range = self.form_entries['page_range'].get().strip()

            # Text widgets use get("1.0", tk.END)
            title = self.form_entries['title'].get("1.0", tk.END).strip()
            authors = self.form_entries['authors'].get("1.0", tk.END).strip()
            abstract = self.form_entries['abstract'].get("1.0", tk.END).strip()

            # Check if at least one field is filled
            if not any([journal_name, publication_year, volume, page_range, title,
                        authors, abstract, self.current_pdf_data]):
                messagebox.showwarning("Empty Form", "Please fill in at least one field or upload a PDF file.")
                return

            # Check if database is available
            if not self.db:
                messagebox.showerror("Error", "Database not available")
                return

            # Save to database
            pub = self.db.add_publication(
                journal_name=journal_name if journal_name else None,
                publication_year=publication_year if publication_year else None,
                volume=volume if volume else None,
                page_range=page_range if page_range else None,
                title=title if title else None,
                authors=authors if authors else None,
                abstract=abstract if abstract else None,
                pdf_data=self.current_pdf_data,
                pdf_filename=self.current_pdf_filename
            )

            # Check if publication was saved successfully
            if pub is None:
                messagebox.showerror("Error", "Failed to save publication. Database returned None.")
                return

            if not isinstance(pub, dict) or 'id' not in pub:
                messagebox.showerror("Error", "Failed to save publication. Invalid response from database.")
                return

            # Success message
            messagebox.showinfo(
                "Success",
                f"Publication submitted successfully!\n\n"
                f"ID: {pub.get('id', 'Unknown')}\n"
                f"Title: {title if title else 'Not provided'}"
            )

            self.clear_form()
            self.navigate_to("main_view")

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error saving publication: {error_details}")
            messagebox.showerror("Error", f"Failed to save publication:\n{str(e)}\n\nCheck console for details.")

    def update_publication_data(self, pub_id, entries):
        """Update publication in database"""
        try:
            journal_name = entries['journal_name'].get().strip()
            publication_year = entries['publication_year'].get().strip()
            volume = entries['volume'].get().strip()
            page_range = entries['page_range'].get().strip()
            title = entries['title'].get("1.0", tk.END).strip()
            authors = entries['authors'].get("1.0", tk.END).strip()
            abstract = entries['abstract'].get("1.0", tk.END).strip()

            if not self.db:
                messagebox.showerror("Error", "Database not available")
                return False

            success = self.db.update_publication(
                pub_id=pub_id,
                journal_name=journal_name if journal_name else None,
                publication_year=publication_year if publication_year else None,
                volume=volume if volume else None,
                page_range=page_range if page_range else None,
                title=title if title else None,
                authors=authors if authors else None,
                abstract=abstract if abstract else None
            )

            if success:
                messagebox.showinfo("Success", "Publication updated successfully!")
                return True
            else:
                messagebox.showerror("Error", "Failed to update publication")
                return False

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error updating publication: {error_details}")
            messagebox.showerror("Error", f"Failed to update publication:\n{str(e)}")
            return False

    def clear_form(self):
        """Clear all form fields"""
        for field_name, widget in self.form_entries.items():
            if isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            else:
                widget.delete(0, tk.END)

        self.current_pdf_data = None
        self.current_pdf_filename = None
        if self.pdf_status_label:
            self.pdf_status_label.config(text="No PDF uploaded", fg="#FFD54F")