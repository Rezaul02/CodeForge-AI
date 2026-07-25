import requests
import socket
from urllib.parse import urlparse

def normalize_url(target):
    """Ensure the target has http/https scheme."""
    if not target.startswith(("http://", "https://")):
        target = "https://" + target
    return target


def get_http_headers(target_url):
    """Check HTTP headers for common security misconfigurations."""
    try:
        response = requests.get(target_url, timeout=10)
        headers = response.headers

        security_headers = {
            "X-Frame-Options": headers.get("X-Frame-Options", "Missing"),
            "Content-Security-Policy": headers.get("Content-Security-Policy", "Missing"),
            "Strict-Transport-Security": headers.get("Strict-Transport-Security", "Missing"),
            "X-Content-Type-Options": headers.get("X-Content-Type-Options", "Missing"),
            "Server": headers.get("Server", "Missing"),
            "X-Powered-By": headers.get("X-Powered-By", "Missing")
        }

        print("[+] Security Headers Analysis:")
        for header, value in security_headers.items():
            print(f"    {header}: {value}")

        return security_headers

    except requests.exceptions.RequestException as e:
        print(f"[-] Error fetching headers: {e}")
        return None


def check_http_methods(target_url):
    """Check which HTTP methods are allowed by the server."""
    try:
        response = requests.options(target_url, timeout=10)
        allow_header = response.headers.get("Allow", "")
        allowed_methods = [m.strip() for m in allow_header.split(",") if m.strip()]

        print("[+] HTTP Method Testing:")
        if not allowed_methods:
            print("    No methods listed in Allow header")
        else:
            print(f"    Allowed Methods: {', '.join(allowed_methods)}")

        findings = []

        if "TRACE" in allowed_methods:
            findings.append("TRACE method enabled (potential XST risk)")
        if "TRACK" in allowed_methods:
            findings.append("TRACK method enabled")
        if "PUT" in allowed_methods:
            findings.append("PUT method enabled")
        if "DELETE" in allowed_methods:
            findings.append("DELETE method enabled")
        if "OPTIONS" in allowed_methods:
            findings.append("OPTIONS method enabled")

        return allowed_methods, findings

    except requests.exceptions.RequestException as e:
        print(f"[-] HTTP method check failed: {e}")
        return [], [f"HTTP method check failed: {e}"]


def check_port_scan(target_host, ports=None):
    """Perform basic port scan on selected ports and return open ports."""
    if ports is None:
        ports = [22, 80, 443, 8080]

    print("[+] Port Scanning (non-intrusive):")
    open_ports = []

    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        try:
            result = sock.connect_ex((target_host, port))
            if result == 0:
                print(f"    Port {port}: Open")
                open_ports.append(port)
            else:
                print(f"    Port {port}: Closed/Filtered")
        except socket.error as e:
            print(f"    Port {port}: Error ({e})")
        finally:
            sock.close()

    return open_ports


def test_xss_vulnerability(target_url):
    """Very basic reflected XSS check using common payloads."""
    xss_payloads = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>"
    ]

    print("[+] XSS Vulnerability Testing (basic reflection check):")

    for payload in xss_payloads:
        try:
            response = requests.get(target_url, params={"q": payload}, timeout=10)

            # Basic reflection check only
            if payload in response.text:
                print(f"    Potential reflected XSS indicator found with payload: {payload}")
                return True, f"Potential reflected XSS indicator with payload: {payload}"

        except requests.exceptions.RequestException:
            continue

    print("    No obvious XSS vulnerability detected with tested payloads")
    return False, "No obvious reflected XSS detected in basic test"


def check_sql_injection(target_url):
    """Very basic SQL injection error pattern check."""
    sqli_payloads = ["'", "1=1", "' OR '1'='1"]

    print("[+] SQL Injection Testing (basic error-based check):")

    error_signatures = [
        "sql syntax",
        "mysql",
        "warning: mysql",
        "unclosed quotation mark",
        "syntax error",
        "odbc",
        "pdoexception",
        "database error"
    ]

    for payload in sqli_payloads:
        try:
            response = requests.get(target_url, params={"id": payload}, timeout=10)
            response_text = response.text.lower()

            if any(sig in response_text for sig in error_signatures):
                print(f"    Potential SQL injection error indicator found with payload: {payload}")
                return True, f"Potential SQL error indicator with payload: {payload}"

        except requests.exceptions.RequestException:
            continue

    print("    No obvious SQL injection errors detected with tested payloads")
    return False, "No obvious SQL error-based issue detected in basic test"


def generate_report(target_url, headers, allowed_methods, open_ports, vulnerabilities, xss_result, sqli_result):
    """Generate final report summary."""
    print("\n[!] Final Report Summary")
    print(f"Target URL: {target_url}")

    if headers:
        missing_headers = [header for header, value in headers.items() if value == "Missing"]
        if missing_headers:
            print("Security Headers Status: Incomplete")
            print("Missing Security Headers:")
            for h in missing_headers:
                print(f"  - {h}")
        else:
            print("Security Headers Status: Complete")
    else:
        print("Security Headers Status: Could not determine")

    print(f"Allowed HTTP Methods: {', '.join(allowed_methods) if allowed_methods else 'Not available'}")
    print(f"Open Ports Found: {open_ports if open_ports else 'None'}")
    print(f"XSS Test Result: {xss_result}")
    print(f"SQLi Test Result: {sqli_result}")

    if vulnerabilities:
        print("Findings / Potential Issues:")
        for item in vulnerabilities:
            print(f"  - {item}")
    else:
        print("Findings / Potential Issues: None detected in this basic scan")


def main():
    target = input("Enter target URL [https://apex4u.com/]: ").strip() or "https://apex4u.com/"
    target = normalize_url(target)

    parsed = urlparse(target)
    target_host = parsed.hostname

    if not target_host:
        print("[-] Invalid target URL.")
        return

    print("[!] Starting security assessment...")
    print("[!] Use only on systems you own or are authorized to test.\n")

    headers = get_http_headers(target)
    allowed_methods, method_findings = check_http_methods(target)
    open_ports = check_port_scan(target_host)
    xss_found, xss_result = test_xss_vulnerability(target)
    sqli_found, sqli_result = check_sql_injection(target)

    vulnerabilities = []

    if headers:
        missing_headers = [header for header, value in headers.items() if value == "Missing"]
        if missing_headers:
            vulnerabilities.append("Missing security headers: " + ", ".join(missing_headers))

        if headers.get("X-Powered-By") != "Missing":
            vulnerabilities.append(f"X-Powered-By header exposed: {headers.get('X-Powered-By')}")

        # Optional: if Server header exists, mention it as information disclosure
        if headers.get("Server") != "Missing":
            vulnerabilities.append(f"Server header exposed: {headers.get('Server')}")

    vulnerabilities.extend(method_findings)

    if xss_found:
        vulnerabilities.append(xss_result)

    if sqli_found:
        vulnerabilities.append(sqli_result)

    generate_report(
        target_url=target,
        headers=headers,
        allowed_methods=allowed_methods,
        open_ports=open_ports,
        vulnerabilities=vulnerabilities,
        xss_result=xss_result,
        sqli_result=sqli_result
    )


if __name__ == "__main__":
    main()