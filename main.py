# parmer is a Linux System-wide Grammer checker, for free :D



import sys

from ui.application import ParmerApplication


def main():
    app = ParmerApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
