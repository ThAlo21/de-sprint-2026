# Insight Vault

## Spark / RDDs (Berkeley, 2012)
- **Problem solved:** MapReduce wrote intermediate results to disk between every step making iterative workloads extremely slow. RDDs keep data in memory across transformations.
- **Core idea:** Distributed immutable partitions processed in memory across a cluster.
- **Trade-off:** RAM consumption — if data doesn't fit in memory Spark spills to disk and performance degrades.
- **Clever mechanism:** Lineage DAG — instead of materializing every transformation Spark records how to recompute lost partitions, achieving fault tolerance without disk writes.
- **Applicable to my work:** Replaces psycopg2-based ingestion when data volume outgrows single-machine Python. Sprint 3 will rewrite the taxi ingestion as a Spark job.
- **One thing to use today:** Iterative processing workloads where MapReduce would pay full disk I/O cost on every iteration.