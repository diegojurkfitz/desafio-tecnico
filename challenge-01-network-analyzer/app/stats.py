from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable

from app.models import PacketRecord


@dataclass(frozen=True)
class TrafficStats:
    total_packets: int
    total_bytes: int
    packets_by_protocol: list[tuple[str, int]]
    top_sources: list[tuple[str, int, int]]
    top_destinations: list[tuple[str, int, int]]


def calculate_stats(packets: Iterable[PacketRecord]) -> TrafficStats:
    records = list(packets)
    protocols = Counter(packet.protocol for packet in records)

    source_bytes: dict[str, int] = defaultdict(int)
    source_count: dict[str, int] = defaultdict(int)
    dest_bytes: dict[str, int] = defaultdict(int)
    dest_count: dict[str, int] = defaultdict(int)

    total_bytes = 0
    for packet in records:
        total_bytes += packet.packet_size
        source_bytes[packet.source_ip] += packet.packet_size
        source_count[packet.source_ip] += 1
        dest_bytes[packet.destination_ip] += packet.packet_size
        dest_count[packet.destination_ip] += 1

    top_sources = sorted(source_bytes.items(), key=lambda x: x[1], reverse=True)[:5]
    top_sources_full = [(ip, source_count[ip], bytes_val) for ip, bytes_val in top_sources]

    top_destinations = sorted(dest_bytes.items(), key=lambda x: x[1], reverse=True)[:5]
    top_destinations_full = [(ip, dest_count[ip], bytes_val) for ip, bytes_val in top_destinations]

    return TrafficStats(
        total_packets=len(records),
        total_bytes=total_bytes,
        packets_by_protocol=protocols.most_common(),
        top_sources=top_sources_full,
        top_destinations=top_destinations_full,
    )


def format_stats(stats: TrafficStats) -> str:
    lines = [
        "Resumo do trafego capturado",
        "=" * 29,
        f"Total de pacotes: {stats.total_packets}",
        f"Total de bytes: {_format_bytes(stats.total_bytes)}",
        "",
        "Pacotes por protocolo:",
    ]

    lines.extend(_format_protocol(stats.packets_by_protocol))
    lines.append("")
    lines.append("Top 5 IPs de origem (por volume de trafego):")
    lines.extend(_format_top_ips(stats.top_sources))
    lines.append("")
    lines.append("Top 5 IPs de destino (por volume de trafego):")
    lines.extend(_format_top_ips(stats.top_destinations))
    return "\n".join(lines)


def _format_protocol(items: list[tuple[str, int]]) -> list[str]:
    if not items:
        return ["- nenhum pacote encontrado"]
    return [f"- {name}: {count}" for name, count in items]


def _format_top_ips(items: list[tuple[str, int, int]]) -> list[str]:
    if not items:
        return ["- nenhum pacote encontrado"]
    return [f"- {ip}: {count} pkts, {_format_bytes(bytes_val)}" for ip, count, bytes_val in items]


def _format_bytes(value: int) -> str:
    if value < 1024:
        return f"{value} B"
    elif value < 1024 * 1024:
        return f"{value / 1024:.1f} KB"
    elif value < 1024 * 1024 * 1024:
        return f"{value / (1024 * 1024):.1f} MB"
    return f"{value / (1024 * 1024 * 1024):.1f} GB"
