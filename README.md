# sms_mcp

Serwer MCP do wysyłania SMS-ów przez API OVH. Odbiorcę podajesz numerem albo nazwą z listy kontaktów, np. „wyślij sms do marcin: jestem za 10 min”.

## Narzędzia

| Narzędzie | Opis |
|---|---|
| `send_sms(recipient, message)` | Wysyła SMS. `recipient` to nazwa kontaktu (wielkość liter bez znaczenia) albo numer: `+48…`, `0048…` albo samo 9 cyfr (wtedy dodaje `+48`). Zwraca odpowiedź OVH albo błąd z OVH, np. brak kredytów. |
| `list_contacts()` | Zwraca listę kontaktów (nazwa → numer). |

## Instalacja przez mcp_loader

Dla instalatora:

- szablon: `python-uv` (wykrywany z `requirements.txt`)
- komenda startowa: `["python", "app.py"]`
- transport: `stdio` (domyślny; loader opakowuje go w `mcp-proxy`)

### Zmienne środowiskowe (env_keys)

| Nazwa | Wymagana | Opis |
|---|---|---|
| `OVH_APPLICATION_KEY` | tak | Application Key z OVH (https://eu.api.ovh.com/createToken/) |
| `OVH_APPLICATION_SECRET` | tak | Application Secret z OVH |
| `OVH_CONSUMER_KEY` | tak | Consumer Key z OVH. Potrzebne uprawnienia: `GET /sms/`, `POST /sms/*/jobs` |
| `CONTACTS` | nie | Lista kontaktów `nazwa:numer` po przecinku, np. `marcin:+48123456789,ania:500600700` |
| `OVH_ENDPOINT` | nie | Region API OVH, domyślnie `ovh-eu` |
| `OVH_SMS_SERVICE` | nie | Nazwa konta SMS (np. `sms-ab12345-1`). Puste: pierwsze konto z listy |
| `OVH_SMS_SENDER` | nie | Nadawca zarejestrowany w panelu OVH. Puste: krótki numer OVH, odbiorca może odpisać |

**Pod mcp_loader nie ustawiaj `MCP_TRANSPORT`, `MCP_HOST` ani `MCP_PORT`.** Serwer musi działać w stdio. Inny transport zajmie port 8000 i `mcp-proxy` nie wystartuje.

## Uruchomienie lokalne

```
python -m venv venv
venv\Scripts\pip install -r requirements.txt
copy .env.example .env    # uzupełnij klucze OVH i CONTACTS
venv\Scripts\python app.py
```

Z `MCP_TRANSPORT=streamable-http` w `.env` serwer nasłuchuje pod `http://<host>:8000/mcp`. Tak go podłączysz bezpośrednio w OpenHands (Settings → MCP → SHTTP). Bez tej zmiennej działa w stdio.

Uwaga: przy `streamable-http` serwer nie ma uwierzytelniania. Każdy, kto ma dostęp do portu, może wysyłać SMS-y na twój koszt. Lokalnie ustaw `MCP_HOST=127.0.0.1`.
