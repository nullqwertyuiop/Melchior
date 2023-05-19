import argparse

parser = argparse.ArgumentParser(description="Melchior daemon")
parser.add_argument("--port", "-p", type=int, default=44550, help="Daemon socket 使用的端口")
parser.add_argument("--dry", "-d", action="store_true", help="仅启动 Daemon，不启动 Melchior")
parser.add_argument(
    "--auto-restart", "-r", action="store_true", help="在 Melchior 退出后自动重启"
)
