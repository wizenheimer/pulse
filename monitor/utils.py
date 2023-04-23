import requests
import ssl
import socket
import datetime

def test_uptime(url, timeout=None):
    '''
        Returns the status code and message
    '''
    if timeout is None or timeout < 0:
        timeout = 5
    
    try:
        response = requests.get(url, timeout=timeout)
        return [response.status_code, response.reason]
    except requests.Timeout:
        return [408, "The server timed out waiting for the request from the client."]
    except requests.ConnectionError:
        return [503, "The server is currently unable to handle the request due to a temporary overload or maintenance."]
    
def test_ssl(domain):
    """
    ("1.1.1.1") -> [..., "..."]
    """
    try:
        # Connect to the website using SSL
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443)) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                # Retrieve SSL certificate information
                cert = ssock.getpeercert()

                # Extract expiry date from certificate
                expiry_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                current_date = datetime.datetime.now()

                # Compare expiry date with current date
                if expiry_date < current_date:
                    return [403, f"The SSL certificate for {domain} has expired."]
                else:
                    return [200, f"The SSL certificate for {domain} is still valid until {expiry_date}."]
    except ssl.SSLError as e:
        return [-1, f"Error: Failed to establish SSL connection to {domain}"]
    except socket.error as e:
        return [404, f"Error: Failed to connect to {domain}"]
    except Exception as e:
        return [401, f"Invalid SSL certificate. Error: {e}"]

def test_port(host, port):
    """
    ("1.1.1.1", 2000) -> [400, "Port 2000 is closed on 1.1.1.1"]
    """
    try:
        # Attempt to connect to the specified port
        with socket.create_connection((host, port), timeout=3) as sock:
            return [200, f"Port {port} is open on {host}"]
    except (ConnectionRefusedError, socket.timeout):
        return [400, f"Port {port} is closed on {host}"]
    except Exception as e:
        return [-1, f"Error: {e}"]
    
def test_website_speed(url, timeout=None):
    """Test website speed"""
    if timeout is None or timeout < 0:
        timeout = 5
    try:
        # Send a GET request and measure response time
        response = requests.get(url, timeout=timeout)
        response_time = response.elapsed.total_seconds()

        # Print the response time in milliseconds
        return [200, f"Response time for {url}: {response_time:.2f} seconds"]
    except requests.Timeout:
        return [408, "The server timed out waiting for the request from the client."]
    except requests.ConnectionError:
        return [503, "The server is currently unable to handle the request due to a temporary overload or maintenance."]
    except requests.exceptions.RequestException as e:
        return [400, f"Response time for {url}: inf seconds"]