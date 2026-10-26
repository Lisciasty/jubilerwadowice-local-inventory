#!/usr/bin/env python3
"""Generates the Google Merchant Center local inventory file for Jubiler Wadowice.

Reads the already-published Google Shopping product feed (same feed that
already powers PRODUCTS SOURCE 5 in Merchant Center) and re-emits a
store_code/id/availability/price file for the single verified store
location (Business Profile store code: Wadowice1), as required by
Merchant Center's "Dodaj asortyment" (Local inventory ads) step.

The source feed URL is read from the FEED_URL environment variable
(set as a repository secret) rather than hardcoded, since it is an
unlisted URL.
"""

import os
import urllib.request
import xml.etree.ElementTree as ET

FEED_URL = os.environ["FEED_URL"]
STORE_CODE = "Wadowice1"
OUTPUT_FILE = "local_inventory_pl.txt"

NS = {"g": "http://base.google.com/ns/1.0"}


def main():
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "jubilerwadowice-local-inventory-generator"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        tree = ET.parse(resp)

    root = tree.getroot()
    rows = []
    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        product_id = entry.findtext("g:id", namespaces=NS)
        availability = entry.findtext("g:availability", namespaces=NS)
        price = entry.findtext("g:price", namespaces=NS)
        if not product_id or not availability:
            continue
        rows.append((STORE_CODE, product_id.strip(), availability.strip(), (price or "").strip()))

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write("store_code\tid\tavailability\tprice\n")
        for store_code, product_id, availability, price in rows:
            f.write(f"{store_code}\t{product_id}\t{availability}\t{price}\n")

    print(f"Wrote {len(rows)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
