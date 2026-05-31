"""Question bank — personalized to Evgenii's real projects and datasets."""

SQL_QUESTIONS = [
    {
        "id": "sql_01", "topic": "GROUP BY + aggregation",
        "question": "Using the Olist dataset, write SQL to find the top 10 product categories by total revenue. Include total revenue, order count, and average order value. Sort by revenue descending.",
        "hint": "GROUP BY category_name, SUM(), COUNT(), AVG(), ORDER BY DESC, LIMIT 10",
        "concepts": ["GROUP BY", "SUM", "COUNT", "AVG", "ORDER BY DESC", "LIMIT"],
    },
    {
        "id": "sql_02", "topic": "Window functions — ROW_NUMBER",
        "question": "In the Uber driver dataset, use a window function to rank trips by earnings per hour within each trip type. Show the top 3 earners per type.",
        "hint": "ROW_NUMBER() OVER (PARTITION BY trip_type ORDER BY earnings_per_hour DESC), filter WHERE rank <= 3",
        "concepts": ["ROW_NUMBER", "PARTITION BY", "ORDER BY in window", "WHERE rank filter"],
    },
    {
        "id": "sql_03", "topic": "CTE",
        "question": "Using the SO Survey data, write a CTE that calculates median salary per country, filters to countries with 100+ respondents, then ranks them by salary. Explain why CTE over subquery.",
        "hint": "WITH cte AS (...), MEDIAN() or PERCENTILE_CONT(0.5), HAVING COUNT(*) >= 100",
        "concepts": ["WITH clause", "MEDIAN", "HAVING", "readability benefit of CTE"],
    },
    {
        "id": "sql_04", "topic": "LAG — month-over-month",
        "question": "In the Job Market Pulse dataset, calculate month-over-month change in Python job postings. Show current month, previous month, absolute change, and % change.",
        "hint": "LAG(count) OVER (ORDER BY month), then (current - prev) / prev * 100",
        "concepts": ["LAG", "DATE_TRUNC", "percentage calculation", "NULL for first row"],
    },
    {
        "id": "sql_05", "topic": "FILTER clause",
        "question": "Using SO Survey, write one query showing per country: total devs, remote count, in-person count, remote %. Use FILTER instead of CASE WHEN.",
        "hint": "COUNT(*) FILTER (WHERE RemoteWork='Remote') — DuckDB specific syntax",
        "concepts": ["FILTER clause", "conditional aggregation", "single-pass aggregation benefit"],
    },
    {
        "id": "sql_06", "topic": "UNNEST + STRING_SPLIT",
        "question": "SO Survey has LanguageHaveWorkedWith as 'Python;SQL;JavaScript'. Write a query to count developers per language. Use UNNEST and STRING_SPLIT.",
        "hint": "UNNEST(STRING_SPLIT(col, ';')) AS lang, then GROUP BY lang — DuckDB syntax",
        "concepts": ["STRING_SPLIT", "UNNEST", "TRIM", "GROUP BY unnested value"],
    },
    {
        "id": "sql_07", "topic": "Running total + % of total",
        "question": "Using Olist monthly revenue, show cumulative revenue by month and what % of annual total each month represents.",
        "hint": "SUM() OVER (ORDER BY month ROWS UNBOUNDED PRECEDING), total in subquery or SUM() OVER ()",
        "concepts": ["SUM OVER", "ROWS UNBOUNDED PRECEDING", "percentage of total", "window vs aggregate"],
    },
    {
        "id": "sql_08", "topic": "Anti-join",
        "question": "You have all_customers and paying_customers tables. Find customers who NEVER paid. Show both LEFT JOIN + NULL and NOT EXISTS approaches. Which is faster and why?",
        "hint": "LEFT JOIN paying ON ... WHERE paying.id IS NULL  vs  WHERE NOT EXISTS (SELECT 1 FROM paying WHERE ...)",
        "concepts": ["LEFT JOIN WHERE NULL", "NOT EXISTS", "index usage", "performance tradeoff"],
    },
]

BEHAVIORAL_QUESTIONS = [
    {
        "id": "beh_01", "topic": "Handling messy data",
        "question": "Tell me about a time you worked with a large messy dataset and had to ensure data quality before analysis.",
        "hint": "NYC 311 (NaN/Int64 fix, 0 ingestion errors) or Uber (26,500 rows, data cleaning). Quantify the problem and result.",
        "elements": ["specific dataset", "what was messy", "your exact steps", "measurable outcome"],
    },
    {
        "id": "beh_02", "topic": "Business impact from data",
        "question": "Describe a project where your analysis led to a concrete business insight. What was the finding and how did you communicate it?",
        "hint": "Uber: 47% $/hr premium for short trips. Olist: delivery delays by state. SO Survey: remote devs earn 51% more.",
        "elements": ["specific metric found", "why it matters", "how communicated", "actual numbers"],
    },
    {
        "id": "beh_03", "topic": "Learning quickly",
        "question": "Tell me about a time you had to learn a new technology quickly to complete a project.",
        "hint": "DuckDB/MotherDuck, dbt, MCP servers, GitHub Actions — all learned from scratch under timeline pressure.",
        "elements": ["specific tech", "timeline pressure", "how you learned", "project outcome"],
    },
    {
        "id": "beh_04", "topic": "Automation + reliability",
        "question": "Give me an example of a manual process you automated. What was the before/after impact?",
        "hint": "Weather Pipeline: 2×/day auto, 20 cities, 6 continents. Job Market Pulse: 110 API calls/day. GitHub Actions CI across 5 projects.",
        "elements": ["before state", "solution built", "time saved", "reliability improvement"],
    },
    {
        "id": "beh_05", "topic": "Technical communication",
        "question": "Tell me about a time you had to explain a complex technical finding to a non-technical audience.",
        "hint": "Any dashboard project. Simplify: 'Instead of showing SQL queries, I built a Streamlit dashboard with...'",
        "elements": ["non-tech audience", "complexity simplified", "visual or analogy", "decision resulted"],
    },
    {
        "id": "beh_06", "topic": "CI/CD + testing",
        "question": "Describe your experience with CI/CD in a data context. How did you ensure pipeline reliability?",
        "hint": "GitHub Actions across 5 projects. 23/23 smoke tests. SQLFluff linting. Docker. Retry logic. Health checks.",
        "elements": ["specific CI/CD tools", "test types", "failures caught", "uptime result"],
    },
]

PROJECT_QUESTIONS = [
    {
        "id": "proj_01", "topic": "SO Survey Analytics",
        "question": "Walk me through the SO Survey Analytics project — architecture, main challenge, key insight, and how you validated data quality.",
        "context": "65K responses, DuckDB, 23 CI smoke tests, HF Spaces, GitHub Actions daily refresh",
        "elements": ["architecture overview", "technical challenge", "key insight with numbers", "testing approach"],
    },
    {
        "id": "proj_02", "topic": "Olist dbt architecture",
        "question": "You used dbt with DuckDB for Olist. Explain what dbt does, why you chose it, and how your 54 tests added value.",
        "context": "dbt-duckdb, staging + marts layers, 54 tests, 100K orders, $13.2M revenue modeled",
        "elements": ["what dbt does simply", "staging vs marts", "test types", "business value of testing"],
    },
    {
        "id": "proj_03", "topic": "Weather Pipeline reliability",
        "question": "Your Weather Pipeline runs twice daily. How did you design it to handle API failures gracefully? What happens if one city's call fails?",
        "context": "20 cities, tenacity retry 3×, graceful skip per city, GitHub Actions, HF Spaces",
        "elements": ["retry logic", "graceful degradation", "what partial success looks like", "monitoring"],
    },
    {
        "id": "proj_04", "topic": "MCP Data Quality Agent",
        "question": "Explain your MCP Data Quality Agent — what problem it solves, how the 19 tools are organized, and how a data analyst uses it in practice.",
        "context": "19 tools, DuckDB + PostgreSQL, CI 33/33 tests, Claude integration, 4 tool categories",
        "elements": ["MCP protocol simply", "tool categories", "real workflow example", "CI testing"],
    },
    {
        "id": "proj_05", "topic": "Uber driver insights",
        "question": "What was the most surprising insight from your Uber driver analytics? How did you find it and what does it mean practically for a driver?",
        "context": "3,448 trips, $118/hr short trips vs $80/hr long hauls, surge timing analysis, PostgreSQL",
        "elements": ["the specific insight", "analysis path", "statistical validity", "practical driver implication"],
    },
    {
        "id": "proj_06", "topic": "Job Market Pulse design",
        "question": "Your Job Market Pulse hits the API 110 times daily. How did you design the data model and keep the dashboard useful as data accumulates?",
        "context": "Adzuna API, 10 skills × 11 cities, DuckDB, daily append strategy, trend analysis",
        "elements": ["schema design", "append vs replace", "deduplication strategy", "trend analysis over time"],
    },
]
