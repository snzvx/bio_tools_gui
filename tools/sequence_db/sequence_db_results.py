# sequence_db_results.py
"""
Sequence Database Results GUI Module
"""

import tkinter as tk
from tkinter import messagebox, filedialog


class SequenceResultsGUI:
    def __init__(self, parent_container, db, navigate_to_callback):
        """Initialize the results GUI component"""
        self.parent_container = parent_container
        self.db = db
        self.navigate_to = navigate_to_callback

        self.search_entry = None
        self.results_label_ref = None
        self.results_frame_ref = None
        self.results_container = None

    def perform_search(self):
        """Perform search based on query"""
        if not self.search_entry:
            messagebox.showerror("Error", "Search interface not initialized")
            return

        query = self.search_entry.get().strip()

        if not query:
            messagebox.showwarning("Empty Search", "Please enter a search term")
            return

        if self.db:
            results = self.db.search_sequences(query)
            self.display_results(results, query)
        else:
            messagebox.showerror("Error", "Database not available")

    def show_all_sequences(self):
        """Show all sequences"""
        if self.db:
            results = self.db.get_all_sequences()
            self.display_results(results, "All Sequences")
        else:
            messagebox.showerror("Error", "Database not available")

    def format_sequence(self, seq):
        """Format sequence for display"""
        parts = []

        if seq.get('gene_name'):
            parts.append(str(seq['gene_name']))
        if seq.get('protein_name'):
            parts.append(str(seq['protein_name']))
        if seq.get('organism_name'):
            parts.append(str(seq['organism_name']))
        if seq.get('accession_number'):
            parts.append(str(seq['accession_number']))

        if parts:
            return " - ".join(parts)
        else:
            return f"Sequence #{seq['id']} (No details provided)"

    def display_results(self, results, query):
        """Display search results"""
        for widget in self.results_container.winfo_children():
            widget.destroy()

        self.results_label_ref.pack(anchor="w", padx=60, pady=(10, 5))
        self.results_frame_ref.pack(fill=tk.BOTH, expand=True, padx=60, pady=(0, 20))

        if not results:
            no_results_label = tk.Label(
                self.results_container,
                text=f"No results found for: '{query}'",
                font=("Arial", 10),
                fg="white",
                bg="#305CDE",
                padx=10,
                pady=10,
                anchor="w"
            )
            no_results_label.pack(anchor="w", fill=tk.X)
        else:
            header_label = tk.Label(
                self.results_container,
                text=f"Found {len(results)} result(s) for '{query}':\n",
                font=("Arial", 10, "bold"),
                fg="white",
                bg="#305CDE",
                padx=10,
                pady=5,
                anchor="w"
            )
            header_label.pack(anchor="w", fill=tk.X)

            for idx, seq in enumerate(results, 1):
                formatted_text = self.format_sequence(seq)

                result_frame = tk.Frame(self.results_container, bg="#305CDE", pady=5)
                result_frame.pack(anchor="w", fill=tk.X, padx=10)

                number_label = tk.Label(
                    result_frame,
                    text=f"{idx}.",
                    font=("Arial", 9, "bold"),
                    fg="white",
                    bg="#305CDE"
                )
                number_label.pack(side=tk.LEFT, padx=(0, 5))

                result_label = tk.Label(
                    result_frame,
                    text=formatted_text,
                    font=("Arial", 9, "underline"),
                    fg="#4CAF50",
                    bg="#305CDE",
                    cursor="hand2",
                    wraplength=400
                )
                result_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
                result_label.bind("<Button-1>", lambda e, s=seq: self.navigate_to("detail", s))
                result_label.bind("<Enter>", lambda e, lbl=result_label: lbl.config(fg="#66BB6A"))
                result_label.bind("<Leave>", lambda e, lbl=result_label: lbl.config(fg="#4CAF50"))

                button_frame = tk.Frame(result_frame, bg="#305CDE")
                button_frame.pack(side=tk.RIGHT, padx=(10, 0))

                if seq.get('pdf_data') is not None:
                    pdf_button = tk.Button(
                        button_frame,
                        text="📥 PDF",
                        command=lambda s=seq: self.download_pdf(s),
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

                edit_button = tk.Button(
                    button_frame,
                    text="Edit",
                    command=lambda s=seq: self.navigate_to("edit", s),
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

                delete_button = tk.Button(
                    button_frame,
                    text="Delete",
                    command=lambda s=seq: self.delete_with_confirm(s),
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

                if idx < len(results):
                    separator = tk.Frame(self.results_container, bg="#1E3A8A", height=1)
                    separator.pack(fill=tk.X, padx=20, pady=3)

    def display_sequence_details(self, detail_container, seq, navigate_to_callback, delete_callback):
        """Display detailed view of a sequence"""
        content_frame = tk.Frame(detail_container, bg="#305CDE")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # Title
        title_text = self.format_sequence(seq)
        title_label = tk.Label(
            content_frame,
            text=title_text,
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#305CDE",
            wraplength=700,
            justify=tk.LEFT
        )
        title_label.pack(fill=tk.X, padx=20, pady=(10, 20))

        separator = tk.Frame(content_frame, bg="white", height=2)
        separator.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Details
        details = [
            ("User Name:", seq.get('user_name', 'Not provided') or "Not provided"),
            ("Affiliation:", seq.get('user_affiliation', 'Not provided') or "Not provided"),
            ("Mobile Phone:", seq.get('user_phone', 'Not provided') or "Not provided"),
            ("", ""),
            ("Gene Name:", seq.get('gene_name', 'Not provided') or "Not provided"),
            ("Protein Name:", seq.get('protein_name', 'Not provided') or "Not provided"),
            ("Organism Name:", seq.get('organism_name', 'Not provided') or "Not provided"),
            ("Accession Number:", seq.get('accession_number', 'Not provided') or "Not provided"),
            ("Sequence:", seq.get('sequence', 'Not provided') or "Not provided"),
            ("PDF File:", seq.get('pdf_filename', 'No PDF uploaded') if seq.get('pdf_filename') else "No PDF uploaded"),
        ]

        for label_text, value in details:
            if not label_text and not value:
                tk.Frame(content_frame, bg="#305CDE", height=10).pack(fill=tk.X, padx=20)
                continue

            detail_row = tk.Frame(content_frame, bg="#305CDE")
            detail_row.pack(fill=tk.X, padx=20, pady=8)

            if label_text in ["User Name:", "Affiliation:", "Mobile Phone:"]:
                label_color = "#FFD700"
            else:
                label_color = "#4CAF50"

            tk.Label(
                detail_row,
                text=label_text,
                font=("Arial", 11, "bold"),
                fg=label_color,
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

        # Action buttons
        button_frame = tk.Frame(content_frame, bg="#305CDE")
        button_frame.pack(pady=30)

        if seq.get('pdf_data') is not None:
            pdf_button = tk.Button(
                button_frame,
                text="📥 Download PDF",
                command=lambda s=seq: self.download_pdf(s),
                bg="#FF9800",
                fg="white",
                font=("Arial", 10, "bold"),
                cursor="hand2",
                relief=tk.FLAT,
                bd=0,
                padx=15,
                pady=10
            )
            pdf_button.pack(side=tk.LEFT, padx=10)

        tk.Button(
            button_frame,
            text="Edit",
            command=lambda: navigate_to_callback("edit", seq),
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
            command=lambda: delete_callback(seq),
            bg="#F44336",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            padx=25,
            pady=10
        ).pack(side=tk.LEFT, padx=10)

    def download_pdf(self, seq):
        """Download PDF file from database"""
        if self.db:
            save_path = filedialog.asksaveasfilename(
                title="Save PDF As",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=seq.get('pdf_filename', f"sequence_{seq['id']}.pdf")
            )

            if save_path:
                try:
                    exported_path = self.db.export_pdf(seq['id'], save_path)
                    if exported_path:
                        messagebox.showinfo("Success", f"PDF downloaded successfully!\nSaved to: {exported_path}")
                    else:
                        messagebox.showerror("Error", "Failed to download PDF. File may not exist.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to download PDF: {str(e)}")

    def delete_with_confirm(self, seq):
        """Delete sequence with confirmation"""
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this sequence?\n\n"
            f"Gene: {seq['gene_name'] if seq['gene_name'] else 'No gene'}\n"
            f"Accession: {seq['accession_number'] if seq['accession_number'] else 'Not provided'}"
        )

        if result and self.db:
            if self.db.delete_sequence(seq['id']):
                messagebox.showinfo("Success", "Sequence deleted successfully!")
                self.show_all_sequences()
            else:
                messagebox.showerror("Error", "Failed to delete sequence.")