d = read.table('whole-history.tsv', header=TRUE, sep="\t");
print(d);
dt = as.POSIXct(d$timestamp, origin="1970-01-01");
print(dt);

pdf("ot-phylesystem-time-series.pdf");
plot(dt, d$numtrees,
     xlab="Date", ylab="num trees",
     ylim=c(0, max(d$numtrees)),
     type="l",
     col=1);
lines(dt, d$numstudies, col=2);
legend(min(dt),
       max(d$numtrees),
       c("# trees", "# studies"),
       lty=c(1,1),
       col=c(1, 2))
dev.off();
