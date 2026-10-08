# SSTI VAPT Lab

A deliberately vulnerable Flask/Jinja2 web application with SQLite for a local/authorized security testing lab.

## Includes
- SQLite database with sample users and notes (generated on first run)
- Normal profile/search functionality
- Intentionally vulnerable SSTI endpoint: `/preview`
- Secure comparison endpoint: `/safe-preview`
- Health endpoint: `/health`
- Database reset endpoint

## Safety
Run only on systems/networks you own or are explicitly authorized to test. Do not expose the vulnerable endpoint to the public Internet.

## Run locally

### Linux/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

### Windows PowerShell
```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## Harmless SSTI validation
Use the vulnerable endpoint:
`/preview?name=World`

Then test the harmless Jinja expression:
`{{7*7}}`

A result of `49` confirms the SSTI behavior. The same input against `/safe-preview?name={{7*7}}` should be displayed as data rather than evaluated.

## Database
The SQLite DB is generated at `data/lab.db` and is intentionally excluded from Git. A fresh clone therefore gets a clean seeded database automatically.

## Suggested VAPT workflow
1. Run and verify the app locally.
2. Confirm SSTI with the harmless expression.
3. Scan with ZAP/Nuclei/Nikto from your VAPT host.
4. Perform only controlled validation in the lab.
5. Install Sophos Endpoint on the Ubuntu test server.
6. Repeat the same controlled validation and compare Sophos Central telemetry.
7. Replace the vulnerable endpoint with the safe implementation and retest.

## Git
```bash
git init
git add .
git commit -m "Initial SSTI VAPT lab"
git branch -M main
git remote add origin <your-repository-url>
git push -u origin main
```

On Ubuntu:
```bash
git clone <your-repository-url>
cd ssti-vapt-lab
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```
