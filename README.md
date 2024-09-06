# Ecoflow ntfy.sh Notifier

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

crontab -e
```

```
* * * * * /path/to/ecoflow-ntfy/venv/bin/python /path/to/ecoflow-ntfy/main.py
```
