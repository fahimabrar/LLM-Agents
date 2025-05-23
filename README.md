# LLM-Agents

Welcome to LLM-Agents – a personal repository where I explore, build, and experiment with AI Agents powered by Large Language Models (LLMs).
This repo is dedicated to documenting my learning journey, sharing insights, and developing projects related to autonomous and semi-autonomous AI agents. Expect code samples, mini-projects, and experiments as I dive deeper into the world of AI agents and their real-world applications.

## 1. GDPR compliant Agent
**Overview**: This project automates the creation of GDPR-compliant privacy policies using Large Language Models (LLMs). It includes a feedback loop between a policy generator and a compliance evaluator to iteratively improve the policy until it meets GDPR standards.

**Diagram**<br>

<img src="https://raw.githubusercontent.com/fahimabrar/LLM-Agents/refs/heads/main/GDPR%20Complient%20Agent/Simple%20Flowchart%20Infographic%20Graph.png" alt="description" width="600" height="400">

   
## 2. Due-Diligence-Agent
What this app will do,
- It will search relevant webpages (using duckduckgo api) based on your query.
- Scrape the webpage and add relevant information to a vector database.
- You can select newly created knowledge to provide LLM to generate the response.

What is unique here,
- Traditional LLM has knowledge cutoff (limited by training data)
- This approach enhance knowledge based on real time data.
- This is locally hosted LLM (so no one gets your data)
You have more control about the knowledge source (e.g. selecting best knowledge source)
