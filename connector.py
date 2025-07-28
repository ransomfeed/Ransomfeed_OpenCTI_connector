import requests
import time
from pycti import OpenCTIConnectorHelper, get_config_variable

class RansomFeedConnector:
    def __init__(self):
        self.helper = OpenCTIConnectorHelper()
        self.api_url = get_config_variable("RANSOMFEED_API_URL", ["ransomfeed", "api_url"])
        self.interval = int(get_config_variable("CONNECTOR_RUN_INTERVAL", ["connector", "interval"], default=3600))

    def get_data(self):
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.helper.log_error(f"Errore nel recupero dati: {e}")
            return []

    def process_claim(self, item):
        self.helper.log_info(f"Processo rivendicazione: {item.get('victim')} da {item.get('gang')}")

        # Vittima (Identity)
        victim = self.helper.api.identity.create(
            type="Organization",
            name=item["victim"],
            description=f"Victim of ransomware group {item['gang']}",
            external_references=[{"source_name": "ransomfeed", "url": item.get("website")}],
            x_opencti_location=self.get_location(item.get("country")),
        )

        # Gruppo ransomware (Intrusion Set)
        group = self.helper.api.intrusion_set.create(
            name=item["gang"],
            description="Ransomware group",
            aliases=[item["gang"]],
            confidence=80
        )

        # Rivendicazione (Incident)
        incident = self.helper.api.incident.create(
            name=f"Ransomware attack on {item['victim']}",
            description=f"Claimed by {item['gang']} on {item['date']}",
            first_seen=item["date"],
            created=item["date"],
            confidence=70
        )

        # Indicator (hash)
        if item.get("hash"):
            indicator = self.helper.api.indicator.create(
                name=f"Hash from attack on {item['victim']}",
                pattern_type="stix",
                pattern=f"[file:hashes.'SHA-256' = '{item['hash']}']",
                confidence=60
            )
            self.helper.api.stix_core_relationship.create(
                relationship_type="indicates",
                source_ref=indicator["id"],
                target_ref=incident["id"]
            )

        # Relazioni
        self.helper.api.stix_core_relationship.create(
            relationship_type="attributed-to",
            source_ref=incident["id"],
            target_ref=group["id"]
        )
        self.helper.api.stix_core_relationship.create(
            relationship_type="targets",
            source_ref=incident["id"],
            target_ref=victim["id"]
        )
        self.helper.api.stix_core_relationship.create(
            relationship_type="targets",
            source_ref=group["id"],
            target_ref=victim["id"]
        )

    def get_location(self, country_code):
        if not country_code:
            return None
        loc = self.helper.api.location.read(filters=[{"key": "x_opencti_aliases", "values": [country_code]}])
        if loc:
            return loc["id"]
        return None

    def run(self):
        self.helper.log_info("Avvio del connector Ransomfeed...")
        while True:
            data = self.get_data()
            for item in data:
                self.process_claim(item)
            self.helper.log_info(f"Attendo {self.interval} secondi prima della prossima esecuzione...")
            time.sleep(self.interval)

if __name__ == "__main__":
    connector = RansomFeedConnector()
    connector.run()
