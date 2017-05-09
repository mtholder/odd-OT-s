#!/usr/bin/env python
from __future__ import print_function
from subprocess import check_output
import datetime
from peyotl import read_as_json
from peyotl.nexson_syntax import extract_tree_nexson
import re

import sys
import os

def debug(m):
    sys.stderr.write("{}\n".format(m))
"""
prev_ns=0
prev_trees=0
stfile=".checkedout-num-studies-and-trees.txt"
resultsfile="timestamps-num_studies-num_trees.csv"
echo "timestamp,numstudies,numtrees,SHA" > "${resultsfile}"
for sha in $(cat ${shasfile})
do
    unix_time=$(git show -s --format=%at "${sha}")
    git checkout $sha || exit
    python -c "from peyotl import Phylesystem; p = Phylesystem(); import sys; t = p.get_study_tree_counts() ; sys.stdout.write('{}\\n{}\\n'.format(t[0], t[1]))" > "${stfile}" || exit
    num_studies=$(head -n1 "${stfile}")
    num_trees=$(tail -n1 "${stfile}")
    if test $num_studies -ne $prev_ns -o $num_trees -ne $prev_trees
    then
        echo "${unix_time},${num_studies},${num_trees},${sha}" >> "${resultsfile}"
    fi
    prev_ns=$num_studies
    prev_trees=$num_trees
done

"""

git_dir, commits_sha_file = sys.argv[1:]

study_dir = os.path.join(git_dir, 'study')
study_fn_pat = re.compile(r"[a-z][a-z]_\d+[.]json")

commits_shas = [i.strip() for i in open(commits_sha_file, 'r') if i.strip()]
mentioned_sha_set = frozenset(commits_shas)
debug("getting parents for shas")
sha2par = {}
for sha in commits_shas:
    x = check_output(['git', "rev-list", "--parents", "-n", "1", sha]).strip().split()
    if not len(x):
        raise RuntimeError("error with rev-list for {}".format(sha))
    assert x[0] == sha
    sha2par[sha] = x[1:]
    for p in x[1:]:
        if p not in sha2par:
            sha2par[p] = []

parentless = [k for k, v in sha2par.items() if not v]
root_commits = frozenset(parentless)

READ_ROOTS = True

sha_full_info = {}

if READ_ROOTS:
    debug("start points: {}".format(parentless))

    for p in parentless:
        check_output(["git", "checkout", p])
        fn2nt = {}
        for root, dirs, files in os.walk(study_dir):
            study_fn = [i for i in files if study_fn_pat.match(i)]
            for fn in study_fn:
                fp = os.path.join(root, fn)
                #debug('fp={}'.format(fp))
                if fn in fn2nt:
                    continue
                nexson = read_as_json(fp)
                tn = extract_tree_nexson(nexson, tree_id=None)
                fn2nt[fn] = len(tn)
        sha_full_info[p] = fn2nt

def study_changes_from_delta_list(delta_list):
    ch = []
    for el in delta_list:
        if not el:
            continue
        #debug('el = "{}"'.format(el))
        assert el.startswith('A\t') or el.startswith('M\t') or el.startswith('D\t')
        action = el[0]
        path = el[2:]
        #debug('path={}'.format(path))
        if path.startswith('study'):
            fn = os.path.split(path)[-1]
            #debug('fn={}'.format(fn))
            if study_fn_pat.match(fn):
                ch.append((action, path))
    #debug('ch = {}'.format(ch))
    return ch

def count_studies_and_tree(fn2nt):
    num_studies = 0
    num_trees = 0
    for k, vi in fn2nt.items():
        if vi is not None:
            num_studies += 1
            num_trees += vi
    return num_studies, num_trees

curr_round = dict(sha2par)
for el in root_commits:
    del curr_round[el]
    if not READ_ROOTS:
        sha_full_info[el] = {}

while curr_round:
    next_round = {}
    num_todo = len(curr_round)
    debug("...working through commits. {} to go...".format(len(curr_round)))
    for sha, par_list in curr_round.items():
        ref_par = None
        for p in par_list:
            if p in sha_full_info:
                ref_par = p
                break
        if ref_par is None:
            next_round[sha] = par_list
        else:
            debug('looking at diff for {}'.format(sha))
            fn_stat = check_output(["git", "diff", "--name-status", ref_par, sha]).split('\n')
            #debug((ref_par, sha, fn_stat))
            study_changes = study_changes_from_delta_list(fn_stat)
            if study_changes:
                fn2nt = dict(sha_full_info[ref_par])
                non_del = []
                deleted = []
                for action, path in study_changes:
                    if action == 'D':
                        deleted.append(path)
                    else:
                        non_del.append(path)
                if non_del:
                    check_output(["git", "checkout", sha])
                    for fp in non_del:
                        fn = os.path.split(fp)[-1]
                        nexson = read_as_json(fp)
                        tn = extract_tree_nexson(nexson, tree_id=None)
                        #debug('tn went from {} to {}'.format(fn2nt.get(fn, 'NULL'), len(tn)))
                        fn2nt[fn] = len(tn)
                for fp in deleted:
                    fn = os.path.split(fp)[-1]
                    if READ_ROOTS and fn not in fn2nt:
                        continue
                    else:
                        assert fn in fn2nt
                    del fn2nt[fn]
            else:
                fn2nt = sha_full_info[ref_par]
            sha_full_info[sha] = fn2nt
    curr_round = next_round



out_sorted = []

for k, d in sha_full_info.items():
    timestamp = int(check_output(["git", "show", "-s", "--format=%at", k]).strip())
    dtobj = datetime.datetime.fromtimestamp(timestamp)
    time_for_people = dtobj.strftime("%Y-%m-%dT%HZ")
    num_studies, num_trees = count_studies_and_tree(d)
    out_sorted.append((timestamp, num_studies, num_trees, time_for_people, k))
    if len(out_sorted) % 1000:
        debug('...time stamp obtained for {}/{} commits'.format(len(out_sorted), len(sha_full_info)))

out_sorted.sort()

out = sys.stdout
out.write('{}\n'.format('\t'.join(["timestamp", "numstudies", "numtrees", "time", "sha"])))
for rec in out_sorted:
    out.write('{}\n'.format('\t'.join([str(i) for i in rec])))