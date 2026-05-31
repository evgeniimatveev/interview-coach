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
    {
        "id": "sql_09", "topic": "WHERE vs HAVING",
        "question": "Write a query on the Olist dataset that finds product categories with 100+ orders AND average review score above 4.0. Explain the difference between WHERE and HAVING and when each applies.",
        "hint": "WHERE filters rows before GROUP BY (row-level). HAVING filters groups after aggregation (group-level). Both can appear in same query.",
        "concepts": ["WHERE vs HAVING", "GROUP BY", "execution order", "row-level vs group-level filter"],
    },
    {
        "id": "sql_10", "topic": "CASE WHEN + COALESCE",
        "question": "Using SO Survey, classify each developer's salary into bands: 'Junior' (<50K), 'Mid' (50–100K), 'Senior' (100–200K), 'Staff+' (>200K). Handle NULL salaries gracefully. Count per band.",
        "hint": "CASE WHEN salary_usd < 50000 THEN 'Junior' ... END; COALESCE(salary_usd, 0) for NULLs; wrap in outer GROUP BY band",
        "concepts": ["CASE WHEN", "COALESCE", "NULL handling", "salary banding", "GROUP BY derived column"],
    },
    {
        "id": "sql_11", "topic": "Deduplication",
        "question": "The Uber trips table has duplicate rows from an ETL bug. Write a query to return only the first occurrence of each trip_id. Show the ROW_NUMBER approach AND explain how you'd delete duplicates in production.",
        "hint": "ROW_NUMBER() OVER (PARTITION BY trip_id ORDER BY ingested_at) AS rn, then WHERE rn = 1. For delete: CTE with ROW_NUMBER, DELETE WHERE rn > 1.",
        "concepts": ["ROW_NUMBER dedup", "PARTITION BY", "CTE with DELETE", "idempotent ETL"],
    },
    {
        "id": "sql_12", "topic": "Cohort retention",
        "question": "Using Olist orders, define each customer's cohort as their first purchase month. Show month-1 and month-2 retention rates for each cohort. Explain the business insight.",
        "hint": "DATE_TRUNC('month', MIN(order_date)) OVER (PARTITION BY customer_id) AS cohort, then count distinct customers who returned in cohort+1, cohort+2 months.",
        "concepts": ["DATE_TRUNC", "cohort definition", "retention %", "MIN OVER partition", "business insight"],
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
    {
        "id": "beh_07", "topic": "Tell me about yourself",
        "question": "Give your 90-second 'Tell me about yourself.' Structure: Background → Key Skills → Best Project with a number → What you're looking for.",
        "hint": "Background: QA/ops → self-taught data → 2+ years analytics projects. Skills: SQL/Python/Docker/DuckDB. Project: Uber ($118/hr insight) or Weather Pipeline (20 cities, 2×/day). Goal: DA or AE role, LA/Remote.",
        "elements": ["background arc in 1–2 sentences", "2–3 specific skills", "one quantified project", "clear goal statement", "under 90 seconds"],
    },
    {
        "id": "beh_08", "topic": "Greatest weakness",
        "question": "What is your greatest professional weakness, and what concrete steps are you taking to improve it?",
        "hint": "Be genuine — not 'I work too hard.' Real example: public speaking → Yoodli practice + mock interviews. Show self-awareness + active improvement.",
        "elements": ["genuine weakness not humble-brag", "specific example of it impacting work", "concrete steps already taken", "evidence of progress"],
    },
    {
        "id": "beh_09", "topic": "5-year career goal",
        "question": "Where do you see yourself in 5 years, and how does this role fit into that path?",
        "hint": "DA/AE → Senior → Analytics Lead or ML Engineer. Show ambition but anchor it to this specific role and what skills you'll build here.",
        "elements": ["clear direction", "realistic progression", "link to current role", "skills you want to develop"],
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
    {
        "id": "proj_07", "topic": "HR BI Analytics — Tableau",
        "question": "Walk me through your HR BI Analytics project. What was the business question, how did you model the data, and what was the key Tableau insight?",
        "context": "30 employees, 5 departments, Sales dept $102K avg salary (+17% above avg), Tableau dashboard",
        "elements": ["business question stated", "data model explained", "key insight with numbers", "Tableau design decision"],
    },
    {
        "id": "proj_08", "topic": "Data Interview Coach",
        "question": "Tell me about your Data Interview Coach project. What problem does it solve, how does the Claude API integration work, and what was the most interesting engineering decision?",
        "context": "CLI + Streamlit, Claude Sonnet streaming + prompt caching (~70% cost reduction), SQLite progress tracking, HF Spaces Docker deploy, 20 questions across SQL/Behavioral/Project/Stats",
        "elements": ["problem statement", "architecture in 2 sentences", "Claude API streaming + caching", "most interesting decision"],
    },
]

STATS_QUESTIONS = [
    {
        "id": "stats_01", "topic": "Mean vs Median",
        "question": "A company reports 'average developer salary is $150K.' You suspect this is misleading. Explain when to use mean vs median, give a concrete example from SO Survey data, and say how you'd correctly report it.",
        "hint": "Mean is pulled up by outliers (FAANG engineers). Median = 50th percentile, more robust for skewed distributions. SO Survey global median: $72K. Use median for salary, income, housing prices.",
        "concepts": ["mean sensitivity to outliers", "median as robust center", "skewed distributions", "honest reporting"],
    },
    {
        "id": "stats_02", "topic": "p-value explained",
        "question": "Your A/B test returns p=0.03. Your manager says 'great, we're 97% sure the new feature works!' Correct this misconception clearly and explain what p=0.03 actually means.",
        "hint": "p-value = P(data this extreme | H0 is true). NOT P(H0 is false). p=0.03 means: if there were truly no effect, we'd see results this extreme 3% of the time by chance alone.",
        "concepts": ["null hypothesis H0", "p-value definition", "common misconception", "significance threshold α=0.05"],
    },
    {
        "id": "stats_03", "topic": "Type I vs Type II errors",
        "question": "Explain Type I and Type II errors using A/B testing. For a new pricing page: which error is more costly? For a medical screening test: which error is more costly? What's the tradeoff?",
        "hint": "Type I (α): false positive — ship a change that doesn't work. Type II (β): false negative — miss a real improvement. Lower α → need larger sample to maintain power. Context determines which is worse.",
        "concepts": ["false positive α", "false negative β", "power = 1-β", "tradeoff", "business context determines priority"],
    },
    {
        "id": "stats_04", "topic": "A/B test design",
        "question": "You want to test a new checkout button. Walk me through: hypothesis, success metric, guardrail metric, how you'd determine sample size, test duration, and what 'winner' means.",
        "hint": "H0: no difference. Primary metric: conversion rate. Guardrail: revenue/user (don't optimize CVR at expense of order value). Sample size: baseline CVR, MDE, α=0.05, power=0.80. Duration: min 2 full business cycles.",
        "concepts": ["hypothesis", "primary vs guardrail metrics", "MDE", "sample size concept", "business cycles", "winner criteria"],
    },
    {
        "id": "stats_05", "topic": "Statistical vs practical significance",
        "question": "Your A/B test shows p=0.01 (statistically significant) but only a 0.1% lift in conversion rate. Revenue impact: +$8K/year. Engineering cost: 2 weeks. Should you ship it? Walk through your decision.",
        "hint": "Statistical significance ≠ practical significance. Ask: absolute revenue lift vs implementation cost + opportunity cost. $8K may not justify 2 weeks of engineering. Effect size matters, not just p-value.",
        "concepts": ["practical vs statistical significance", "absolute vs relative lift", "cost-benefit analysis", "effect size", "opportunity cost"],
    },
    {
        "id": "stats_06", "topic": "A/B testing pitfalls",
        "question": "Name 3 common A/B testing mistakes that invalidate results. For each: what goes wrong, why it's a problem, and how to prevent it.",
        "hint": "1. Peeking early → inflated false positive rate → pre-commit to duration. 2. Multiple comparisons → Bonferroni correction or FDR. 3. Simpson's Paradox → always check segment-level results. Bonus: novelty effect, network effects.",
        "concepts": ["peeking problem", "multiple comparisons Bonferroni", "Simpson's Paradox", "novelty effect", "network effects / contamination"],
    },
]
