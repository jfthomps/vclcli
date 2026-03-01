#!/usr/bin/env python3
import argparse
import sys

from vcl.rpc import VCLRPCError
from vcl.commands import (
    cmd_test,
    cmd_images_list,
    cmd_request_list,
    cmd_request_create,
    cmd_request_status,
    cmd_request_connect,
    cmd_request_end,
    cmd_request_end_all,
)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="vclctl", description="vclctl")
    p.add_argument("--json", action="store_true", help="Print raw JSON")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("test", help="Test RPC (XMLRPCtest)")
    sp.set_defaults(func=lambda a: cmd_test(json=a.json))

    sp = sub.add_parser("images", help="Images")
    s2 = sp.add_subparsers(dest="subcmd", required=True)
    sp2 = s2.add_parser("list", help="List images")
    sp2.set_defaults(func=lambda a: cmd_images_list(json=a.json))

    sp = sub.add_parser("request", help="Requests")
    s2 = sp.add_subparsers(dest="subcmd", required=True)

    sp2 = s2.add_parser("list", help="List active requests")
    sp2.set_defaults(func=lambda a: cmd_request_list(json=a.json))

    sp2 = s2.add_parser("create", help="Create request")
    sp2.add_argument("--image-id", type=int, required=True)
    sp2.add_argument("--duration", type=int, default=60)
    sp2.add_argument("--start", default="now")
    sp2.set_defaults(func=lambda a: cmd_request_create(a.image_id, a.start, a.duration, json=a.json))

    sp2 = s2.add_parser("status", help="Request status")
    sp2.add_argument("--id", type=int, required=True)
    sp2.set_defaults(func=lambda a: cmd_request_status(a.id, json=a.json))

    sp2 = s2.add_parser("end", help="End request")
    sp2.add_argument("--id", type=int, required=True)
    sp2.set_defaults(func=lambda a: cmd_request_end(a.id, json=a.json))

    sp2 = s2.add_parser("end-all", help="End all active requests")
    sp2.set_defaults(func=lambda a: cmd_request_end_all(json=a.json))

    sp = sub.add_parser("connect", help="Get connect data")
    sp.add_argument("--id", type=int, required=True)
    sp.add_argument("--client-ip", default=None)
    sp.set_defaults(func=lambda a: cmd_request_connect(a.id, client_ip=a.client_ip, json=a.json))

    return p


def main() -> int:
    args = build_parser().parse_args()
    try:
        args.func(args)
        return 0
    except VCLRPCError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Cancelled.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
