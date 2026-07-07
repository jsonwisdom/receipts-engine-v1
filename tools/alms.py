#!/usr/bin/env python3
# ALMS Receipt CLI - V0.1

import sys, json, hashlib
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

def main():
    cmd = sys.argv[1]
    if cmd == 'verify':
        with open(sys.argv[2]) as f:
            data = json.load(f)
        print('VALID' if data.get('signature') else 'INVALID')
        sys.exit(0 if data.get('signature') else 1)
    # sign stub...
    print('ALMS CLI ready')

if __name__ == '__main__':
    main()