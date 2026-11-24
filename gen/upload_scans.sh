#!/bin/bash
# Upload the block images (scans/<book>/*.jpg, made by gen/chaya_crops.py) and the books they come from
# (<book>.chaya.pdf, made with scan-test) to the site's R2 bucket, which serves them at the URL in gen/chaya.py
# (SCANS). Needs wrangler 4 (WRANGLER=path, else the one on the PATH), logged in to the Cloudflare account (wrangler
# login). Each file uploaded is noted in
# scans/uploaded.txt, and a run skips those: run it again to finish an interrupted upload, or after adding images.
#
#   gen/upload_scans.sh BUCKET [BOOK=PATH.chaya.pdf ...]
#   e.g. gen/upload_scans.sh bhartrhari-scans telang=~/w/scan-test/outputs/books/telang-dli.chaya.pdf
set -euo pipefail
cd "$(dirname "$0")/.."
bucket=$1; shift
WRANGLER=${WRANGLER:-wrangler}
touch scans/uploaded.txt
upload() {   # key file content-type
  "$WRANGLER" r2 object put "$bucket/$1" --remote --file "$2" --content-type "$3" > /dev/null 2>&1 && echo "$1" >> scans/uploaded.txt || echo "FAILED $1" >&2
}
export -f upload
export bucket WRANGLER
for spec in "$@"; do
  book=${spec%%=*}; file=${spec#*=}
  grep -qx "books/$book.chaya.pdf" scans/uploaded.txt || upload "books/$book.chaya.pdf" "$file" application/pdf
done
find scans -mindepth 2 -name '*.jpg' | sed 's|^scans/||' | sort | comm -23 - <(sort scans/uploaded.txt) \
  | xargs -P 8 -I{} bash -c 'upload "$1" "scans/$1" image/jpeg' _ {}
echo "$(wc -l < scans/uploaded.txt) files uploaded in all"
