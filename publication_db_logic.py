# publication_db_logic.py
"""
Publication Database Logic Module
Handles database operations for storing and retrieving publications
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class PublicationDatabaseLogic:
    """Handles all database operations for publications"""

    def __init__(self, db_file="publications_db.json"):
        """
        Initialize the database logic
        
        Args:
            db_file: Path to JSON database file
        """
        self.db_file = db_file
        self.publications = []
        self.load_database()

    def load_database(self):
        """Load publications from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    self.publications = json.load(f)
                print(f"✓ Loaded {len(self.publications)} publications from database")
            except Exception as e:
                print(f"Error loading database: {e}")
                self.publications = []
        else:
            self.publications = []
            print("No existing database found. Starting fresh.")

    def save_database(self):
        """Save publications to JSON file"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.publications, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved {len(self.publications)} publications to database")
            return True
        except Exception as e:
            print(f"Error saving database: {e}")
            return False

    def add_publication(self, journal: str, year: int, title: str, 
                       authors: str, abstract: str, pdf_path: Optional[str] = None,
                       volume: Optional[str] = None, issue: Optional[str] = None,
                       pages: Optional[str] = None) -> Dict:
        """
        Add a new publication to the database
        
        Args:
            journal: Journal name
            year: Publication year
            title: Article title
            authors: Author names (comma-separated)
            abstract: Article abstract
            pdf_path: Optional path to PDF file
            volume: Optional journal volume
            issue: Optional journal issue
            pages: Optional page range
            
        Returns:
            Dictionary containing the added publication
        """
        # Generate unique ID
        pub_id = self._generate_id()

        # Create publication entry
        publication = {
            'id': pub_id,
            'journal': journal,
            'year': year,
            'title': title,
            'authors': authors,
            'abstract': abstract,
            'pdf_path': pdf_path,
            'volume': volume,
            'issue': issue,
            'pages': pages,
            'date_added': datetime.now().isoformat(),
            'keywords': self._extract_keywords(title, abstract)
        }

        # Add to database
        self.publications.append(publication)
        self.save_database()

        return publication

    def _generate_id(self) -> str:
        """Generate unique ID for publication"""
        if not self.publications:
            return "PUB001"
        
        # Extract numeric part from last ID
        last_id = self.publications[-1]['id']
        num = int(last_id[3:]) + 1
        return f"PUB{num:03d}"

    def _extract_keywords(self, title: str, abstract: str) -> List[str]:
        """
        Extract keywords from title and abstract
        
        Args:
            title: Article title
            abstract: Article abstract
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction (you can enhance this)
        text = (title + " " + abstract).lower()
        
        # Common stop words to exclude
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 
                     'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was',
                     'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do',
                     'does', 'did', 'will', 'would', 'could', 'should', 'may',
                     'might', 'can', 'this', 'that', 'these', 'those'}
        
        # Extract words
        words = text.split()
        keywords = [w.strip('.,;:!?()[]{}') for w in words 
                   if len(w) > 3 and w.lower() not in stop_words]
        
        # Return unique keywords (first 20)
        return list(dict.fromkeys(keywords))[:20]

    def search_publications(self, query: str) -> List[Dict]:
        """
        Search for publications by keyword, author, or year
        
        Args:
            query: Search query string
            
        Returns:
            List of matching publications
        """
        if not query:
            return []

        query = query.lower()
        results = []

        for pub in self.publications:
            # Search in multiple fields
            searchable_text = " ".join([
                pub['title'].lower(),
                pub['authors'].lower(),
                pub['journal'].lower(),
                pub['abstract'].lower(),
                str(pub['year']),
                " ".join(pub['keywords'])
            ])

            if query in searchable_text:
                results.append(pub)

        return results

    def search_by_author(self, author: str) -> List[Dict]:
        """Search publications by author name"""
        author = author.lower()
        return [pub for pub in self.publications 
                if author in pub['authors'].lower()]

    def search_by_year(self, year: int) -> List[Dict]:
        """Search publications by year"""
        return [pub for pub in self.publications if pub['year'] == year]

    def search_by_year_range(self, start_year: int, end_year: int) -> List[Dict]:
        """Search publications within a year range"""
        return [pub for pub in self.publications 
                if start_year <= pub['year'] <= end_year]

    def search_by_journal(self, journal: str) -> List[Dict]:
        """Search publications by journal name"""
        journal = journal.lower()
        return [pub for pub in self.publications 
                if journal in pub['journal'].lower()]

    def get_publication_by_id(self, pub_id: str) -> Optional[Dict]:
        """Get a specific publication by ID"""
        for pub in self.publications:
            if pub['id'] == pub_id:
                return pub
        return None

    def delete_publication(self, pub_id: str) -> bool:
        """Delete a publication by ID"""
        for i, pub in enumerate(self.publications):
            if pub['id'] == pub_id:
                del self.publications[i]
                self.save_database()
                return True
        return False

    def update_publication(self, pub_id: str, **kwargs) -> bool:
        """Update publication fields"""
        pub = self.get_publication_by_id(pub_id)
        if not pub:
            return False

        # Update allowed fields
        allowed_fields = ['journal', 'year', 'title', 'authors', 'abstract',
                         'pdf_path', 'volume', 'issue', 'pages']
        
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                pub[key] = value

        # Update keywords if title or abstract changed
        if 'title' in kwargs or 'abstract' in kwargs:
            pub['keywords'] = self._extract_keywords(
                pub['title'], pub['abstract']
            )

        self.save_database()
        return True

    def get_all_publications(self) -> List[Dict]:
        """Get all publications"""
        return self.publications

    def get_statistics(self) -> Dict:
        """Get database statistics"""
        if not self.publications:
            return {
                'total': 0,
                'years': [],
                'journals': [],
                'authors': []
            }

        years = [pub['year'] for pub in self.publications]
        journals = list(set([pub['journal'] for pub in self.publications]))
        
        # Extract unique authors
        all_authors = []
        for pub in self.publications:
            authors = [a.strip() for a in pub['authors'].split(',')]
            all_authors.extend(authors)
        unique_authors = list(set(all_authors))

        return {
            'total': len(self.publications),
            'years': sorted(list(set(years))),
            'year_range': (min(years), max(years)) if years else (0, 0),
            'journals': sorted(journals),
            'journal_count': len(journals),
            'unique_authors': len(unique_authors),
            'most_recent': max(years) if years else None,
            'oldest': min(years) if years else None
        }

    def export_to_bibtex(self, publications: List[Dict], filename: str) -> bool:
        """
        Export publications to BibTeX format
        
        Args:
            publications: List of publications to export
            filename: Output filename
            
        Returns:
            True if successful
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for pub in publications:
                    # Create BibTeX entry
                    entry_type = "article"
                    cite_key = f"{pub['authors'].split(',')[0].strip().replace(' ', '')}_{pub['year']}"
                    
                    f.write(f"@{entry_type}{{{cite_key},\n")
                    f.write(f"  title = {{{pub['title']}}},\n")
                    f.write(f"  author = {{{pub['authors']}}},\n")
                    f.write(f"  journal = {{{pub['journal']}}},\n")
                    f.write(f"  year = {{{pub['year']}}},\n")
                    
                    if pub.get('volume'):
                        f.write(f"  volume = {{{pub['volume']}}},\n")
                    if pub.get('issue'):
                        f.write(f"  number = {{{pub['issue']}}},\n")
                    if pub.get('pages'):
                        f.write(f"  pages = {{{pub['pages']}}},\n")
                    if pub.get('abstract'):
                        f.write(f"  abstract = {{{pub['abstract']}}},\n")
                    
                    f.write("}\n\n")
            
            return True
        except Exception as e:
            print(f"Error exporting to BibTeX: {e}")
            return False


if __name__ == "__main__":
    # Test the database logic
    db = PublicationDatabaseLogic("test_publications.json")
    
    # Add sample publication
    pub = db.add_publication(
        journal="Nature",
        year=2023,
        title="CRISPR-Cas9 Gene Editing in Human Cells",
        authors="Smith, J., Doe, A., Johnson, B.",
        abstract="This study demonstrates the application of CRISPR-Cas9 technology for precise gene editing in human cell lines.",
        volume="612",
        issue="7940",
        pages="123-130"
    )
    
    print(f"\nAdded publication: {pub['id']}")
    print(f"Statistics: {db.get_statistics()}")
    
    # Search test
    results = db.search_publications("CRISPR")
    print(f"\nSearch results for 'CRISPR': {len(results)} found")
