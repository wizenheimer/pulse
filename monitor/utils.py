import requests
import ssl
import socket
import datetime


def test_uptime(url, timeout=None):
    """
    Returns the status code and message
    """
    result = {}
    if timeout is None or timeout < 0:
        timeout = 5

    try:
        response = requests.get(url, timeout=timeout)
        result["status_code"] = response.status_code
        result["log"] = response.reason
    except requests.Timeout:
        result["status_code"] = 408
        result["log"] = "The server timed out waiting for the request from the client."
    except requests.ConnectionError:
        result["status_code"] = 503
        result[
            "log"
        ] = "The server is currently unable to handle the request due to a temporary overload or maintenance"
    finally:
        return result


def test_ssl(domain):
    """
    ("1.1.1.1") -> [..., "..."]
    """
    result = {}
    try:
        # Connect to the website using SSL
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                # Retrieve SSL certificate information
                cert = ssock.getpeercert()

                # Extract expiry date from certificate
                expiry_date = datetime.datetime.strptime(
                    cert["notAfter"], "%b %d %H:%M:%S %Y %Z"
                )
                current_date = datetime.datetime.now()

                # Compare expiry date with current date
                if expiry_date < current_date:
                    result["status_code"] = 403
                    result["log"] = f"The SSL certificate for {domain} has expired."
                else:
                    result["status_code"] = 200
                    result[
                        "log"
                    ] = f"The SSL certificate for {domain} is still valid until {expiry_date}."
    except ssl.SSLError as e:
        result["status_code"] = -1
        result["log"] = f"Error: Failed to establish SSL connection to {domain}"
    except socket.error as e:
        result["status_code"] = 404
        result["log"] = f"Error: Failed to connect to {domain}"
    except Exception as e:
        result["status_code"] = 401
        result["log"] = f"Invalid SSL certificate. Error: {e}"
    finally:
        return result


def test_port(url, port):
    """
    ("1.1.1.1", 2000) -> [400, "Port 2000 is closed on 1.1.1.1"]
    """
    if port is None:
        port = 0000
    result = {}
    try:
        # Attempt to connect to the specified port
        host = str(socket.gethostbyname(url))
        with socket.create_connection((host, port), timeout=3) as sock:
            result["status_code"] = 200
            result["log"] = f"Port {port} is open on {host}"
    except (ConnectionRefusedError, socket.timeout):
        result["status_code"] = 400
        result["log"] = f"Port {port} is closed on {host}"
    except Exception as e:
        result["status_code"] = 500
        result["log"] = f"Port {port} can't be reached."
    finally:
        return result


def test_website_speed(url, timeout=None):
    """Test website speed"""
    result = {}
    if timeout is None or timeout < 0:
        timeout = 5
    try:
        # Send a GET request and measure response time
        response = requests.get(url, timeout=timeout)
        response_time = response.elapsed.total_seconds()

        # Print the response time in milliseconds
        result["status_code"] = 200
        result["log"] = f"Response time for {url}: {response_time:.2f} seconds"
        result["response_time"] = response_time

    except requests.Timeout:
        result["status_code"] = 408
        result["log"] = "The server timed out waiting for the request from the client."
        result["response_time"] = -1

    except requests.ConnectionError:
        result["status_code"] = 503
        result[
            "log"
        ] = "The server is currently unable to handle the request due to a temporary overload or maintenance."
        result["response_time"] = -1

    except requests.exceptions.RequestException as e:
        result["status_code"] = 400
        result["log"] = f"Response time for {url}: inf seconds"
        result["response_time"] = -1

    finally:
        return result
