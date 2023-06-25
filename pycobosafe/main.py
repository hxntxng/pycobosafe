from argparse import ArgumentParser

from pycobosafe.console import CoboSafeConsole
from pycobosafe.utils import connect_new_chain, get_all_support_chains


def get_args():
    parser = ArgumentParser(
        prog="cobosafe", description="CoboSafe utilities command-line tool."
    )

    parser.add_argument(
        "-c",
        "--chain",
        choices=get_all_support_chains(),
        default="mainnet",
        help="Chain of the network.",
    )

    parser.add_argument(
        "--cmd",
        nargs="+",
        help="Execute one command in peth console.",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print debug logs.",
    )

    parser.add_argument(
        "--console",
        action="store_true",
        help="Start CoboSafe console.",
    )

    args = parser.parse_args()
    return args


def main():
    args = get_args()

    connect_new_chain(args.chain)

    console = CoboSafeConsole()

    if args.debug:
        console.debug = True

    if args.cmd:
        cmd_str = " ".join(args.cmd)
        for cmd in cmd_str.split(";"):
            console.single_command(cmd)

        # Run commands and start console
        if args.console:
            console.start_console()
    else:
        console.start_console()


if __name__ == "__main__":
    main()
