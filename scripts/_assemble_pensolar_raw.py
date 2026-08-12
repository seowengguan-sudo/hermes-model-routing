import os

DATE = "2026-08-11"
RAW = "/opt/data/knowledge/raw/pensolar-%s.md" % DATE

sources = [
    ("SEDA Malaysia - NEM 3.0", "https://www.seda.gov.my/reportal/nem/", "/opt/data/cache/web/www.seda.gov.my-39755019a7.md"),
    ("Trexon - Solar Installation Process Malaysia", "https://trexon.my/installation-process", "/opt/data/cache/web/trexon.my-4cc5a42569.md"),
    ("Ember - Solar and grid flexibility critical for Malaysia", "https://ember-energy.org/latest-insights/solar-and-grid-flexibility-critical-for-malaysia/", "/opt/data/cache/web/ember-energy.org-0c2dc161c9.md"),
    ("Northern Solar - Commercial Solar Setup (inline capture)", "https://northernsolar.com.my/from-roof-to-grid-commercial-solar-setup-in-malaysia/", "/opt/data/cache/web/_inline_northernsolar.md"),
    ("Eigen Energy - Top challenges in solar EPC (inline capture)", "https://www.eigen.energy/articles/top-challenges-solar-epc-projects-how-to-avoid-them", "/opt/data/cache/web/_inline_eigen.md"),
    ("IEA-PVPS - Malaysia 2025 Country Update (inline capture)", "https://iea-pvps.org/about-iea-pvps/members/malaysia/", "/opt/data/cache/web/_inline_ieapvps.md"),
]

parts = ["# PENSOLAR Raw Extracts - %s\n" % DATE]
parts.append("Sources pulled via FREE web_search + web_extract (local research cron). 6 URLs.\n")
for title, url, path in sources:
    parts.append("\n\n========== %s ==========\nSource: %s\n" % (title, url))
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            parts.append(f.read())
    except Exception as e:
        parts.append("[ERROR reading %s: %s]" % (path, e))
with open(RAW, "w", encoding="utf-8") as f:
    f.write("".join(parts))
print("RAW written: %d bytes -> %s" % (os.path.getsize(RAW), RAW))
