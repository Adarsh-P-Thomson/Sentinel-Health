Sentinel Health (PulseGuard)

Vision: A highly extensible, agentic monitoring platform that automates the extraction of patient safety signals from the noisy web. We are building a LangGraph-powered multi-agent system combined with MCP (Model Context Protocol) to move from passive "listening" to autonomous "hunting" for adverse healthcare events.

1. The Solution: Core Modules & ArchitectureModule A: The Configurator (The "Input")
Before the intelligence kicks in, the human remains in command.
Purpose: To allow the Admin to define the "Mission Parameters" for the AI agents.
What goes here: A sleek screen where the user enters Target Keywords, selects the Time Interval, and chooses the Data Sources (e.g., X, Reddit).
The Vibe: Precise and professional. This ensures the agentic brain stays focused and efficient.
Module B: MCP Servers (The "Scout")
The Model Context Protocol (MCP) is the "bridge" that connects our AI to the outside world.
Purpose: To standardize how our agents "talk" to different websites and databases.
Why MCP: It creates a "Universal Adapter." Whether it’s X, Reddit, or a medical database, the MCP server translates raw data into a language the AI understands instantly.
The Integration: This makes the system infinitely extensible. Adding a new forum is as simple as plugging in a new MCP server without touching the core AI logic.
Module C: LangGraph (The "Multi-Agent Brain")
LangGraph allows our AI to think in loops through a multi-agent assembly line where specialized agents collaborate like a professional medical team:
The Anonymizer Agent: Focuses solely on scrubbing PII/PHI (Names, Locations) to ensure HIPAA compliance.
The Medical Entity Extractor: A specialist in identifying drugs, dosages, and symptoms from messy, slang-heavy social text.
The Sentiment Analyst: Evaluates the emotional tone—distinguishing between a patient’s frustration with a side effect vs. general dissatisfaction.
The Trend & Virality Agent: Checks engagement metrics to determine if a specific safety signal is "Trending" or has "High Viral Potential."
The Safety Auditor: The final gatekeeper that "loops back" to the Medical MCP to verify symptoms against known drug side effects and flags "Unknown/Critical" events.
Module D: The User UI (The "Outcome")
The User UI is the command centre where raw intelligence is turned into a visual story.
Purpose: To show the final, analyzed medical insights to the healthcare professional.
What goes here: Animated timeline charts, "High Risk" signal cards, and Virality Gauges.
The Vibe: Simple, fast, and actionable. Using Framer Motion, the dashboard feels alive, with cards sliding and pulsing as new signals are verified.
Module E: Actionable Insights & Crisis Sharing (The Intervention)
This module transforms intelligence into action, allowing the Admin to bridge the gap between the web and health authorities.
Purpose: To share validated insights with the necessary teams to trigger immediate intervention.
What goes here: A "Share & Escalate" hub. One click generates a Patient Impact Report highlighting the patient experience and flagged safety impacts.
Distribution: Send instant WhatsApp/Slack notifications, auto-draft structured Email Reports, or sync directly with a CRM (Salesforce/Zendesk) if required.
Module F:Langsmith
LangSmith is the "Black Box Flight Recorder" providing total transparency.
Purpose: To provide Explainability ,monitoring and Trust.
The Integration: Every card on the User UI has a "Trace" button to show the user exactly why the AI made that specific decision before they choose to share it.

Module G: Data Retention & Cost Optimization (The "Sustain")
In a high-volume social environment, data noise can be expensive. This module ensures the system is cost-effective and compliant.
Purpose: To intelligently manage data storage and LLM token usage.
Data Retention: A tiered storage policy. "High Value" flagged safety signals are moved to permanent PostgreSQL storage for historical reporting and MongoDb, Redis/Elasticsearch. "Low Value/Noise" data is purged after 30 days to reduce storage costs and maintain a clean database.
Cost Optimization: We implement LLM Caching (via Redis). If multiple searches for the same drug return identical raw text, the system retrieves the previous analysis instead of re-running the expensive AI Brain, reducing API costs by up to 40%.


3. The Tech StackFrontend: 

Next.js 14, Tailwind CSS, Framer Motion.
Agentic Framework: LangGraph (Multi-agent orchestration) & LangChain.
Privacy: Microsoft Presidio (PII/PHI scrubbing).
Connectivity: MCP Servers (Python-based adapters for Social & Medical APIs).
Observability & Retention: LangSmith (Traceability), Redis (Caching), PostgreSQL (Permanent DB),MongoDB ,Elasticsearch.
Communication: Twilio (WhatsApp), SendGrid (Email).
Input: Admin enters "Drug-Y" in the Configurator.
Scout: MCP Server fetches a viral Reddit thread about a rare reaction to Drug-Y.
Brain (Multi-Agent): Anonymizer cleans the data; Extractor identifies the reaction; Trend Agent flags it as "Spiking"; Auditor confirms it is an unlisted risk.
Outcome: The User UI displays a high-priority red card.
Intervention: Admin clicks "Share Insight." The system generates a report of the Patient Experience and pings the safety team via WhatsApp.
Sustain: The "High Value" signal is archived in PostgreSQL, while the system caches the result in Redis to save costs on the next identical query.
Multimodal Vision: Analyzing patient-uploaded photos,videos.
More Secured Analysis.


4. Real-Time Example: The "Pulse-to-Action" Flow

Input: Admin enters "Drug-Y" in the Configurator, source reddis
Scout: MCP Server fetches a viral Reddit thread about a rare reaction to Drug-Y.
Brain (Multi-Agent): Anonymizer cleans the data; Extractor identifies the reaction; Trend Agent flags it as "Spiking"; Auditor confirms it is an unlisted risk.
Outcome: The User UI displays a high-priority red card.
Intervention: Admin clicks "Share Insight." The system generates a report of the Patient Experience and admin pings the safety team via WhatsApp.




Sustain: The "High Value" signal is archived in PostgreSQL, while the system caches the result in Redis to save costs on the next identical query.


IDEA IS BASED ON THIS:
Theme 6
Real-Time Social Listening for Patient Experience & Safety Signals

The Problem 

Healthcare insights are increasingly available through patient-generated data on social media, forums, and online platforms. These sources provide early signals of adverse events, treatment dissatisfaction, and quality-of-life impacts that are often not captured in traditional systems. 

Historically, though, these insights have been difficult to acquire due to a lack of systems that effectively listen to or index the right sources on the internet. 

What to Build

Build a solution that identifies mentions or references made to a set of keywords, from multiple sources, at varying degrees of intervals, and can run analysis on the data acquired. Core Requirements:

There are two parts to this problem 

Part 1: Build a generic engine that can then be leveraged to 

Build Social monitoring projects – a project would be where all the information related to a use case.
Each project would allow configuration of keywords that need to be monitored, eg: drugs, symptoms, and conditions.
Additionally, the user can also configure the sources (X, Reddit, communities, forums) where these keywords need to be monitored.
Each source will have a crawler/data acquisition engine that acquires and extracts the data for further processing.
Each source defined in a project should also allow for the configuration of latency metrics
Real-time,
Daily
Weekly
A UI to set up and configure these projects
New engine types for sources (data sources) can also be set up or configured via this admin tool. 
Part 2: Analysis 

Identify entities, extract entities, and extract individual sentiment from the individual content pieces acquired as part of the feed.
Extract overall sentiment and trending from a source (for a defined period of time)
Highlight any safety issues or any adverse issues reported
Show trending of detected signals in a timeline view.
Incorporate explainability, traceability, and confidence scores when building these models.
Flag and PII or PHI that may have been accidentally reported in the acquired data.
Scope

In  
Support multiple sources/engines for acquiring data
Processing pipelines
Storage of acquired data/signals
Ability to run models, reporting, and analysis against the data acquired.
Dashboard, Administration, and reporting UI.
Major sources: X, Reddit, Quora, online communities that fit a forum structure.
Out
Data retention
Cost projections 
Tech Stack

Open to the choices made by the team. Ideally lean towards python.
Modularity, extensibility and configurability will be key
Evaluation Criteria

Ideas on building engines to acquire data (40%)
Approaches for data acquisition from multiple sources
Extensibility (ease of adding new websites for scraping/searching keywords)
Reliability of sourcing data
Execution on above ideas (30%)
Clarity of design
Architecture
Working demo
Presentation and UX (15%)
Overall presentation, UX, and dashboard design
How well key differentiators are highlighted compared to existing solutions
Uniqueness (15%)
Innovative application of agentic and AI capabilities, especially for onboarding new data sources/websites
Deliverables

Working Demo – Ideally Live
Pitch Deck
Architecture
Repository Link
Readme for setup and details of executing code
Walkthrough of the solution
Bonus

Application of Agentic approaches
Constraints

All code written for the purposes of the hackathon
Ownership assignment to the sponsor for IP 
What we provide 

Limited credits for https://twitterapi.io
Mentors
Ideas

X ingestion using https://twitterapi.io
Adjacent solutions:
https://github.com/Kuew/social-media-monitoring-open-source