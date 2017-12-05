# -*- coding: utf-8 -*-

import sys
from app.main import Main


if __name__ == '__main__':
    Main(sys.argv[1] if len(sys.argv) == 2 else '').process()
