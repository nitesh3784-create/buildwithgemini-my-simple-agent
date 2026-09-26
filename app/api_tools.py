# Copyright 2026 Google LLC
# Public API tools for General IT & Tech Support Agent.

import json
import urllib.request


def lookup_ip_info(query: str = "") -> str:
    """Fetches IP, ISP, organization, and geolocation details for an IP address or domain name.

    Args:
        query: Optional IP address or domain name (e.g., '8.8.8.8', '1.1.1.1', 'github.com').
               If empty, fetches details for the agent's egress IP address.

    Returns:
        Formatted string containing ISP, organization, AS number, location, and timezone.
    """
    target = query.strip().lower()
    if target.startswith("http://"):
        target = target[7:]
    if target.startswith("https://"):
        target = target[8:]
    target = target.split("/")[0]

    url = f"http://ip-api.com/json/{target}" if target else "http://ip-api.com/json/"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ITSupportAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        if data.get("status") == "fail":
            return f"❌ IP/Domain lookup failed for '{query}': {data.get('message', 'Invalid IP/domain')}"

        return (
            f"🌐 IP & Network Info for '{data.get('query')}':\n"
            f"  ISP: {data.get('isp')}\n"
            f"  Organization: {data.get('org') or 'N/A'}\n"
            f"  AS Number: {data.get('as')}\n"
            f"  Location: {data.get('city')}, {data.get('regionName')}, {data.get('country')}\n"
            f"  Timezone: {data.get('timezone')}"
        )
    except Exception as e:
        return f"Error querying IP info API for '{query}': {str(e)}"
