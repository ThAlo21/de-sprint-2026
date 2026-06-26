# Insight Vault

## Spark / RDDs (Berkeley, 2012)
- **Problem solved:** MapReduce wrote intermediate results to disk between every step making iterative workloads extremely slow. RDDs keep data in memory across transformations.
- **Core idea:** Distributed immutable partitions processed in memory across a cluster.
- **Trade-off:** RAM consumption — if data doesn't fit in memory Spark spills to disk and performance degrades.
- **Clever mechanism:** Lineage DAG — instead of materializing every transformation Spark records how to recompute lost partitions, achieving fault tolerance without disk writes.
- **Applicable to my work:** Replaces psycopg2-based ingestion when data volume outgrows single-machine Python. Sprint 3 will rewrite the taxi ingestion as a Spark job.
- **One thing to use today:** Iterative processing workloads where MapReduce would pay full disk I/O cost on every iteration.

## code issues and decision making

### The 5 bugs found in the broken job
- **driver.memory = 512m :**OOM on large datasets .
- **shuffle.partitions = 1:**No parallelism, 47min runtime .
- **.collect() + createDataFrame() :**OOM killer, destroys parallelism .
- **repartition(1) :** Forces single partition output .
- **write.mode("append") :** Row count mismatch on reruns .


### Why .collect() is an OOM killer ?
- **.collect() pulls the entire dataset from the distributed cluster into the driver's memory as a Python list. On 3 months of data it barely fits. On 12 months it crashes. That's your OOM — symptom 1. 



### Why operation order matters in cleaning pipelines ?
- **Filter, deduplication, Null removing all will remove rows so of ordered different may lead to mismatch or incorrect data sometimes .   


### Partitioning decision and reasoning
- **Best practice is to make each file on partitioning never exceed 1 Gb .
- **Best way that data organized in , and never effected the business is  to partition based on day .
- **That will result 32 files with bearable size .

