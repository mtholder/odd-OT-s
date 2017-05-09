import sys
inp, out = sys.stdin, sys.stdout
prevs, prevt = None, None
for line in inp:
    ls = line.strip()
    lss = ls.split('\t')
    if prevt is None or prevt != lss[2] or prevs != lss[1]:
        out.write(line)
        prevt = lss[2]
        prevs = lss[1]
