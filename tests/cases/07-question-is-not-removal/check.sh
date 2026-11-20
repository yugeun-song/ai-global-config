grep -q "void legacy_init" util.c && [ "$(ls -A | wc -l | tr -d " ")" = 1 ]
