import argparse
import sys

from app.capture import capture_packets, demo_packets
from app.database import PacketRepository
from app.stats import calculate_stats, format_stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Captura pacotes de rede, armazena em SQLite e exibe estatisticas basicas."
    )
    parser.add_argument(
        "-i",
        "--interface",
        default="eth0",
        help="Interface de rede utilizada na captura. Padrao: eth0.",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        default=100,
        help="Quantidade maxima de pacotes a capturar. Padrao: 100.",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=30,
        help="Tempo maximo de captura em segundos. Padrao: 30.",
    )
    parser.add_argument(
        "--db",
        default="/data/packets.db",
        help="Caminho do banco SQLite. Padrao: /data/packets.db.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Usa pacotes simulados para demonstracao sem permissao de captura.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.count <= 0:
        print("Erro: --count deve ser maior que zero.", file=sys.stderr)
        return 2

    if args.timeout <= 0:
        print("Erro: --timeout deve ser maior que zero.", file=sys.stderr)
        return 2

    try:
        if args.demo:
            packets = demo_packets()
        else:
            print(f"Capturando ate {args.count} pacotes na interface {args.interface} "
                  f"(timeout: {args.timeout}s)...")
            print("Pressione Ctrl+C para interromper a captura a qualquer momento.\n")
            packets = capture_packets(
                interface=args.interface,
                count=args.count,
                timeout=args.timeout,
            )

        # Armazenar no banco (insercao em batch)
        with PacketRepository(args.db) as repository:
            saved = repository.save_many(packets)

        # Exibir estatisticas
        print(format_stats(calculate_stats(packets)))
        print("")
        print(f"Pacotes armazenados no banco: {saved}")
        print(f"Banco utilizado: {args.db}")
        return 0
    except PermissionError:
        print(
            "Erro de permissao ao capturar pacotes. Execute o container com NET_RAW/NET_ADMIN "
            "ou use --demo para validar a aplicacao.",
            file=sys.stderr,
        )
        return 1
    except Exception as exc:
        print(f"Erro durante a execucao: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
