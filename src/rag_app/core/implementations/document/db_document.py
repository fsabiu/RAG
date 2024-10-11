from typing import List, Optional
import oracledb  # You'll need to install this package
from ...interfaces.document_interface import DocumentInterface

class DBDocument(DocumentInterface):
    def __init__(self, name: str, collection: str, title: str, content: Optional[str] = None, db_connection: oracledb.Connection = None):
        self._name = name
        self._collection = collection
        self._title = title
        self._db_connection = db_connection
        if content:
            self.set_content(content)

    @property
    def name(self) -> str:
        return self._name

    @property
    def collection(self) -> str:
        return self._collection

    @property
    def title(self) -> str:
        return self._title

    def get_content(self) -> Optional[str]:
        # Fetch content from the database
        cursor = self._db_connection.cursor()
        cursor.execute("SELECT content FROM documents WHERE name = :name AND collection = :collection", 
                       name=self._name, collection=self._collection)
        result = cursor.fetchone()
        return result[0] if result else None

    def set_content(self, content: str) -> None:
        # Update or insert content in the database
        cursor = self._db_connection.cursor()
        cursor.execute("MERGE INTO documents d USING (SELECT :name AS name, :collection AS collection FROM DUAL) s "
                       "ON (d.name = s.name AND d.collection = s.collection) "
                       "WHEN MATCHED THEN UPDATE SET d.content = :content "
                       "WHEN NOT MATCHED THEN INSERT (name, collection, title, content) "
                       "VALUES (:name, :collection, :title, :content)",
                       name=self._name, collection=self._collection, title=self._title, content=content)
        self._db_connection.commit()

    def get_keywords(self) -> List[str]:
        # Fetch keywords from the database
        cursor = self._db_connection.cursor()
        cursor.execute("SELECT keyword FROM document_keywords WHERE name = :name AND collection = :collection",
                       name=self._name, collection=self._collection)
        return [row[0] for row in cursor.fetchall()]

    def set_keywords(self, keywords: List[str]) -> None:
        # Update keywords in the database
        cursor = self._db_connection.cursor()
        cursor.execute("DELETE FROM document_keywords WHERE name = :name AND collection = :collection",
                       name=self._name, collection=self._collection)
        cursor.executemany("INSERT INTO document_keywords (name, collection, keyword) VALUES (:name, :collection, :keyword)",
                           [(self._name, self._collection, keyword) for keyword in keywords])
        self._db_connection.commit()

    def get_chunks(self) -> List[str]:
        # Fetch chunks from the database
        cursor = self._db_connection.cursor()
        cursor.execute("SELECT chunk FROM document_chunks WHERE name = :name AND collection = :collection ORDER BY chunk_order",
                       name=self._name, collection=self._collection)
        return [row[0] for row in cursor.fetchall()]

    def set_chunks(self, chunks: List[str]) -> None:
        # Update chunks in the database
        cursor = self._db_connection.cursor()
        cursor.execute("DELETE FROM document_chunks WHERE name = :name AND collection = :collection",
                       name=self._name, collection=self._collection)
        cursor.executemany("INSERT INTO document_chunks (name, collection, chunk_order, chunk) VALUES (:name, :collection, :chunk_order, :chunk)",
                           [(self._name, self._collection, i, chunk) for i, chunk in enumerate(chunks)])
        self._db_connection.commit()

    def __repr__(self):
        return f"DBDocument(name='{self.name}', collection='{self.collection}', title='{self.title}')"
