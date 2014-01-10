#!/bin/csh -f
set i = ` wc -l $1 `
@ i--
tail -$i $1 > jnk1.doc
tail -$i $2 > jnk2.doc
paste jnk1.doc jnk2.doc > jnk3.doc

cat jnk3.doc | awk '{ printf "%7d%8.3f%8.3f%8.3f%8.3f%8.3f%8.1f%6d%9.1f%9.1f%8.2f%7.2f%6.2f\n",$1,$3,$4,$5,$6,$7,$8,$10,$11,$12,$13,$14,$15}'> $3

rm jnk*.doc



