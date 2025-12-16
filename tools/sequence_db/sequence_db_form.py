# sequence_db_form.py
"""
Sequence Database Form GUI Module
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import os


class SequenceFormGUI:
    def __init__(self, parent_container, db, back_button_image, navigate_back_callback, navigate_to_callback):
        """Initialize the form GUI component"""
        self.parent_container = parent_container
        self.db = db
        self.back_button_image = back_button_image  # Store the image reference
        self.navigate_back = navigate_back_callback
        self.navigate_to = navigate_to_callback

        self.form_entries = {}
        self.current_pdf_data = None
        self.current_pdf_filename = None
        self.pdf_status_label = None

        # Debug output
        print(f"[SequenceFormGUI] Back button image received: {self.back_button_image}")
        print(f"[SequenceFormGUI] Back button image type: {type(self.back_button_image)}")

    def create_submission_form(self):
        """Create sequence submission form"""
        for widget in self.parent_container.winfo_children():
            widget.destroy()

        header_frame = tk.Frame(self.parent_container, bg="#305CDE")
        header_frame.pack(fill=tk.X, pady=(10, 10))

        # Debug: Check if image is available
        print(f"[create_submission_form] Creating back button, image available: {self.back_button_image is not None}")

        # Back button - use image if available, otherwise text
        if self.back_button_image:
            print("[create_submission_form] Using IMAGE button")
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
            # CRITICAL: Keep a reference to prevent garbage collection
            back_btn.image = self.back_button_image
        else:
            print("[create_submission_form] Using TEXT button (no image)")
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
            text="Submit Sequence",
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

        # Personal Information
        user_info_label = tk.Label(
            form_container,
            text="Personal Information",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#305CDE",
            anchor="w"
        )
        user_info_label.pack(anchor="w", pady=(10, 5))

        user_fields = [
            ("Name (user):", "user_name"),
            ("Affiliation:", "user_affiliation"),
            ("Mobile phone number:", "user_phone"),
        ]

        for label_text, field_name in user_fields:
            label = tk.Label(form_container, text=label_text, font=("Arial", 11, "bold"),
                             fg="white", bg="#305CDE", anchor="w")
            label.pack(anchor="w", pady=(10, 5))

            entry = tk.Entry(form_container, font=("Arial", 10), bg="#FFFF99",
                             fg="black", relief=tk.FLAT, bd=2)
            entry.pack(fill=tk.X, ipady=6)
            self.form_entries[field_name] = entry

        separator = tk.Frame(form_container, bg="white", height=2)
        separator.pack(fill=tk.X, pady=20)

        # Sequence Information
        seq_info_label = tk.Label(
            form_container,
            text="Sequence Information",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#305CDE",
            anchor="w"
        )
        seq_info_label.pack(anchor="w", pady=(10, 5))

        fields = [
            ("Gene Name:", "gene_name", 1),
            ("Protein Name:", "protein_name", 1),
            ("Organism Name:", "organism_name", 1),
            ("Accession Number:", "accession_number", 1),
            ("Sequence:", "sequence", 6),
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
            command=self.save_sequence,
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

    def show_edit_form(self, edit_container, seq, update_callback, navigate_back_callback):
        """Show edit form populated with sequence data"""
        for widget in edit_container.winfo_children():
            widget.destroy()

        header_frame = tk.Frame(edit_container, bg="#305CDE")
        header_frame.pack(fill=tk.X, pady=(10, 10))

        # Debug: Check if image is available
        print(f"[show_edit_form] Creating back button, image available: {self.back_button_image is not None}")

        # Back button - use image if available, otherwise text
        if self.back_button_image:
            print("[show_edit_form] Using IMAGE button")
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
            # CRITICAL: Keep a reference to prevent garbage collection
            back_btn.image = self.back_button_image
        else:
            print("[show_edit_form] Using TEXT button (no image)")
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
            text="Edit Sequence",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#305CDE"
        ).pack(side=tk.LEFT, expand=True)

        form_container = tk.Frame(edit_container, bg="#305CDE")
        form_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        edit_entries = {}

        # Personal Information
        user_info_label = tk.Label(form_container, text="Personal Information",
                                   font=("Arial", 12, "bold"), fg="white", bg="#305CDE", anchor="w")
        user_info_label.pack(anchor="w", pady=(10, 5))

        user_fields = [
            ("Name (user):", "user_name"),
            ("Affiliation:", "user_affiliation"),
            ("Mobile phone number:", "user_phone"),
        ]

        for label_text, field_name in user_fields:
            label = tk.Label(form_container, text=label_text, font=("Arial", 11, "bold"),
                             fg="white", bg="#305CDE", anchor="w")
            label.pack(anchor="w", pady=(10, 5))

            entry = tk.Entry(form_container, font=("Arial", 10), bg="#FFFF99",
                             fg="black", relief=tk.FLAT, bd=2)
            entry.pack(fill=tk.X, ipady=6)
            edit_entries[field_name] = entry

        separator = tk.Frame(form_container, bg="white", height=2)
        separator.pack(fill=tk.X, pady=20)

        # Sequence Information
        seq_info_label = tk.Label(form_container, text="Sequence Information",
                                  font=("Arial", 12, "bold"), fg="white", bg="#305CDE", anchor="w")
        seq_info_label.pack(anchor="w", pady=(10, 5))

        fields = [
            ("Gene Name:", "gene_name", 1),
            ("Protein Name:", "protein_name", 1),
            ("Organism Name:", "organism_name", 1),
            ("Accession Number:", "accession_number", 1),
            ("Sequence:", "sequence", 6),
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
        if seq.get('user_name'):
            edit_entries['user_name'].insert(0, str(seq['user_name']))
        if seq.get('user_affiliation'):
            edit_entries['user_affiliation'].insert(0, str(seq['user_affiliation']))
        if seq.get('user_phone'):
            edit_entries['user_phone'].insert(0, str(seq['user_phone']))

        if seq.get('gene_name'):
            edit_entries['gene_name'].insert(0, str(seq['gene_name']))
        if seq.get('protein_name'):
            edit_entries['protein_name'].insert(0, str(seq['protein_name']))
        if seq.get('organism_name'):
            edit_entries['organism_name'].insert(0, str(seq['organism_name']))
        if seq.get('accession_number'):
            edit_entries['accession_number'].insert(0, str(seq['accession_number']))
        if seq.get('sequence'):
            edit_entries['sequence'].insert("1.0", str(seq['sequence']))

        # Buttons
        button_frame = tk.Frame(form_container, bg="#305CDE")
        button_frame.pack(pady=20)

        save_button = tk.Button(
            button_frame,
            text="Save Changes",
            command=lambda: update_callback(seq['id'], edit_entries),
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

    def save_sequence(self):
        """Handle sequence submission"""
        user_name = self.form_entries['user_name'].get().strip()
        user_affiliation = self.form_entries['user_affiliation'].get().strip()
        user_phone = self.form_entries['user_phone'].get().strip()

        gene_name = self.form_entries['gene_name'].get().strip()
        protein_name = self.form_entries['protein_name'].get().strip()
        organism_name = self.form_entries['organism_name'].get().strip()
        accession_number = self.form_entries['accession_number'].get().strip()
        sequence = self.form_entries['sequence'].get("1.0", tk.END).strip()

        if not any([user_name, user_affiliation, user_phone, gene_name, protein_name,
                    organism_name, accession_number, sequence, self.current_pdf_data]):
            messagebox.showwarning("Empty Form", "Please fill in at least one field or upload a PDF file.")
            return

        if self.db:
            try:
                seq = self.db.add_sequence(
                    user_name=user_name if user_name else None,
                    user_affiliation=user_affiliation if user_affiliation else None,
                    user_phone=user_phone if user_phone else None,
                    gene_name=gene_name if gene_name else None,
                    protein_name=protein_name if protein_name else None,
                    organism_name=organism_name if organism_name else None,
                    accession_number=accession_number if accession_number else None,
                    sequence=sequence if sequence else None,
                    pdf_data=self.current_pdf_data,
                    pdf_filename=self.current_pdf_filename
                )
                messagebox.showinfo(
                    "Success",
                    f"Sequence submitted successfully!\n\nID: {seq['id']}\nGene: {gene_name if gene_name else 'Not provided'}"
                )
                self.clear_form()
                self.navigate_to("main_view")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save sequence:\n{str(e)}")

    def update_sequence_data(self, seq_id, entries):
        """Update sequence in database"""
        user_name = entries['user_name'].get().strip()
        user_affiliation = entries['user_affiliation'].get().strip()
        user_phone = entries['user_phone'].get().strip()

        gene_name = entries['gene_name'].get().strip()
        protein_name = entries['protein_name'].get().strip()
        organism_name = entries['organism_name'].get().strip()
        accession_number = entries['accession_number'].get().strip()
        sequence = entries['sequence'].get("1.0", tk.END).strip()

        if self.db:
            try:
                success = self.db.update_sequence(
                    seq_id=seq_id,
                    user_name=user_name if user_name else None,
                    user_affiliation=user_affiliation if user_affiliation else None,
                    user_phone=user_phone if user_phone else None,
                    gene_name=gene_name if gene_name else None,
                    protein_name=protein_name if protein_name else None,
                    organism_name=organism_name if organism_name else None,
                    accession_number=accession_number if accession_number else None,
                    sequence=sequence if sequence else None
                )
                if success:
                    messagebox.showinfo("Success", "Sequence updated successfully!")
                    return True
                else:
                    messagebox.showerror("Error", "Failed to update sequence")
                    return False
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update sequence:\n{str(e)}")
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