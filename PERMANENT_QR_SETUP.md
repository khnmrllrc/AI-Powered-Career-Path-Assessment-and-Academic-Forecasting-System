# Permanent QR Code Setup

This guide configures student QR codes to use a permanent HTTPS address instead of `localhost`, a private LAN IP, or a temporary `trycloudflare.com` URL.

## How it works

The QR code opens a public URL like:

```text
https://career.example.com/student/<student-qr-code>/results/
```

Cloudflare Tunnel forwards that public URL to the local Django server at `http://localhost:8000`.

## Requirements

- A domain name, such as `example.com`.
- A free Cloudflare account.
- The domain added to Cloudflare DNS.
- Django running on port `8000`.
- `cloudflared.exe` available on Windows.

Cloudflare documentation: [Set up Cloudflare Tunnel](https://developers.cloudflare.com/tunnel/get-started/)

## 1. Start Django locally

Open PowerShell in the project root:

```powershell
cd "C:\Users\servano\Desktop\AI-Powered-Career-Path-Assessment-and-Academic-Forecasting-System"
.\venv\Scripts\python.exe .\careerpath\manage.py runserver 0.0.0.0:8000
```

Confirm that this works on the computer:

```text
http://localhost:8000/
```

## 2. Create a Cloudflare Named Tunnel

1. Open the Cloudflare dashboard.
2. Go to **Networking > Tunnels**.
3. Select **Create Tunnel**.
4. Name it, for example, `careerpath-production`.
5. Select the Windows connector option.
6. Copy the tunnel token shown by Cloudflare.

Named tunnels provide a stable identity and hostname. Quick tunnels do not; their URLs change when the process stops.

## 3. Add a permanent public hostname

In the tunnel configuration, add a **Published application**:

| Setting | Value |
|---|---|
| Hostname | `career.example.com` |
| Service type | `HTTP` |
| Service URL | `http://localhost:8000` |

Use your real domain instead of `example.com`.

Cloudflare will create the DNS route for the hostname. The final public URL should be:

```text
https://career.example.com/
```

## 4. Install the tunnel as a Windows service

Open **Command Prompt as Administrator** and run:

```cmd
cd C:\path\to\cloudflared
cloudflared.exe service install YOUR_TUNNEL_TOKEN
```

Replace `YOUR_TUNNEL_TOKEN` with the token from Cloudflare. The service starts automatically with Windows and reconnects when the network is restored.

Cloudflare documentation: [Run Cloudflare Tunnel as a service](https://developers.cloudflare.com/tunnel/features/locally-managed-tunnels/as-a-service/)

## 5. Configure Django to use the permanent URL

The project already reads `QR_PUBLIC_BASE_URL` in [settings.py](careerpath/careerpath/settings.py).

For the current PowerShell session:

```powershell
$env:QR_PUBLIC_BASE_URL = "https://career.example.com"
.\venv\Scripts\python.exe .\careerpath\manage.py runserver 0.0.0.0:8000
```

Do not include a trailing slash. The application adds the results path automatically.

For a permanent Windows environment variable, run PowerShell as your user and execute:

```powershell
[Environment]::SetEnvironmentVariable(
    "QR_PUBLIC_BASE_URL",
    "https://career.example.com",
    "User"
)
```

Close and reopen PowerShell after setting the variable, then restart Django.

## 6. Verify the public site

Open this URL from a phone using mobile data or another network:

```text
https://career.example.com/
```

If it loads, the public route is working.

## 7. Generate a new QR code

1. Open `https://career.example.com/`.
2. Log in as the student.
3. Open **QR Profile**.
4. Generate or display the QR code again.
5. Scan it with a phone.
6. Confirm that the student assessment results page opens.

The QR destination format is:

```text
https://career.example.com/student/<uuid>/results/
```

## Troubleshooting

### The QR opens `localhost` or `192.168.x.x`

Django was started without `QR_PUBLIC_BASE_URL`. Set the variable, restart Django, and generate the QR code again.

### The public domain does not open

Check that:

- The Cloudflare service is running.
- The tunnel hostname points to `http://localhost:8000`.
- Django is running on port `8000`.
- The domain DNS is managed by Cloudflare.
- Windows Firewall is not blocking `cloudflared`.

### The page opens but says results are unavailable

The QR route is working, but the student may not have completed an assessment yet. Complete the assessment first.

### Existing QR codes still use the old URL

Open the QR Profile page again after configuring `QR_PUBLIC_BASE_URL`. QR images are generated on demand with the current public URL.

### Temporary tunnel warning

This command is temporary and should not be used for permanent QR codes:

```powershell
cloudflared tunnel --url http://localhost:8000
```

Use a Named Tunnel with your own domain instead.
