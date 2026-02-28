# Data Platforms

## Introduction to Bruin

- Original video (in English): [Bruin Tutorial](https://www.youtube.com/watch?v=f6vg7lGqZx0&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=1&feature=youtu.be)

[Bruin](https://getbruin.com) is a data platform that helps manage data processes end to end. It integrates functionalities ranging from ingestion, transformations, and orchestration to data quality checks and metadata management.

## ETL / ELT

Throughout this module, we will work with a project organized into three phases:

1. **Extraction** and data ingestion: from the various data sources in the project,
2. **Transformations**: to adapt the data into a format suitable for analysis,
3. **Loading**: into the environment where users will consume the transformed data.

### Orchestration

To coordinate the processes that make up each of these phases, we will need a tool to help with orchestration. This tool will handle task scheduling and determine the order and concurrency conditions under which tasks are executed.

### Data Governance

From a data perspective, we want strong metadata management that allows us to document our data catalog, as well as a solid data governance policy that documents and enforces compliance with our data quality standards.

## Getting Started with Bruin

- Original video (in English): [Getting Started with Bruin](https://www.youtube.com/watch?v=JJwHKSidX_c&list=PL3MmuxUbc_hJed7dXYoJw8DoCuVHhGEQb&index=3)

### Installation

To work with Bruin, the first step is to install its command-line tool:

```bash
curl -LsSf https://getbruin.com/install/cli | sh
```

Once installation is complete, it is recommended to verify it:

```bash
bruin version
```

Project Creation

In our case, we created the project in the subdirectory pipelines/chess-pipeline/, using bruin init and selecting the default profile:

```bash
mkdir pipelines
cd pipelines

bruin init chess chess-pipeline
```

Project Structure

This creates:

A file chess-pipeline/pipeline.yml with the data flow configuration,

A directory chess-pipeline/assets/ with three example artifacts.

Connections File: .bruin.yml

Additionally, Bruin scans your directory tree for a root .git directory and, if found, adds a .gitignore and a connections configuration file: .bruin.yml.

```yaml
default_environment: default
environments:
  default:
    connections:
      duckdb:
        - name: duckdb-default
          path: duckdb.db
      chess:
        - name: chess-default
          players:
            - MagnusCarlsen
            - Hikaru
```

In our case, since we want to have more than one pipeline in the same directory and ensure each has its own independent connections file, we will move the file into the chess-pipeline/ folder.

From now on, we must reference the connections file whenever running bruin commands using the --config-file attribute:

```bash
In our case, since we want to have more than one pipeline in the same directory and ensure each has its own independent connections file, we will move the file into the chess-pipeline/ folder.

From now on, we must reference the connections file whenever running bruin commands using the --config-file attribute:
```

Data Flows

The pipeline.yml file contains the configuration of our project. In Bruin, a data flow is simply a set of artifacts that are executed in a specific order.

```yaml
name: chess_duckdb
catchup: false
default:
  type: ingestr
  parameters:
    source_connection: chess-default
    destination: duckdb
```

# Artifacts

Artifacts are anything that can be executed as part of our data flows and that ultimately generates some kind of data. In a Bruin project, they live in the `assets/` folder.

For example, the chess project generates three default artifacts:

- `assets/chess_games.asset.yml`
- `assets/chess_profiles.asset.yml`
- `assets/player_summary.sql`

## YAML Artifacts

The first two artifacts describe data sources from which we will read data—in this case, games and players:

```yaml
# chess_games.asset.yml
name: chess_playground.games
parameters:
  source_table: games

# chess_profiles.asset.yml
name: chess_playground.profiles
parameters:
  source_table: profiles
```

SQL Artifacts

The third artifact materializes "on the fly" a table that allows us to analytically consume information about games and players. The file begins with a declarative section where we specify the artifact’s dependencies, columns, and other properties.

```sql
/* @bruin

name: chess_playground.player_summary
type: duckdb.sql
materialization:
   type: table

depends:
   - chess_playground.games
   - chess_playground.profiles

columns:
  - name: total_games
    type: integer
    description: "the games"
    checks:
      - name: positive

@bruin */
```

It continues with the query that transforms game and player data into a summary ready for analysis.

```sql

WITH game_results AS (
    SELECT
        CASE
            WHEN g.white->>'result' = 'win' THEN g.white->>'@id'
            WHEN g.black->>'result' = 'win' THEN g.black->>'@id'
            ELSE NULL
            END AS winner_aid,
        g.white->>'@id' AS white_aid,
        g.black->>'@id' AS black_aid
    FROM chess_playground.games g
)

SELECT
    p.username,
    p.aid,
    COUNT(*) AS total_games,
    COUNT(CASE WHEN g.white_aid = p.aid AND g.winner_aid = p.aid THEN 1 END) AS white_wins,
    COUNT(CASE WHEN g.black_aid = p.aid AND g.winner_aid = p.aid THEN 1 END) AS black_wins,
    COUNT(CASE WHEN g.white_aid = p.aid THEN 1 END) AS white_games,
    COUNT(CASE WHEN g.black_aid = p.aid THEN 1 END) AS black_games,
    ROUND(COUNT(CASE WHEN g.white_aid = p.aid AND g.winner_aid = p.aid THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN g.white_aid = p.aid THEN 1 END), 0), 2) AS white_win_rate,
    ROUND(COUNT(CASE WHEN g.black_aid = p.aid AND g.winner_aid = p.aid THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN g.black_aid = p.aid THEN 1 END), 0), 2) AS black_win_rate
FROM chess_playground.profiles p
LEFT JOIN game_results g
       ON p.aid IN (g.white_aid, g.black_aid)
GROUP BY p.username, p.aid
ORDER BY total_games DESC

```

Data Materialization

To ask Bruin to materialize these queries into the DuckDB database we configured, we can use:

```bash
bruin run --config-file .bruin.yml
```
