# AI Financial Analyst Agent

An autonomous AI-powered platform designed for deep financial research and real-time market monitoring. This agent combines private document intelligence (RAG) with live web tools to provide professional-grade investment insights.

### Core Features

* **RAG-Powered SEC Intelligence**: Uses a PGVector database to search and analyze private SEC 10-K filings for technical financial data, risks, and corporate strategies.
* **Live Market Data**: Integrates with Yahoo Finance to fetch real-time stock prices and market capitalization.
* **Autonomous Reasoning**: Built with LangGraph, the agent independently decides whether to search internal filings or fetch live market data based on your questions.
* **Interactive Visual Analytics**: Features a custom Streamlit dashboard that generates interactive candlestick charts and automated technical reports.
* **Automated Investor Insights**: Provides concise 30-day performance analytics including trend direction, price range, and volatility assessments.
* **Private Data Pipeline**: Includes a complete ingestion engine that converts complex SEC HTML filings into clean, searchable Markdown.
