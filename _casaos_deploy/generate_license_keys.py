#!/usr/bin/env python3
"""Generate Ed25519 signing keypair for license server.

Prints:
- LICENSE_SIGNING_KEY_B64 (private)
- LICENSE_SERVER_PUBLIC_KEY_B64 (public)

Keep private key SECRET. Public key goes to customers' apps.
"""

import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def main() -> None:
    k = Ed25519PrivateKey.generate()
    sk = k.private_bytes_raw()
    pk = k.public_key().public_bytes_raw()
    print("LICENSE_SIGNING_KEY_B64=", base64.b64encode(sk).decode("ascii"))
    print("LICENSE_SERVER_PUBLIC_KEY_B64=", base64.b64encode(pk).decode("ascii"))


if __name__ == "__main__":
    main()
