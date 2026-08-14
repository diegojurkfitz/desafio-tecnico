from dataclasses import dataclass


@dataclass(frozen=True)
class PacketRecord:
    source_ip: str
    destination_ip: str
    protocol: str
    packet_size: int
