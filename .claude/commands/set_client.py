#!/usr/bin/env python3
"""
set_client.py - Set active SDLC Agêntico client profile
Version: 3.0.0
Part of: Phase 1 - Foundation (Multi-Client Architecture)

Cross-platform (Linux, macOS, Windows)
"""

import sys
from pathlib import Path

# Add lib/python to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib" / "python"))

try:
    from client_resolver import ClientResolver
except ImportError:
    print("ERROR: client_resolver not available", file=sys.stderr)
    print("Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def usage():
    """Print usage and exit."""
    print("Usage: set_client.py <client-id>")
    print()
    print("Set active SDLC Agêntico client profile.")
    print()
    print("Arguments:")
    print("  client-id    Client ID (must exist in .sdlc_clients/ directory)")
    print()
    print("Examples:")
    print("  set_client.py generic        # Use base framework (default)")
    print("  set_client.py demo-client    # Use demo client profile")
    print("  set_client.py yourco         # Use custom client profile")
    print()

    resolver = ClientResolver()
    clients = resolver.list_clients()
    if clients:
        print("Available clients:")
        for c in clients:
            print(f"  - {c}")
    else:
        print("(no clients directory found)")

    sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        usage()

    client_id = sys.argv[1]

    # Initialize resolver
    resolver = ClientResolver()

    # Set client
    success, message = resolver.set_client(client_id)
    print(message)

    if not success:
        sys.exit(1)

    # Show client info
    info = resolver.get_client_info(client_id)
    if info:
        print()
        print("Client Profile:")
        print(f"  ID:      {client_id}")
        print(f"  Name:    {info.get('name', 'N/A')}")
        print(f"  Domain:  {info.get('domain', 'N/A')}")
        print(f"  Version: {info.get('version', 'N/A')}")

    # Next steps
    print()
    print("Next steps:")
    print("  - Run /sdlc-start to use this client profile")
    print("  - Run /new-feature to create feature with this client")
    print(f"  - All workflows will use client: {client_id}")


if __name__ == "__main__":
    main()
