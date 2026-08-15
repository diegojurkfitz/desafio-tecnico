import logging
import signal
from typing import Optional

from app.models import PacketRecord

logger = logging.getLogger(__name__)

IP_PROTOCOLS: dict[int, str] = {
    1: "ICMP",
    6: "TCP",
    17: "UDP",
}

# Flag global para shutdown graceful
_stop_capture = False


def _signal_handler(sig: int, frame: object) -> None:
    """Handler para Ctrl+C - sinaliza parada da captura."""
    global _stop_capture
    _stop_capture = True
    logger.warning("Interrupcao recebida (SIGINT). Finalizando captura...")


def packet_to_record(packet: object) -> Optional[PacketRecord]:
    """Converte um pacote Scapy em PacketRecord, ou None se nao possuir camada IP."""
    try:
        from scapy.layers.inet import IP
    except ImportError as exc:
        raise RuntimeError(
            "Scapy nao esta instalado. Instale as dependencias ou execute via Docker."
        ) from exc

    if IP not in packet:
        return None

    ip_layer = packet[IP]
    protocol = IP_PROTOCOLS.get(int(ip_layer.proto), str(ip_layer.proto))

    return PacketRecord(
        source_ip=str(ip_layer.src),
        destination_ip=str(ip_layer.dst),
        protocol=protocol,
        packet_size=len(packet),
    )


def capture_packets(interface: str, count: int, timeout: int) -> list[PacketRecord]:
    """
    Captura pacotes da interface de rede com suporte a interrupcao graceful.

    Se o usuario pressionar Ctrl+C durante a captura, os pacotes ja capturados
    sao retornados normalmente, preservando o trabalho realizado.
    """
    global _stop_capture
    _stop_capture = False

    try:
        from scapy.all import sniff
    except ImportError as exc:
        raise RuntimeError(
            "Scapy nao esta instalado. Instale as dependencias ou execute via Docker."
        ) from exc

    # Registrar handler de sinal para shutdown graceful
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, _signal_handler)

    try:
        logger.debug("sniff() iniciado em %s (count=%d, timeout=%d)", interface, count, timeout)
        packets = sniff(
            iface=interface,
            count=count,
            timeout=timeout,
            store=True,
            stop_filter=lambda _: _stop_capture,
        )
    finally:
        # Restaurar handler original
        signal.signal(signal.SIGINT, original_sigint)

    records = [record for packet in packets if (record := packet_to_record(packet)) is not None]
    logger.debug("Pacotes com camada IP extraidos: %d de %d capturados", len(records), len(packets))
    return records


def demo_packets() -> list[PacketRecord]:
    """Retorna pacotes simulados para demonstracao sem permissao de captura."""
    return [
        PacketRecord("10.0.0.10", "8.8.8.8", "UDP", 76),
        PacketRecord("10.0.0.10", "8.8.4.4", "UDP", 120),
        PacketRecord("10.0.0.11", "172.217.29.14", "TCP", 1500),
        PacketRecord("10.0.0.12", "172.217.29.14", "TCP", 60),
        PacketRecord("10.0.0.10", "1.1.1.1", "ICMP", 84),
        PacketRecord("10.0.0.13", "10.0.0.1", "TCP", 66),
        PacketRecord("10.0.0.11", "10.0.0.1", "TCP", 1400),
    ]
