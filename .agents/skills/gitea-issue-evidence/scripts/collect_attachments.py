#!/usr/bin/env python3
"""Download Gitea issue attachments with a matching local Tea PAT."""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, unquote, urlencode, urljoin, urlparse, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tif", ".tiff"}
LOG_EXTENSIONS = {".log", ".txt", ".out", ".trace"}
SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS | LOG_EXTENSIONS
ATTACHMENT_MARKERS = ("/attachments/", "/uploads/")
URL_PATTERNS = (
    re.compile(r"!?\[[^\]]*\]\(\s*<?([^\s)>]+)", re.IGNORECASE),
    re.compile(r"<(https?://[^>\s]+)>", re.IGNORECASE),
    re.compile(r"(?:src|href)=[\"']([^\"']+)[\"']", re.IGNORECASE),
    re.compile(r"(?<![\w\"'=])(https?://[^\s<>)\]]+)", re.IGNORECASE),
)
MIME_EXTENSIONS = {
    "image/png": ".png", "image/jpeg": ".jpg", "image/gif": ".gif", "image/webp": ".webp",
    "image/bmp": ".bmp", "image/tiff": ".tiff", "text/plain": ".txt",
}


class EvidenceError(RuntimeError):
    """A bounded collection or Tea credential error."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True, help="Gitea origin, for example https://git.example.com")
    parser.add_argument("--issue-json", type=Path, help="Normalized issue_read(method=get) JSON")
    parser.add_argument("--comments-json", type=Path, help="Normalized issue_read(method=get_comments) JSON")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--tea-login", help="Tea login name; otherwise select the unique/default origin match")
    parser.add_argument("--credential-check-only", action="store_true", help="Validate the local Tea credential without downloading or writing files")
    parser.add_argument("--max-attachment-bytes", type=int, default=25 * 1024 * 1024)
    parser.add_argument("--allow-external-origin", action="append", default=[], metavar="ORIGIN")
    return parser.parse_args()


def origin(url: str) -> tuple[str, str, int | None]:
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    port = parsed.port
    if (scheme == "http" and port == 80) or (scheme == "https" and port == 443):
        port = None
    return scheme, (parsed.hostname or "").lower(), port


def redacted_url(url: str) -> str:
    parsed = urlsplit(url)
    query = urlencode([(key, "[REDACTED]") for key, _ in parse_qsl(parsed.query, keep_blank_values=True)])
    hostname = parsed.hostname or ""
    if ":" in hostname and not hostname.startswith("["):
        hostname = f"[{hostname}]"
    port = f":{parsed.port}" if parsed.port else ""
    return urlunsplit((parsed.scheme, f"{hostname}{port}" if parsed.netloc else "", parsed.path, query, ""))


def resolve_tea_token(base_url: str, login_name: str | None) -> tuple[str, str]:
    tea = shutil.which("tea")
    if not tea:
        raise EvidenceError("local Tea executable was not found on PATH")
    parsed = urlparse(base_url)
    command = [tea, "login", "helper", "get"]
    if login_name:
        command.extend(("--login", login_name))
    request = f"protocol={parsed.scheme}\nhost={parsed.netloc}\n\n"
    try:
        completed = subprocess.run(
            command,
            input=request,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise EvidenceError("tea login helper get could not complete") from exc
    if completed.returncode != 0:
        raise EvidenceError("tea login helper get failed; configure a matching local Tea login or upgrade Tea")

    credentials: dict[str, str] = {}
    for line in completed.stdout.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            credentials[key.strip()] = value.strip()
    token = credentials.get("password", "")
    if not token:
        raise EvidenceError("tea login helper get returned no token")
    returned_url = f"{credentials.get('protocol', '')}://{credentials.get('host', '')}"
    try:
        if origin(returned_url) != origin(base_url):
            raise EvidenceError("Tea credential origin does not match the requested Gitea origin")
    except ValueError as exc:
        raise EvidenceError("Tea credential helper returned an invalid origin") from exc
    return login_name or credentials.get("username") or "origin-match", token


def read_json(path: Path, expected: type) -> Any:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"could not read {path}: {exc}") from exc
    if not isinstance(payload, expected):
        raise EvidenceError(f"{path} must contain a JSON {expected.__name__}")
    return payload


def iter_urls(body: str) -> Iterable[str]:
    seen: set[str] = set()
    for pattern in URL_PATTERNS:
        for match in pattern.finditer(body or ""):
            candidate = match.group(1).strip().rstrip(".,;:")
            if candidate and candidate not in seen:
                seen.add(candidate)
                yield candidate


def category(path_or_url: str, content_type: str = "") -> str:
    suffix = Path(unquote(urlparse(path_or_url).path)).suffix.lower()
    mime = content_type.split(";", 1)[0].strip().lower()
    if suffix in IMAGE_EXTENSIONS or mime.startswith("image/"):
        return "image"
    if suffix in LOG_EXTENSIONS or mime.startswith("text/"):
        return "log"
    return "other"


def is_candidate(url: str) -> bool:
    parsed = urlparse(url)
    return Path(unquote(parsed.path)).suffix.lower() in SUPPORTED_EXTENSIONS or any(marker in parsed.path.lower() for marker in ATTACHMENT_MARKERS)


def safe_name(url: str, headers: Any, index: int, preferred: str) -> str:
    filename = preferred or Path(unquote(urlparse(url).path)).name or f"attachment-{index:03d}"
    filename = re.sub(r"[^A-Za-z0-9._-]+", "-", filename).strip(".-") or f"attachment-{index:03d}"
    content_type = headers.get_content_type() if hasattr(headers, "get_content_type") else ""
    if not Path(filename).suffix:
        filename += MIME_EXTENSIONS.get(content_type) or mimetypes.guess_extension(content_type) or ""
    return filename[:180]


def unique_path(directory: Path, filename: str) -> Path:
    candidate = directory / filename
    counter = 2
    while candidate.exists():
        candidate = directory / f"{Path(filename).stem}-{counter}{Path(filename).suffix}"
        counter += 1
    return candidate


class SafeRedirect(HTTPRedirectHandler):
    def __init__(self, allowed: set[tuple[str, str, int | None]], auth_origin: tuple[str, str, int | None], token: str) -> None:
        super().__init__()
        self.allowed = allowed
        self.auth_origin = auth_origin
        self.token = token

    def redirect_request(self, req: Request, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> Request | None:
        resolved = urljoin(req.full_url, newurl)
        target = origin(resolved)
        if target not in self.allowed:
            raise HTTPError(resolved, 403, "redirect target origin is not allowed", headers, fp)
        redirected = super().redirect_request(req, fp, code, msg, headers, resolved)
        if redirected is not None and target == self.auth_origin:
            redirected.add_unredirected_header("Authorization", f"token {self.token}")
        return redirected


def download(url: str, destination: Path, token: str, maximum: int, index: int, allowed: set[tuple[str, str, int | None]], auth_origin: tuple[str, str, int | None], preferred: str) -> dict[str, Any]:
    target_origin = origin(url)
    request = Request(url, headers={"Accept": "*/*", "User-Agent": "gitea-issue-driven/2"})
    if target_origin == auth_origin:
        request.add_unredirected_header("Authorization", f"token {token}")
    opener = build_opener(SafeRedirect(allowed, auth_origin, token))
    try:
        with opener.open(request, timeout=45) as response:
            declared = response.headers.get("Content-Length")
            if declared and int(declared) > maximum:
                raise EvidenceError(f"attachment exceeds {maximum} bytes")
            filename = safe_name(response.geturl(), response.headers, index, preferred)
            target = unique_path(destination, filename)
            digest = hashlib.sha256()
            size = 0
            with target.open("wb") as output:
                while chunk := response.read(64 * 1024):
                    size += len(chunk)
                    if size > maximum:
                        output.close()
                        target.unlink(missing_ok=True)
                        raise EvidenceError(f"attachment exceeds {maximum} bytes")
                    digest.update(chunk)
                    output.write(chunk)
            content_type = response.headers.get("Content-Type", "application/octet-stream")
            return {"status": "downloaded", "local_path": str(target), "content_type": content_type, "size": size, "sha256": digest.hexdigest(), "category": category(filename, content_type)}
    except HTTPError as exc:
        raise EvidenceError(f"HTTP {exc.code}") from exc
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        raise EvidenceError(str(exc)) from exc


def candidate_sources(issue: dict[str, Any], comments: list[Any]) -> Iterable[tuple[str, Any, str, list[Any]]]:
    yield "issue", issue.get("number") or issue.get("index"), str(issue.get("body") or ""), list(issue.get("assets") or [])
    for comment in comments:
        if isinstance(comment, dict):
            yield "comment", comment.get("id"), str(comment.get("body") or ""), list(comment.get("assets") or [])


def main() -> int:
    args = parse_args()
    if args.max_attachment_bytes < 1:
        print("--max-attachment-bytes must be positive", file=sys.stderr)
        return 2
    if not args.credential_check_only and (args.issue_json is None or args.comments_json is None or args.output is None):
        print("--issue-json, --comments-json, and --output are required unless --credential-check-only is used", file=sys.stderr)
        return 2
    base_url = args.base_url.rstrip("/")
    parsed = urlparse(base_url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        print("--base-url must be an absolute HTTPS URL without embedded credentials", file=sys.stderr)
        return 2

    try:
        base_origin = origin(base_url)
        login_name, token = resolve_tea_token(base_url, args.tea_login)
    except (EvidenceError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.credential_check_only:
        print(f"Tea credential gate passed for {base_url} using login {login_name}; token was not exposed")
        return 0

    try:
        issue = read_json(args.issue_json, dict)
        comments = read_json(args.comments_json, list)
        external_origins = {origin(item) for item in args.allow_external_origin}
        for item in args.allow_external_origin:
            candidate = urlparse(item)
            if candidate.scheme != "https" or not candidate.netloc or candidate.username or candidate.password:
                raise EvidenceError(f"invalid external HTTPS origin: {item}")
    except (EvidenceError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    output = args.output.resolve()
    attachments_dir = output / "attachments"
    attachments_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    warnings: list[str] = []
    seen: set[str] = set()
    allowed = {base_origin, *external_origins}

    for source_kind, source_id, body, assets in candidate_sources(issue, comments):
        candidates: list[tuple[str, dict[str, Any] | None]] = []
        for asset in assets:
            if isinstance(asset, dict) and (asset.get("browser_download_url") or asset.get("url")):
                candidates.append((str(asset.get("browser_download_url") or asset.get("url")), asset))
        candidates.extend((url, None) for url in iter_urls(body))
        for raw_url, asset in candidates:
            resolved = urljoin(f"{base_url}/", raw_url)
            if resolved in seen or (asset is None and not is_candidate(resolved)):
                continue
            seen.add(resolved)
            record: dict[str, Any] = {"source_kind": source_kind, "source_id": source_id, "url": redacted_url(resolved), "category": category(str((asset or {}).get("name") or resolved))}
            try:
                target_origin = origin(resolved)
                if target_origin not in allowed:
                    raise EvidenceError("external attachment origin is not allowlisted")
                result = download(resolved, attachments_dir, token, args.max_attachment_bytes, len(records) + 1, allowed, base_origin, str((asset or {}).get("name") or ""))
                result["local_path"] = str(Path(result["local_path"]).relative_to(output))
                record.update(result)
            except (EvidenceError, ValueError) as exc:
                record.update(status="error", reason=str(exc))
                warnings.append(f"Could not download {redacted_url(resolved)}: {exc}")
            records.append(record)

    manifest = {
        "schema_version": 2,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "source": {"base_url": base_url, "issue": issue.get("number") or issue.get("index")},
        "tea": {"login": login_name, "credential_source": "tea login helper get", "token_exposed": False},
        "attachments": records,
        "warnings": warnings,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Collected {sum(1 for item in records if item.get('status') == 'downloaded')} of {len(records)} attachment candidates")
    print(output / "manifest.json")
    return 0 if not warnings else 3


if __name__ == "__main__":
    raise SystemExit(main())
