## 📄 `README.md` — *Ransomfeed Connector for OpenCTI*

### 🔗 Ransomfeed Connector

Questo **connector custom** per [OpenCTI](https://www.opencti.io/) importa automaticamente i dati sulle **rivendicazioni ransomware pubblicate** dall'API esterna ufficiale di Ransomfeed.it. Ogni rivendicazione viene trasformata in entità STIX compatibili con OpenCTI, arricchendo così l’intelligence sulla minaccia ransomware globale.

---

### 📌 Funzionalità

* Recupero automatico dei dati via API (`GET`).
* Creazione di:

  * `Intrusion Set` (gang ransomware)
  * `Identity` (vittime)
  * `Incident` (attacco)
  * `Indicator` (hash, se disponibile)
* Relazioni tra gli oggetti:

  * `attributed-to`, `targets`, `indicates`
* Supporto per geolocalizzazione tramite campo `country`.

---

### 🧱 Requisiti

* Python ≥ 3.8
* Un’istanza funzionante di OpenCTI (≥ 5.x)
* Accesso a una API che restituisce i dati in formato JSON come:

```json
[
  {
    "id": 1,
    "date": "2025-05-22 14:30:00",
    "victim": "Azienda X",
    "gang": "BlackCat",
    "hash": "abc123...",
    "country": "IT",
    "website": "https://www.azienda.it"
  }
]
```

---

### 🚀 Installazione

#### 1. Clona il repository

```bash
git clone https://github.com/ransomfeed/Ransomfeed_OpenCTI_connector.git
cd Ransomfeed_OpenCTI_connector
```

#### 2. Crea il file `.env` (opzionale)

Puoi anche usare direttamente il `config.yml` se non usi Docker.

---

### ⚙️ Configurazione (`config.yml`)

```yaml
opencti:
  url: "http://localhost:8080"
  token: "YOUR_OPENCTI_TOKEN"

connector:
  id: "ransomfeed-connector"
  type: "EXTERNAL_IMPORT"
  name: "RansomFeed Connector"
  scope: "incident,indicator,identity,intrusion-set"
  interval: 3600  # ogni ora

ransomfeed:
  api_url: "https://api.ransomfeed.it"
```

---

### ▶️ Esecuzione

#### Metodo 1: Avvio manuale

Installa le dipendenze e avvia il connector:

```bash
pip install -r requirements.txt
python connector.py
```

#### Metodo 2: Avvio con Docker

```bash
docker build -t ransomfeed-connector .
docker run --rm ransomfeed-connector
```

---

### 📊 Output in OpenCTI

Per ogni rivendicazione il connector crea:

* Un'entità **`Incident`**
* Una **`Identity`** della vittima
* Una **`Intrusion Set`** per la gang
* (facoltativo) un **`Indicator`** con hash
* Le seguenti **relazioni**:

  * `incident` → `attributed-to` → `gang`
  * `incident` → `targets` → `victim`
  * `gang` → `targets` → `victim`
  * `indicator` → `indicates` → `incident`

---

### 🛡 Licenza

2025 - GNU GPLv3

---

### 📬 Contatti

Sviluppato da Dario Fadda per Ransomfeed.it
📧 Contatto: [dario@ransomfeed.it](mailto:dario@ransomfeed.it)
🔗 [ransomfeed.it](https://ransomfeed.it)
