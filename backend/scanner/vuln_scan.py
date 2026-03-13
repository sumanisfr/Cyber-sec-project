import re
import socket
import ssl

import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning


requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; CyberShieldLab/1.0; +http://127.0.0.1)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}


class VulnerabilityReport:
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.vulns = []

    def add(self, name, level, description, fix, evidence=None):
        self.vulns.append({
            'name': name,
            'level': level,
            'description': description,
            'fix': fix,
            'evidence': evidence,
        })

    def summary(self):
        levels = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
        for vuln in self.vulns:
            levels[vuln['level']] += 1
        return {
            'target': self.target_url,
            'counts': levels,
            'details': self.vulns,
        }


def _normalize_url(url: str) -> str:
    normalized = (url or '').strip()
    if not normalized:
        return normalized
    if not normalized.startswith(('http://', 'https://')):
        normalized = f'https://{normalized}'
    return normalized


def _build_session():
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    return session


def _fetch(session, url, **kwargs):
    """Wrapper around requests.get with timeout and safe exception handling."""
    try:
        response = session.get(url, timeout=12, allow_redirects=True, verify=True, **kwargs)
        response.raise_for_status()
        return response, None
    except requests.exceptions.SSLError:
        try:
            response = session.get(url, timeout=12, allow_redirects=True, verify=False, **kwargs)
            response.raise_for_status()
            return response, 'TLS certificate validation failed; response was fetched without certificate verification.'
        except Exception as exc:
            return None, str(exc)
    except Exception as exc:
        return None, str(exc)


def _simple_crawl(session, base_url, limit=10):
    """Crawl the given URL for internal links (up to a limit)."""
    urls = {base_url}
    resp, _ = _fetch(session, base_url)
    if not resp or not resp.text:
        return list(urls)

    soup = BeautifulSoup(resp.text, 'html.parser')
    for anchor in soup.find_all('a', href=True):
        href = anchor['href']
        if href.startswith('/'):
            href = base_url.rstrip('/') + href
        if href.startswith(base_url) and href not in urls:
            urls.add(href)
            if len(urls) >= limit:
                break
    return list(urls)


def _check_sql_injection(response_text):
    patterns = [r"\bUNION\s+SELECT\b", r"\bOR\b\s+1=1", r"\b' OR '1'='1"]
    return any(re.search(pattern, response_text, flags=re.IGNORECASE) for pattern in patterns)


def _check_xss(response_text):
    return '<script>alert(1)' in response_text.lower() or 'onerror=' in response_text.lower()


def _check_ssrf(response_text):
    ssrf_patterns = [
        r'http://127\.0\.0\.1',
        r'http://localhost',
        r'http://169\.254\.169\.254',
        r'http://10\.',
        r'http://192\.168\.',
        r'http://172\.(1[6-9]|2[0-9]|3[0-1])\.',
    ]
    return any(re.search(pattern, response_text, flags=re.IGNORECASE) for pattern in ssrf_patterns)


def _check_rce(response_text):
    return 'uid=' in response_text or 'root@' in response_text or 'bash:' in response_text


def _port_scan_allowed(host: str) -> bool:
    return host in {'127.0.0.1', 'localhost'} or host.endswith('.local')


def run_scan(url):
    normalized_url = _normalize_url(url)
    report = VulnerabilityReport(normalized_url)
    parsed = requests.utils.urlparse(normalized_url)
    host = parsed.hostname
    session = _build_session()

    main_resp, fetch_warning = _fetch(session, normalized_url)
    if not main_resp:
        fix = 'Verify the URL, local firewall rules, or outbound network access. Try scanning http://127.0.0.1:3000 to test the local demo.'
        description = 'Could not connect to target.'
        if fetch_warning:
            description = f'Could not connect to target. Details: {fetch_warning}'
        report.add('Connection', 'High', description, fix, evidence=normalized_url)
        return report.summary()

    if fetch_warning:
        report.add('TLS Warning', 'Medium', fetch_warning, 'Install a valid certificate chain and enable full TLS verification.', evidence=normalized_url)

    targets = _simple_crawl(session, normalized_url, limit=8)

    for target in targets:
        response, target_error = _fetch(session, target)
        if not response:
            if target_error:
                report.add(
                    'Partial Crawl Failure',
                    'Low',
                    f'Could not inspect {target}. Details: {target_error}',
                    'Review server-side blocking rules or scan from a network with outbound access.',
                    evidence=target,
                )
            continue

        text = response.text

        if _check_sql_injection(text):
            report.add(
                'SQL Injection',
                'Critical',
                'Application appears to reflect common SQL injection payloads.',
                'Use parameterized queries and validate all input.',
                evidence=target,
            )

        if _check_xss(text):
            report.add(
                'Cross Site Scripting (XSS)',
                'High',
                'Potential reflected XSS vectors detected.',
                'Sanitize outputs and enable Content Security Policy (CSP).',
                evidence=target,
            )

        if _check_ssrf(text):
            report.add(
                'Server-Side Request Forgery (SSRF)',
                'High',
                'Potential SSRF indicators found in response payload.',
                'Validate and sanitize URL input and restrict outbound requests.',
                evidence=target,
            )

        if _check_rce(text):
            report.add(
                'Remote Code Execution (RCE)',
                'Critical',
                'Response contains indicators common to command execution output.',
                'Avoid evaluating user input and employ strict input validation.',
                evidence=target,
            )

    required_headers = {
        'Content-Security-Policy': 'Define a strict CSP to mitigate JavaScript injection.',
        'X-Frame-Options': 'Prevent clickjacking by setting X-Frame-Options to DENY or SAMEORIGIN.',
        'X-XSS-Protection': 'Enable browser XSS protection filters.',
        'Strict-Transport-Security': 'Enforce HTTPS connections with HSTS.',
    }
    for header_name, remediation in required_headers.items():
        if header_name not in main_resp.headers:
            report.add('Missing Security Header', 'Medium', f'{header_name} header missing.', remediation)

    if host and _port_scan_allowed(host):
        for port in [80, 443, 21, 22, 23, 25, 3306, 8080]:
            try:
                sock = socket.socket()
                sock.settimeout(1)
                sock.connect((host, port))
                report.add(
                    'Open Port',
                    'Low',
                    f'Port {port} is open on host.',
                    'Close unnecessary services and firewall unused ports.',
                    evidence=str(port),
                )
                sock.close()
            except Exception:
                pass

    for path in ['/admin', '/backup', '/config', '/.git/', '/.env']:
        url_to_check = normalized_url.rstrip('/') + path
        r2, _ = _fetch(session, url_to_check)
        if r2 and r2.status_code == 200:
            report.add(
                'Directory Exposure',
                'High',
                f'Accessible content at {path}',
                'Restrict access to sensitive directories and use proper authentication.',
                evidence=url_to_check,
            )

    if normalized_url.startswith('https://') and host:
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=host) as wrapped_socket:
                wrapped_socket.settimeout(3)
                wrapped_socket.connect((host, 443))
                cert = wrapped_socket.getpeercert()
                if not cert:
                    report.add('SSL', 'Critical', 'No TLS certificate detected.', 'Install a valid SSL/TLS certificate.')
        except Exception as exc:
            report.add(
                'SSL',
                'High',
                f'SSL/TLS connection issue: {exc}',
                'Ensure SSL certificate is valid, properly configured, and reachable from the scanning host.',
            )

    return report.summary()
