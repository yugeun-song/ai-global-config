test -s "$3" && python3 -I -c 'import re,sys; sys.exit(0 if re.search("[\uac00-\ud7a3]", open(sys.argv[1], encoding="utf-8").read()) else 1)' "$3" && grep -q "니다" "$3"
