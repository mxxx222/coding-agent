```bash
# 1. Asenna
cd server && pip3 install -r requirements.txt

# 2. Käynnistä
python3 -m uvicorn api.main:app --reload

# 3. Avaa selaimessa
open http://localhost:8000/api/docs
```

