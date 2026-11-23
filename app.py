import os
import re

import ovh
from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

mcp = MCPServer("sms")


def contacts() -> dict[str, str]:
    # CONTACTS=marcin:+48123456789,ania:500600700
    pairs = (c.split(":", 1) for c in os.getenv("CONTACTS", "").split(",") if ":" in c)
    return {name.strip().lower(): number.strip() for name, number in pairs}


def normalize(number: str) -> str:
    n = re.sub(r"[\s\-()]", "", number)
    if n.startswith("00"):
        n = "+" + n[2:]
    elif re.fullmatch(r"\d{9}", n):
        n = "+48" + n  # shortcut: bare 9 digits assumed Polish, use +CC for other countries
    if not re.fullmatch(r"\+\d{8,15}", n):
        raise ValueError(f"Niepoprawny numer telefonu: {number}")
    return n


def resolve(recipient: str) -> str:
    return normalize(contacts().get(recipient.strip().lower(), recipient))


@mcp.tool()
def list_contacts() -> dict[str, str]:
    """Lista kontaktow (nazwa -> numer) z .env."""
    return contacts()


@mcp.tool()
def send_sms(recipient: str, message: str) -> str:
    """Wyslij SMS. recipient = nazwa kontaktu z listy (np. 'marcin') albo numer telefonu (np. +48123456789)."""
    try:
        number = resolve(recipient)
    except ValueError:
        return f"Nie znam kontaktu '{recipient}' i to nie jest numer. Kontakty: {', '.join(contacts()) or 'brak'}"
    client = ovh.Client(
        endpoint=os.getenv("OVH_ENDPOINT", "ovh-eu"),
        application_key=os.environ["OVH_APPLICATION_KEY"],
        application_secret=os.environ["OVH_APPLICATION_SECRET"],
        consumer_key=os.environ["OVH_CONSUMER_KEY"],
    )
    service = os.getenv("OVH_SMS_SERVICE") or client.get("/sms/")[0]  # key is granted "/sms/", not "/sms"
    body = {"message": message, "receivers": [number], "noStopClause": True}
    if sender := os.getenv("OVH_SMS_SENDER"):
        body["sender"] = sender
    else:
        body["senderForResponse"] = True
    result = client.post(f"/sms/{service}/jobs", **body)
    if result.get("invalidReceivers"):
        return f"OVH odrzucil numer {number}: {result}"
    return f"Wyslano SMS do {recipient} ({number}). Zuzyte kredyty: {result.get('totalCreditsRemoved')}"


if __name__ == "__main__":
    # stdio for local clients; MCP_TRANSPORT=sse or streamable-http for OpenHands over network
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    http = {} if transport == "stdio" else {"host": os.getenv("MCP_HOST", "0.0.0.0"), "port": int(os.getenv("MCP_PORT", "8000"))}
    mcp.run(transport=transport, **http)
