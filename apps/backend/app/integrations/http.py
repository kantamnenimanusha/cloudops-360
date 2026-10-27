import httpx


def make_client():
    return httpx.Client(timeout=httpx.Timeout(6.0, connect=3.0))


client_factory = make_client  # tests replace this with a MockTransport-backed client


def get_json(url, params=None, auth=None, headers=None):
    with client_factory() as c:
        r = c.get(url, params=params, auth=auth, headers=headers)
        r.raise_for_status()
        return r.json()
