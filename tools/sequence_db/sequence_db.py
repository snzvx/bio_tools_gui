# sequence_db.py
"""
Sequence Database Module
Handles SQLite database operations for biological sequence management
"""

import sqlite3
import os


class SequenceDatabase:
    def __init__(self, db_path="sequences.db"):
        """
        Initialize sequence database

        Args:
            db_path (str): Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database with schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sequences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT,
                user_affiliation TEXT,
                user_phone TEXT,
                gene_name TEXT,
                protein_name TEXT,
                organism_name TEXT,
                accession_number TEXT,
                sequence TEXT,
                pdf_data BLOB,
                pdf_filename TEXT
            )
        ''')

        # Check and add missing columns
        cursor.execute("PRAGMA table_info(sequences)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'user_name' not in columns:
            cursor.execute('ALTER TABLE sequences ADD COLUMN user_name TEXT')
        if 'user_affiliation' not in columns:
            cursor.execute('ALTER TABLE sequences ADD COLUMN user_affiliation TEXT')
        if 'user_phone' not in columns:
            cursor.execute('ALTER TABLE sequences ADD COLUMN user_phone TEXT')
        if 'pdf_data' not in columns:
            cursor.execute('ALTER TABLE sequences ADD COLUMN pdf_data BLOB')
            cursor.execute('ALTER TABLE sequences ADD COLUMN pdf_filename TEXT')

        # Create index for search performance
        try:
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_seq_search 
                ON sequences(gene_name, protein_name, organism_name, accession_number, user_name)
            ''')
        except sqlite3.OperationalError:
            pass

        conn.commit()
        conn.close()
        print("Sequence database schema updated successfully")

    def add_sequence(self, user_name=None, user_affiliation=None, user_phone=None,
                    gene_name=None, protein_name=None, organism_name=None,
                    accession_number=None, sequence=None, pdf_data=None, pdf_filename=None):
        """Add a new sequence to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO sequences 
                (user_name, user_affiliation, user_phone, gene_name, protein_name, 
                 organism_name, accession_number, sequence, pdf_data, pdf_filename)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_name, user_affiliation, user_phone, gene_name, protein_name,
                  organism_name, accession_number, sequence, pdf_data, pdf_filename))

            sequence_id = cursor.lastrowid
            conn.commit()

            sequence = self.get_sequence(sequence_id)
            return sequence
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_sequence(self, seq_id):
        """Get a specific sequence by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM sequences WHERE id = ?', (seq_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_dict(cursor, row)
            return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
        finally:
            conn.close()

    def get_all_sequences(self):
        """Get all sequences from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM sequences ORDER BY id DESC')
            rows = cursor.fetchall()
            return [self._row_to_dict(cursor, row) for row in rows]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()

    def search_sequences(self, query):
        """Search sequences by query string"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            search_term = f"%{query}%"
            cursor.execute('''
                SELECT * FROM sequences 
                WHERE gene_name LIKE ? OR protein_name LIKE ? OR organism_name LIKE ? 
                OR accession_number LIKE ? OR user_name LIKE ?
                ORDER BY id DESC
            ''', (search_term, search_term, search_term, search_term, search_term))

            rows = cursor.fetchall()
            return [self._row_to_dict(cursor, row) for row in rows]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []
        finally:
            conn.close()

    def update_sequence(self, seq_id, user_name=None, user_affiliation=None, user_phone=None,
                       gene_name=None, protein_name=None, organism_name=None,
                       accession_number=None, sequence=None):
        """Update an existing sequence"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                UPDATE sequences 
                SET user_name = ?, user_affiliation = ?, user_phone = ?,
                    gene_name = ?, protein_name = ?, organism_name = ?,
                    accession_number = ?, sequence = ?
                WHERE id = ?
            ''', (user_name, user_affiliation, user_phone, gene_name, protein_name,
                  organism_name, accession_number, sequence, seq_id))

            success = cursor.rowcount > 0
            conn.commit()
            return success
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete_sequence(self, seq_id):
        """Delete a sequence by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('DELETE FROM sequences WHERE id = ?', (seq_id,))
            success = cursor.rowcount > 0
            conn.commit()
            return success
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def _row_to_dict(self, cursor, row):
        """Convert SQLite row to dictionary"""
        columns = [description[0] for description in cursor.description]
        result = {}
        for i, column in enumerate(columns):
            result[column] = row[i]
        return result

    def export_pdf(self, seq_id, save_path=None):
        """Export PDF file from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT pdf_data, pdf_filename FROM sequences WHERE id = ?', (seq_id,))
            result = cursor.fetchone()

            if result and result[0] is not None:
                pdf_data, pdf_filename = result[0], result[1]

                if save_path is None:
                    downloads_dir = "downloads"
                    os.makedirs(downloads_dir, exist_ok=True)
                    save_path = os.path.join(downloads_dir, pdf_filename)

                with open(save_path, 'wb') as file:
                    file.write(pdf_data)

                return save_path
            return None
        except Exception as e:
            print(f"Error exporting PDF: {e}")
            return None
        finally:
            conn.close()