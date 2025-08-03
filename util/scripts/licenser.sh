#!/bin/bash

YEAR=$(date +%Y)
AUTHOR="henn1001"
HEADER_FILE="apache_header.txt"

# Temporary license block (template for prepending)
cat >"$HEADER_FILE" <<EOF
# Copyright $YEAR $AUTHOR
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

EOF

add_or_update_header() {
  FILE="$1"

  if grep -q "Licensed under the Apache License" "$FILE"; then
    echo "Updating year in $FILE"
    # Replace the year in the existing header (only in the first 15 lines)
    awk -v year="$YEAR" -v author="$AUTHOR" '
      NR <= 15 {
        sub(/^# Copyright [0-9]{4}/, "# Copyright " year);
        print;
        next;
      }
      { print }
    ' "$FILE" >"$FILE.tmp" && mv "$FILE.tmp" "$FILE"
  else
    echo "Adding header to $FILE"
    cat "$HEADER_FILE" "$FILE" >"$FILE.tmp" && mv "$FILE.tmp" "$FILE"
  fi
}

export -f add_or_update_header
export HEADER_FILE AUTHOR YEAR

find src -name "*.py" -type f -exec bash -c 'add_or_update_header "$0"' {} \;

rm $HEADER_FILE

echo "Done. Headers added or updated."
