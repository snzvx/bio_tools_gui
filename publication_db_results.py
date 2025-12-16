# publication_db_results.py
"""
Publication Database Results GUI Module
UPDATED: Fixed white background to match blue theme
"""

import tkinter as tk
from tkinter import messagebox, filedialog


class PublicationResultsGUI:
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
            results = self.db.search_publications(query)
            self.display_results(results, query)
        else:
            messagebox.showerror("Error", "Database not available")

    def format_publication(self, pub):
        """Format publication for display - ONLY TITLE"""
        title = pub.get('title')
        if title:
            return str(title)
        else:
            return f"Publication #{pub['id']} (No title provided)"

    def display_results(self, results, query):
        """Display search results with proper blue background"""
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

            for idx, pub in enumerate(results, 1):
                formatted_text = self.format_publication(pub)

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
                result_label.bind("<Button-1>", lambda e, p=pub: self.navigate_to("detail", p))
                result_label.bind("<Enter>", lambda e, lbl=result_label: lbl.config(fg="#66BB6A"))
                result_label.bind("<Leave>", lambda e, lbl=result_label: lbl.config(fg="#4CAF50"))

                button_frame = tk.Frame(result_frame, bg="#305CDE")
                button_frame.pack(side=tk.RIGHT, padx=(10, 0))

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

                delete_button = tk.Button(
                    button_frame,
                    text="Delete",
                    command=lambda p=pub: self.delete_with_confirm(p),
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

    def display_publication_details(self, detail_container, pub, navigate_to_callback,
                                   delete_callback, back_button_image=None, view_pdf_callback=None):
        """Display detailed view of a publication with View PDF button"""
        content_frame = tk.Frame(detail_container, bg="#305CDE")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)

        # Title
        title_text = pub.get('title', 'No title provided')
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
            ("Journal Name:", pub.get('journal_name', 'Not provided') or "Not provided"),
            ("Publication Year:", pub.get('publication_year', 'Not provided') or "Not provided"),
            ("Volume:", pub.get('volume', 'Not provided') or "Not provided"),
            ("Page Range:", pub.get('page_range', 'Not provided') or "Not provided"),
            ("", ""),
            ("Title:", pub.get('title', 'Not provided') or "Not provided"),
            ("Authors:", pub.get('authors', 'Not provided') or "Not provided"),
            ("Abstract:", pub.get('abstract', 'Not provided') or "Not provided"),
            ("PDF File:", pub.get('pdf_filename', 'No PDF uploaded') if pub.get('pdf_filename') else "No PDF uploaded"),
        ]

        for label_text, value in details:
            if not label_text and not value:
                tk.Frame(content_frame, bg="#305CDE", height=10).pack(fill=tk.X, padx=20)
                continue

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

        # Action buttons
        button_frame = tk.Frame(content_frame, bg="#305CDE")
        button_frame.pack(pady=30)

        # View PDF button (NEW!)
        if pub.get('pdf_data') is not None and view_pdf_callback:
            view_pdf_button = tk.Button(
                button_frame,
                text="View PDF",
                command=lambda: view_pdf_callback(pub),
                bg="#9C27B0",  # Purple color
                fg="white",
                font=("Arial", 10, "bold"),
                cursor="hand2",
                relief=tk.FLAT,
                bd=0,
                padx=20,
                pady=10
            )
            view_pdf_button.pack(side=tk.LEFT, padx=10)

        # Download PDF button
        if pub.get('pdf_data') is not None:
            pdf_button = tk.Button(
                button_frame,
                text="Download PDF",
                command=lambda p=pub: self.download_pdf(p),
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
            command=lambda: navigate_to_callback("edit", pub),
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
            command=lambda: delete_callback(pub),
            bg="#F44336",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            bd=0,
            padx=25,
            pady=10
        ).pack(side=tk.LEFT, padx=10)

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

    def delete_with_confirm(self, pub):
        """Delete publication with confirmation"""
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this publication?\n\n"
            f"Title: {pub['title'] if pub['title'] else 'No title'}"
        )

        if result and self.db:
            if self.db.delete_publication(pub['id']):
                messagebox.showinfo("Success", "Publication deleted successfully!")
                # Clear results instead of showing all
                for widget in self.results_container.winfo_children():
                    widget.destroy()
                self.results_label_ref.pack_forget()
                self.results_frame_ref.pack_forget()
            else:
                messagebox.showerror("Error", "Failed to delete publication.")