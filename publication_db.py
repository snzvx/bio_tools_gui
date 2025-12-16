# publication_db.py
"""
Publication Database Module
Handles SQLite database operations for publication management
FIXED: Better error handling and debugging
"""

import sqlite3
import os


class PublicationDatabase:
    def __init__(self, db_path="publications.db"):
        """
        Initialize publication database

        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        print(f"Initializing database at: {os.path.abspath(db_path)}")
        self.init_database()

    def init_database(self):
        """Initialize database with schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS publications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    journal_name TEXT,
                    publication_year TEXT,
                    volume TEXT,
                    page_range TEXT,
                    title TEXT,
                    authors TEXT,
                    abstract TEXT,
                    pdf_data BLOB,
                    pdf_filename TEXT
                )
            ''')

            # Create index for search performance
            try:
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_pub_search 
                    ON publications(title, authors, journal_name)
                ''')
            except sqlite3.OperationalError as e:
                print(f"Note: Index already exists or couldn't be created: {e}")

            conn.commit()
            conn.close()
            print("✓ Publication database schema initialized successfully")
        except Exception as e:
            print(f"✗ Error initializing database: {e}")
            import traceback
            traceback.print_exc()

    def add_publication(self, journal_name=None, publication_year=None, volume=None,
                        page_range=None, title=None, authors=None, abstract=None,
                        pdf_data=None, pdf_filename=None):
        """Add a new publication to the database"""
        print("\n=== Adding Publication ===")
        print(f"Journal: {journal_name}")
        print(f"Year: {publication_year}")
        print(f"Volume: {volume}")
        print(f"Page Range: {page_range}")
        print(f"Title: {title}")
        print(f"Authors: {authors}")
        print(f"Abstract: {abstract[:50] + '...' if abstract and len(abstract) > 50 else abstract}")
        print(f"PDF: {pdf_filename if pdf_filename else 'None'}")

        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO publications 
                (journal_name, publication_year, volume, page_range, title, 
                 authors, abstract, pdf_data, pdf_filename)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (journal_name, publication_year, volume, page_range, title,
                  authors, abstract, pdf_data, pdf_filename))

            publication_id = cursor.lastrowid
            conn.commit()

            print(f"✓ Publication saved with ID: {publication_id}")

            # Retrieve the saved publication
            publication = self.get_publication(publication_id)

            if publication is None:
                print("✗ Warning: Publication was saved but couldn't be retrieved")
                # Return a basic dict with the ID at least
                return {
                    'id': publication_id,
                    'journal_name': journal_name,
                    'publication_year': publication_year,
                    'volume': volume,
                    'page_range': page_range,
                    'title': title,
                    'authors': authors,
                    'abstract': abstract,
                    'pdf_data': pdf_data,
                    'pdf_filename': pdf_filename
                }

            return publication

        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            if conn:
                conn.rollback()
            import traceback
            traceback.print_exc()
            return None
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            if conn:
                conn.rollback()
            import traceback
            traceback.print_exc()
            return None
        finally:
            if conn:
                conn.close()

    def get_publication(self, pub_id):
        """Get a specific publication by ID"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM publications WHERE id = ?', (pub_id,))
            row = cursor.fetchone()

            if row:
                result = self._row_to_dict(cursor, row)
                print(f"✓ Retrieved publication ID {pub_id}")
                return result
            else:
                print(f"✗ No publication found with ID {pub_id}")
                return None

        except sqlite3.Error as e:
            print(f"✗ Database error retrieving publication: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            if conn:
                conn.close()

    def get_all_publications(self):
        """Get all publications from database"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM publications ORDER BY id DESC')
            rows = cursor.fetchall()
            return [self._row_to_dict(cursor, row) for row in rows]

        except sqlite3.Error as e:
            print(f"✗ Database error: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            if conn:
                conn.close()

    def search_publications(self, query):
        """Search publications across all text fields"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            search_term = f"%{query}%"
            # Search across multiple fields
            cursor.execute('''
                SELECT * FROM publications 
                WHERE journal_name LIKE ? 
                   OR publication_year LIKE ?
                   OR volume LIKE ?
                   OR page_range LIKE ?
                   OR title LIKE ?
                   OR authors LIKE ?
                   OR abstract LIKE ?
                   OR pdf_filename LIKE ?
                ORDER BY id DESC
            ''', (search_term, search_term, search_term, search_term,
                  search_term, search_term, search_term, search_term))

            rows = cursor.fetchall()
            results = [self._row_to_dict(cursor, row) for row in rows]
            print(f"✓ Search for '{query}' found {len(results)} results")
            return results

        except sqlite3.Error as e:
            print(f"✗ Database error during search: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            if conn:
                conn.close()

    def update_publication(self, pub_id, journal_name=None, publication_year=None,
                           volume=None, page_range=None, title=None, authors=None,
                           abstract=None):
        """Update an existing publication"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE publications 
                SET journal_name = ?, publication_year = ?, volume = ?,
                    page_range = ?, title = ?, authors = ?, abstract = ?
                WHERE id = ?
            ''', (journal_name, publication_year, volume, page_range, title,
                  authors, abstract, pub_id))

            success = cursor.rowcount > 0
            conn.commit()

            if success:
                print(f"✓ Publication {pub_id} updated successfully")
            else:
                print(f"✗ No publication found with ID {pub_id}")

            return success

        except sqlite3.Error as e:
            print(f"✗ Database error updating publication: {e}")
            if conn:
                conn.rollback()
            import traceback
            traceback.print_exc()
            return False
        finally:
            if conn:
                conn.close()

    def delete_publication(self, pub_id):
        """Delete a publication by ID"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('DELETE FROM publications WHERE id = ?', (pub_id,))
            success = cursor.rowcount > 0
            conn.commit()

            if success:
                print(f"✓ Publication {pub_id} deleted successfully")
            else:
                print(f"✗ No publication found with ID {pub_id}")

            return success

        except sqlite3.Error as e:
            print(f"✗ Database error deleting publication: {e}")
            if conn:
                conn.rollback()
            import traceback
            traceback.print_exc()
            return False
        finally:
            if conn:
                conn.close()

    def _row_to_dict(self, cursor, row):
        """Convert SQLite row to dictionary"""
        try:
            columns = [description[0] for description in cursor.description]
            result = {}
            for i, column in enumerate(columns):
                result[column] = row[i]
            return result
        except Exception as e:
            print(f"✗ Error converting row to dict: {e}")
            import traceback
            traceback.print_exc()
            return None

    def export_pdf(self, pub_id, save_path=None):
        """Export PDF file from database"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT pdf_data, pdf_filename FROM publications WHERE id = ?', (pub_id,))
            result = cursor.fetchone()

            if result and result[0] is not None:
                pdf_data, pdf_filename = result[0], result[1]

                if save_path is None:
                    downloads_dir = "downloads"
                    os.makedirs(downloads_dir, exist_ok=True)
                    save_path = os.path.join(downloads_dir, pdf_filename)

                with open(save_path, 'wb') as file:
                    file.write(pdf_data)

                print(f"✓ PDF exported to: {save_path}")
                return save_path
            else:
                print(f"✗ No PDF data found for publication {pub_id}")
                return None

        except Exception as e:
            print(f"✗ Error exporting PDF: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            if conn:
                conn.close()


# Test the database if run directly
if __name__ == "__main__":
    print("Testing Publication Database...")
    db = PublicationDatabase("test_publications.db")

    # Test add
    pub = db.add_publication(
        journal_name="Nature",
        publication_year="1953",
        volume="171",
        page_range="737-738",
        title="Molecular Structure of Nucleic Acids",
        authors="Watson, J.D., Crick, F.H.C.",
        abstract="We wish to suggest a structure for DNA..."
    )

    if pub:
        print(f"\n✓ Test passed! Publication created with ID: {pub['id']}")
    else:
        print("\n✗ Test failed! Publication was not created")