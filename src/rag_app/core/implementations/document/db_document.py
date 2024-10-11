from typing import List, Optional, Dict
import oracledb
from ...interfaces.document_interface import DocumentInterface, Chunk
import uuid

class DBDocument(DocumentInterface):
    def __init__(self, id: str, name: str, collection: str, title: str, content: Optional[str] = None, db_connection: oracledb.Connection = None):
        self._id = id
        self._name = name
        self._collection = collection
        self._title = title
        self._db_connection = db_connection
        if content:
            self.content = content

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def collection(self) -> str:
        return self._collection

    @property
    def title(self) -> str:
        return self._title

    @property
    def content(self) -> Optional[str]:
        cursor = self._db_connection.cursor()
        cursor.execute("SELECT content FROM documents WHERE id = :id", id=self._id)
        result = cursor.fetchone()
        return result[0] if result else None

    @content.setter
    def content(self, value: str) -> None:
        cursor = self._db_connection.cursor()
        cursor.execute("MERGE INTO documents d USING (SELECT :id AS id FROM DUAL) s "
                       "ON (d.id = s.id) "
                       "WHEN MATCHED THEN UPDATE SET d.content = :content "
                       "WHEN NOT MATCHED THEN INSERT (id, name, collection, title, content) "
                       "VALUES (:id, :name, :collection, :title, :content)",
                       id=self._id, name=self._name, collection=self._collection, title=self._title, content=value)
        self._db_connection.commit()

    @property
    def keywords(self) -> List[str]:
        cursor = self._db_connection.cursor()
        cursor.execute("SELECT keyword FROM document_keywords WHERE document_id = :id", id=self._id)
        return [row[0] for row in cursor.fetchall()]

    @keywords.setter
    def keywords(self, value: List[str]) -> None:
        cursor = self._db_connection.cursor()
        cursor.execute("DELETE FROM document_keywords WHERE document_id = :id", id=self._id)
        cursor.executemany("INSERT INTO document_keywords (document_id, keyword) VALUES (:id, :keyword)",
                           [(self._id, keyword) for keyword in value])
        self._db_connection.commit()

    @property
    def chunks(self) -> List[Chunk]:
        cursor = self._db_connection.cursor()
        cursor.execute("SELECT chunk_id, metadata, content FROM document_chunks WHERE document_id = :id ORDER BY chunk_id",
                       id=self._id)
        return [Chunk(self._id, row[0], eval(row[1]), row[2]) for row in cursor.fetchall()]

    @chunks.setter
    def chunks(self, value: List[Chunk]) -> None:
        cursor = self._db_connection.cursor()
        cursor.execute("DELETE FROM document_chunks WHERE document_id = :id", id=self._id)
        cursor.executemany("INSERT INTO document_chunks (document_id, chunk_id, metadata, content) VALUES (:document_id, :chunk_id, :metadata, :content)",
                           [(chunk.document_id, chunk.chunk_id, str({**chunk.metadata, 'document_name': self._name}), chunk.content) for chunk in value])
        self._db_connection.commit()

    def __repr__(self):
        return f"DBDocument(id='{self.id}', name='{self.name}', collection='{self.collection}', title='{self.title}')"
