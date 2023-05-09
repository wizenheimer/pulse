import requests


def unshorten_url(url, timeout=30):
    return requests.head(url, allow_redirects=True, timeout=timeout).url


def handle_url(url, timeout=30):
    parent_url = None
    message = "URL is accepted for making requests."
    try:
        parent_url = unshorten_url(url, timeout=timeout)
    except requests.exceptions.Timeout:
        # Maybe set up for a retry, or continue in a retry loop
        message = "Request timed out. Try exceeding the timeout limit."
    except requests.exceptions.TooManyRedirects:
        # Tell the user their URL was bad and try a different one
        message = "Request exceeds the configured number of maximum redirections. Try a different URL."
    except requests.exceptions.ConnectionError:
        # Network problem (DNS failure, refused connection, etc)
        message = "Request couldn't be fulfilled. URL connection refused."
    except requests.exceptions.HTTPError:
        # Invalid HTTP response or regular unsuccesful
        message = "HTTP response is invalid. Please try with a different URL."
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        message = "Request couldn't be fulfilled. URL connection refused."
    # prepare a context object
    context = {
        "url": parent_url,
        "message": message,
    }
    return context
