# publication_db_pdf_viewer.py
"""
Publication Database PDF Viewer Module
MODIFIED: Uses main application's scrollbar instead of internal scrollbar
"""

import tkinter as tk
from tkinter import messagebox
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import io


class PDFViewerGUI:
    def __init__(self, parent_container, back_button_image, navigate_back_callback):
        """
        Initialize PDF viewer component

        Args:
            parent_container: The container frame for PDF viewer
            back_button_image: Image for back button
            navigate_back_callback: Function to navigate back
        """
        self.parent_container = parent_container
        self.back_button_image = back_button_image
        self.navigate_back = navigate_back_callback

        self.current_pdf_doc = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0
        self.pdf_images = []  # Store PhotoImage references
        self.pdf_image_label = None  # Store reference to the label displaying PDF

    def show_pdf(self, pdf_data, pdf_filename):
        """
        Display PDF from binary data

        Args:
            pdf_data: Binary PDF data from database
            pdf_filename: Name of the PDF file
        """
        # Clear existing content
        for widget in self.parent_container.winfo_children():
            widget.destroy()

        if not pdf_data:
            messagebox.showerror("Error", "No PDF data available")
            self.navigate_back()
            return

        try:
            # Open PDF from memory
            self.current_pdf_doc = fitz.open(stream=pdf_data, filetype="pdf")
            self.total_pages = len(self.current_pdf_doc)
            self.current_page = 0

            # Create PDF viewer UI
            self.create_pdf_viewer_ui(pdf_filename)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF: {str(e)}")
            self.navigate_back()

    def create_pdf_viewer_ui(self, pdf_filename):
        """Create the PDF viewer interface WITHOUT internal scrollbar"""

        # Header with back button and controls
        header_frame = tk.Frame(self.parent_container, bg="#305CDE")
        header_frame.pack(fill=tk.X, pady=(10, 10))

        # Back button
        if self.back_button_image:
            back_btn = tk.Button(
                header_frame,
                image=self.back_button_image,
                command=self.close_pdf,
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
                command=self.close_pdf,
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

        # PDF filename
        tk.Label(
            header_frame,
            text=f"📄 {pdf_filename}",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#305CDE"
        ).pack(side=tk.LEFT, padx=20)

        # Page info
        self.page_info_label = tk.Label(
            header_frame,
            text=f"Page {self.current_page + 1} of {self.total_pages}",
            font=("Arial", 11),
            fg="white",
            bg="#305CDE"
        )
        self.page_info_label.pack(side=tk.RIGHT, padx=20)

        # Control bar
        control_frame = tk.Frame(self.parent_container, bg="#1E40AF")
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Navigation buttons
        btn_frame = tk.Frame(control_frame, bg="#1E40AF")
        btn_frame.pack(pady=10)

        # First page
        tk.Button(
            btn_frame,
            text="⏮ First",
            command=self.first_page,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

        # Previous page
        tk.Button(
            btn_frame,
            text="◀ Previous",
            command=self.previous_page,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

        # Next page
        tk.Button(
            btn_frame,
            text="Next ▶",
            command=self.next_page,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

        # Last page
        tk.Button(
            btn_frame,
            text="Last ⏭",
            command=self.last_page,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

        # Zoom controls
        zoom_frame = tk.Frame(control_frame, bg="#1E40AF")
        zoom_frame.pack(pady=5)

        tk.Button(
            zoom_frame,
            text="🔍- Zoom Out",
            command=self.zoom_out,
            bg="#2196F3",
            fg="white",
            font=("Arial", 9, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

        self.zoom_label = tk.Label(
            zoom_frame,
            text=f"{int(self.zoom_level * 100)}%",
            font=("Arial", 10, "bold"),
            fg="white",
            bg="#1E40AF",
            width=6
        )
        self.zoom_label.pack(side=tk.LEFT, padx=10)

        tk.Button(
            zoom_frame,
            text="🔍+ Zoom In",
            command=self.zoom_in,
            bg="#2196F3",
            fg="white",
            font=("Arial", 9, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            zoom_frame,
            text="↺ Reset",
            command=self.reset_zoom,
            bg="#FF9800",
            fg="white",
            font=("Arial", 9, "bold"),
            cursor="hand2",
            relief=tk.FLAT,
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)

        # PDF display area - REMOVED internal Canvas and Scrollbar
        # Now just a simple frame that will use the main app's scrollbar
        pdf_display_frame = tk.Frame(self.parent_container, bg="white")
        pdf_display_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Label to hold the PDF image
        self.pdf_image_label = tk.Label(
            pdf_display_frame,
            bg="white"
        )
        self.pdf_image_label.pack(pady=10)

        # Display first page
        self.display_current_page()

    def display_current_page(self):
        """Render and display the current PDF page"""
        if not self.current_pdf_doc:
            return

        try:
            # Get the current page
            page = self.current_pdf_doc[self.current_page]

            # Render page to pixmap with zoom
            mat = fitz.Matrix(self.zoom_level, self.zoom_level)
            pix = page.get_pixmap(matrix=mat)

            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)

            # Store reference to prevent garbage collection
            self.pdf_images = [photo]

            # Display image on label
            if self.pdf_image_label:
                self.pdf_image_label.config(image=photo)
                self.pdf_image_label.image = photo  # Keep a reference

            # Update page info
            self.page_info_label.config(text=f"Page {self.current_page + 1} of {self.total_pages}")

            # Update the parent container to trigger scroll region update
            self.parent_container.update_idletasks()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to display page: {str(e)}")

    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_current_page()

    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_current_page()

    def first_page(self):
        """Go to first page"""
        self.current_page = 0
        self.display_current_page()

    def last_page(self):
        """Go to last page"""
        self.current_page = self.total_pages - 1
        self.display_current_page()

    def zoom_in(self):
        """Increase zoom level"""
        if self.zoom_level < 3.0:
            self.zoom_level += 0.25
            self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
            self.display_current_page()

    def zoom_out(self):
        """Decrease zoom level"""
        if self.zoom_level > 0.5:
            self.zoom_level -= 0.25
            self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
            self.display_current_page()

    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.zoom_level = 1.0
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        self.display_current_page()

    def close_pdf(self):
        """Close PDF and navigate back"""
        if self.current_pdf_doc:
            self.current_pdf_doc.close()
            self.current_pdf_doc = None
        self.pdf_images = []
        self.navigate_back()