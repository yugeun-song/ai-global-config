grep -q "void legacy_init" util.c && [ "$(ls -A | wc -l)" = 1 ]
