#!/usr/bin/env bash
# Download the publicly available source documents into corpus/raw/, then index
# them with scripts/ingest_raw.py.
#
#   bash scripts/fetch_sources.sh
#   python3 scripts/ingest_raw.py --replace
#
# corpus/raw/ is gitignored. Only 10 CFR 50.150 and RG 1.217 are US federal
# works in the public domain; NEI and IAEA documents are copyrighted but freely
# downloadable — keep them local. EUR is licensed and is NOT fetched here.
set -uo pipefail
cd "$(dirname "$0")/.."
RAW=corpus/raw
UA="aircraft-impact-rag/1.0"

get() {  # get <SOURCE_ID> <filename> <url>
  local sid="$1" name="$2" url="$3"
  mkdir -p "$RAW/$sid"
  if [ -s "$RAW/$sid/$name" ]; then
    echo "have   $sid/$name"
    return 0
  fi
  echo "fetch  $sid/$name"
  if ! curl -fsSL --retry 3 --retry-delay 2 -A "$UA" -o "$RAW/$sid/$name" "$url"; then
    echo "  FAILED: $url" >&2
    rm -f "$RAW/$sid/$name"
    return 1
  fi
}

# ---- United States (public domain) ----------------------------------------
get US-10CFR50.150 50-150.pdf \
  "https://www.govinfo.gov/content/pkg/CFR-2025-title10-vol1/pdf/CFR-2025-title10-vol1-sec50-150.pdf"
get US-RG-1.217     rg-1-217.html \
  "https://www.govinfo.gov/content/pkg/FR-2011-08-12/html/2011-20513.htm"

# ---- United States (copyrighted, freely downloadable — keep local) --------
get US-NEI-07-13    nei-07-13-rev8p.pdf "https://www.nrc.gov/docs/ML1114/ML111440006.pdf"
get US-NEI-07-13    nei-07-13-rev7.pdf  "https://www.nrc.gov/docs/ML0914/ML091490723.pdf"

# ---- Czech Republic (official texts) --------------------------------------
get CZ-329-2017     329-2017.pdf "https://sujb.gov.cz/fileadmin/sujb/docs/legislativa/vyhlasky/329_2017.pdf"
get CZ-263-2016     263-2016.pdf "https://www.radonovyprogram.cz/fileadmin/radonovyprogram/pdf_doc/zakon_263-2016.pdf"

# ---- IAEA (copyrighted, freely downloadable — keep local) -----------------
get IAEA-SSG-68     ssg-68.pdf  "https://www-pub.iaea.org/MTCD/publications/PDF/PUB1968_web.pdf"
get IAEA-SSG-79     ssg-79.pdf  "https://www-pub.iaea.org/MTCD/Publications/PDF/PUB2036_web.pdf"
get IAEA-SRS-86     srs-86.pdf  "https://www-pub.iaea.org/MTCD/Publications/PDF/P1721_web.pdf"
get IAEA-SRS-87     srs-87.pdf  "https://www-pub.iaea.org/MTCD/Publications/PDF/P1723_web.pdf"

# ---- Europe ---------------------------------------------------------------
get EU-WENRA-SRL    wenra-srl-2020.pdf \
  "https://wenra.eu/sites/default/files/publications/wenra_safety_reference_level_for_existing_reactors_2020.pdf"
get EU-WENRA-SRL    wenra-issue-tu.pdf \
  "https://www.wenra.eu/sites/default/files/publications/wenra_guidance_on_issue_tu_head_document_-2020-06-01.pdf"

cat <<'EOF'

Not fetched automatically:
  EU-EUR       European Utility Requirements Vol. 2 — licensed document,
               obtain from https://europeanutilityrequirements.eu/
  CZ-378-2016  confirm the decree number first (see the to_verify note in
               corpus/clauses/cz_national.yaml)

Next:  python3 scripts/ingest_raw.py --replace
EOF
