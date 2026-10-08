# Security Policy

> 🌐 Language: **English** | [Tiếng Việt](SECURITY.vi.md)

## Supported surface

Security reports are accepted for the current `main` branch and the latest published release.

## Reporting a vulnerability

Do not open a public issue for an undisclosed vulnerability or exposed credential. Contact **Đăng Khoa <i.am@dangkhoa.dev>** with a concise reproduction, affected path, impact, and any proposed mitigation.

## Project-specific boundaries

- Authenticated endpoints require a per-session Bearer token.
- The internal GPU worker binds to `127.0.0.1` only and is not intended for public exposure.
- Cloudflare Quick Tunnel is optional and ephemeral; tunnel URLs are not authority data and must not be committed.
- Model weights are mounted locally from Kaggle and are not redistributed by this repository.
- Runtime secrets, generated outputs, metadata, logs, and `.runtime/` state are intentionally excluded from source control.
