# Copyright 2026 Google LLC
# Network diagnostic tools for General IT & Tech Support Agent.

import socket
import time


def ping_host(host: str, port: int = 80, timeout: float = 3.0) -> str:
    """Executes a real network connectivity and latency check against a target host or IP address.

    Args:
        host: Hostname or IP address to test (e.g., 'google.com', '8.8.8.8', '1.1.1.1', 'sso.company.com').
        port: Port number to test TCP connection against (default is 80 for HTTP, 443 for HTTPS, 53 for DNS).
        timeout: Timeout in seconds for the connection attempt (default is 3.0 seconds).

    Returns:
        Formatted summary indicating reachability, resolved IP address, and latency in milliseconds.
    """
    cleaned_host = host.strip().lower()
    # Strip protocol or path if user provided a URL
    if cleaned_host.startswith("http://"):
        cleaned_host = cleaned_host[7:]
    if cleaned_host.startswith("https://"):
        cleaned_host = cleaned_host[8:]
    cleaned_host = cleaned_host.split("/")[0]

    if not cleaned_host:
        return "Error: Please provide a valid hostname or IP address."

    try:
        # Resolve IP address
        ip = socket.gethostbyname(cleaned_host)

        # Measure TCP socket connection latency
        start_time = time.perf_counter()
        sock = socket.create_connection((ip, port), timeout=timeout)
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        sock.close()

        return (
            f"✅ Host '{cleaned_host}' ({ip}) is ONLINE & REACHABLE.\n"
            f"Tested Port: {port} | Latency: {elapsed_ms:.2f} ms"
        )
    except socket.gaierror:
        return f"❌ Host '{cleaned_host}' FAILED: Could not resolve hostname or DNS record."
    except (socket.timeout, TimeoutError):
        return f"⏱️ Host '{cleaned_host}' TIMED OUT after {timeout} seconds (Unreachable or blocked on port {port})."
    except Exception as e:
        # Fallback: check if DNS resolved even if specific port was refused
        try:
            ip = socket.gethostbyname(cleaned_host)
            return (
                f"✅ Host '{cleaned_host}' resolved to IP {ip} (DNS Reachable), "
                f"but connection on port {port} failed: {str(e)}"
            )
        except Exception:
            return f"❌ Connection check to '{cleaned_host}' failed: {str(e)}"
