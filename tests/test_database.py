import tempfile
import unittest
from pathlib import Path

from app.capture import demo_packets
from app.database import PacketRepository


class PacketRepositoryTest(unittest.TestCase):
    def test_repository_saves_packets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "packets.db"

            with PacketRepository(str(db_path)) as repository:
                saved = repository.save_many(demo_packets())
                total = repository.connection.execute(
                    "SELECT COUNT(*) FROM packets"
                ).fetchone()[0]

        self.assertEqual(saved, 7)
        self.assertEqual(total, 7)

    def test_repository_saves_empty_list(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "packets.db"

            with PacketRepository(str(db_path)) as repository:
                saved = repository.save_many([])

        self.assertEqual(saved, 0)

    def test_repository_batch_insert_large_set(self):
        """Verifica que insercao em batch funciona para mais de 50 pacotes."""
        from app.models import PacketRecord

        packets = [
            PacketRecord(f"10.0.0.{i % 256}", "192.168.1.1", "TCP", 100)
            for i in range(120)
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "packets.db"

            with PacketRepository(str(db_path)) as repository:
                saved = repository.save_many(packets)
                total = repository.connection.execute(
                    "SELECT COUNT(*) FROM packets"
                ).fetchone()[0]

        self.assertEqual(saved, 120)
        self.assertEqual(total, 120)

    def test_repository_stores_correct_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "packets.db"

            with PacketRepository(str(db_path)) as repository:
                repository.save_many(demo_packets())
                row = repository.connection.execute(
                    "SELECT source_ip, destination_ip, protocol, packet_size FROM packets LIMIT 1"
                ).fetchone()

        self.assertEqual(row["source_ip"], "10.0.0.10")
        self.assertEqual(row["destination_ip"], "8.8.8.8")
        self.assertEqual(row["protocol"], "UDP")
        self.assertEqual(row["packet_size"], 76)


if __name__ == "__main__":
    unittest.main()
