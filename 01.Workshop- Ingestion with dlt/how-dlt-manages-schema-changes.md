# Workshop: **Ingesting Data from an API with DLT**

> [!NOTE]  
> This question has already been submitted as a contribution to the course FAQ:  
> [How does dlt handle schema evolution?](https://github.com/DataTalksClub/faq/issues/202)

---

## FAQ Contribution: **How Does dlt Handle Schema Evolution?**

The good news is that dlt automatically detects and adapts to most schema changes during ingestion, so you typically don’t need to manually modify destination tables.

### What Happens When the Source Schema Changes?

- If **new columns appear**, dlt adds them to the destination table.
- If **new nested fields appear**, dlt creates the necessary child tables or columns.
- If **existing columns disappear**, they remain in the table (they are not deleted).
- If **existing columns change their data type**, dlt attempts a safe type conversion; if that’s not possible, it raises an error so you can handle it explicitly.

### How It Works Internally

dlt infers the schema from incoming data and stores both the schema and the pipeline state locally (in the `.dlt` folder).

On the next run, it compares the incoming data with the stored schema and applies the required migrations to the destination.

### Why This Is Useful in the Course

- You can ingest evolving APIs or semi-structured JSON without writing DDL.
- Your pipelines continue working even when new fields appear.
- It is safe for incremental loads: schema updates do not require a full reload.

### When You May Need to Intervene

- If a column changes to an incompatible data type.
- If you want to enforce a specific schema or data type.
- If you want to remove or rename columns.

In those cases, you can explicitly define the schema in your dlt resource.
