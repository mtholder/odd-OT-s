#!/bin/bash
startsha=$1
shasfile=".relevant-commits-in-chronological-order.txt"
if test -z "${startsha}"; 
then 
    git rev-list --reverse HEAD > "${shasfile}" || exit
else
    echo "${startsha}" > "${shasfile}" || exit
    git rev-list --reverse "${startsha}..HEAD" >> "${shasfile}" || exit
fi

csvfile=study-tree-by-sha.tsv
python report-on-studies-trees-stats.py . "${shasfile}" > "${csvfile}" || exit
uniqf=num-altering-study-tree-by-sha.tsv
cat "${csvfile}" | python uniq-num-studies-or-trees.py > "${uniqf}"
Rscript plot-ot-ts.R