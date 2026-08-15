import logging
import sqlite3
from pathlib import Path
from typing import Iterable

from app.models import PacketRecord

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS packets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    captured_at TEXT NOT NULL DEFAULT (datetime('now')),
    source_ip TEXT NOT NULL,
    destination_ip TEXT NOT NULL,
    protocol TEXT NOT NULL,
    packet_size INTEGER NOT NULL CHECK (packet_size >= 0)
);

CREATE INDEX IF NOT EXISTS idx_packets_protocol ON packets(protocol);
CREATE INDEX IF NOT EXISTS idx_packets_source_ip ON packets(source_ip);
CREATE INDEX IF NOT EXISTS idx_packets_destination_ip ON packets(destination_ip);
"""

# Tamanho do lote para insercao em batch (otimiza I/O em grandes volumes)
BATCH_SIZE: int = 50


class PacketRepository:
    """Repositorio para persistencia de pacotes capturados em SQLite."""

    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)
        if self.db_path.parent:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection: sqlite3.Connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        # WAL mode melhora performance em escritas concorrentes
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.initialize()
        logger.debug("Repositorio inicializado: %s", self.db_path)

    def initialize(self) -> None:
        """Cria schema se nao existir."""
        self.connection.executescript(SCHEMA)
        self.connection.commit()

    def save_many(self, packets: Iterable[PacketRecord]) -> int:
        """
        Armazena pacotes no banco usando insercao em batch.

        Em vez de inserir tudo em uma unica transacao (problematico para volumes
        muito grandes), divide em lotes de BATCH_SIZE para equilibrar performance
        e uso de memoria.
        """
        records = list(packets)
        if not records:
            return 0

        total_saved = 0
        for i in range(0, len(records), BATCH_SIZE):
            batch = records[i:i + BATCH_SIZE]
            self.connection.executemany(
                """
                INSERT INTO packets (source_ip, destination_ip, protocol, packet_size)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (
                        packet.source_ip,
                        packet.destination_ip,
                        packet.protocol,
                        packet.packet_size,
                    )
                    for packet in batch
                ],
            )
            self.connection.commit()
            total_saved += len(batch)

        logger.debug("Batch insert concluido: %d pacotes em %d lotes",
                     total_saved, (len(records) + BATCH_SIZE - 1) // BATCH_SIZE)
        return total_saved

    def close(self) -> None:
        """Fecha conexao com o banco."""
        self.connection.close()

    def __enter__(self) -> "PacketRepository":
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()
