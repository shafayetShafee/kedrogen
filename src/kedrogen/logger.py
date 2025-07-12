from rich import print

class Logger:
    def __init__(self, verbose: bool = False, quiet: bool = False):
        self.verbose = verbose
        self.quiet = quiet

    def info(self, msg: str):
        if not self.quiet:
            print(msg)

    def debug(self, msg: str):
        if self.verbose and not self.quiet:
            print(msg)

    def warn(self, msg: str):
        print(msg)

    def error(self, msg: str):
        print(msg)