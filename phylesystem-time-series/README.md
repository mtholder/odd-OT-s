# Generating time series stats for phylesystem.
If you were to:
  1. checkout the phylesystem-1 shard
  2. copy all of the scripts to the top of that directory
  3. cd to the top of the directory
  4. run `./trace-num-studies-and-trees.bash`


Then you should be able to generate something like the 
[ot-phylesystem-time-series.pdf](./ot-phylesystem-time-series.pdf)
plot found in this directory.

## Notes/To Do

  1. See https://gist.github.com/mtholder/81a6378d668dc87204515005b36e8c59 for
      how one can scape the release summaries to inject info about
      the number of trees in the synthesis into this sort of script.
      *NOTE* that script would have to be tweaked to deal with the
      different table structure for the output in these scripts.
  2.  This script is slow because it checks out every commit. Could be a lot
      zippier if it used lower level git operations.
  3. rather than make it faster, it probably just needs to process since 
    a start point. Note that `./trace-num-studies-and-trees.bash` can
    take an argument for the SHA to treat as the beginning of the operation.
    By concatenating the data from that run onto the current data, we should
    be able to update frequently.