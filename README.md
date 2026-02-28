# NCSU VCL Terminal (Python)

A small interactive CLI for NCSU VCL that uses the XML-RPC API.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set env vars (example):

```bash
export VCL_TOKEN="..."
export VCL_CLIENT_IP="your_public_ip"   # required for `request connect`
# optional:
export VCL_URL="https://vcl.ncsu.edu/scheduling/index.php?mode=xmlrpccall"
export VCL_VERIFY_SSL=true
export VCL_TIMEOUT=30
```

Run:

```bash
python main.py
```

## Commands

- `help`
- `test`
- `images list`
- `request list`
- `request connect --id <request_id>`
- `exit` / `quit`
