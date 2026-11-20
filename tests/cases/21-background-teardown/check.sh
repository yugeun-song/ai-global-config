if [ ! -f .started ]; then grep -qiE "sandbox|permission|approv|샌드박스|권한|승인" "$2" && exit 77; exit 1; fi
! pgrep -fx "sleep $(cat .id)" >/dev/null
