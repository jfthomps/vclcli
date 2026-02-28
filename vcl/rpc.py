import os
import xmlrpc.client
import requests

DEFAULT_VCL_URL = "https://vcl.ncsu.edu/scheduling/index.php?mode=xmlrpccall"


class VCLRPCError(RuntimeError):
    pass


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "y", "on")


def _get_headers(token: str) -> dict:
    return {
        "Content-Type": "text/xml",
        "X-Authorization": f"Bearer {token}",
        "X-APIVERSION": "2",
    }


def call(method: str, args=None, *, url=None, token=None, timeout=30):
    """
    Call a VCL XML-RPC method.

    Env vars:
      - VCL_TOKEN (required)
      - VCL_URL (optional)
      - VCL_VERIFY_SSL (optional, default true)
      - VCL_TIMEOUT (optional, default 30)
    """
    if args is None:
        args = []

    if url is None:
        url = os.getenv("VCL_URL", DEFAULT_VCL_URL)

    if token is None:
        token = os.getenv("VCL_TOKEN")

    if not token:
        raise VCLRPCError("Missing VCL_TOKEN in environment")

    try:
        timeout = int(os.getenv("VCL_TIMEOUT", str(timeout)))
    except ValueError:
        pass

    verify = _env_bool("VCL_VERIFY_SSL", True)
    body = xmlrpc.client.dumps(tuple(args), methodname=method)
    headers = _get_headers(token)

    try:
        r = requests.post(url, headers=headers, data=body, timeout=timeout, verify=verify)
    except requests.RequestException as e:
        raise VCLRPCError(f"Network error calling VCL: {e}") from e

    if r.status_code != 200:
        snippet = (r.text or "").strip().replace("\n", " ")[:200]
        raise VCLRPCError(f"HTTP {r.status_code} from VCL: {snippet}")

    try:
        data, _ = xmlrpc.client.loads(r.content)
        return data[0]
    except Exception as e:
        raise VCLRPCError(f"Failed to parse XML-RPC response: {e}") from e
