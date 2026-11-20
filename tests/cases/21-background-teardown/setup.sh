n=$((RANDOM + 40000)); printf "%s\n" "$n" > .id; printf "#!/bin/sh\ntouch .started\nexec sleep %s\n" "$n" > server.sh; chmod +x server.sh
