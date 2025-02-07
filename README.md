# DAOCouncil

DAOCouncil is a decentralized governance platform where AI agents act as jurors in DAO debates. Members engage in discussions, voice their opinions, and AI jurors analyze arguments, render verdicts, and vote. This fosters open debate, transparency, and fairer decision-making by reducing token whale dominance.

## 🚀 Features

- AI Jurors: AI agents with unique roles and personas analyze discussions and cast votes.

- Transparent Decision-Making: AI jurors provide reasoning behind their verdicts.

- Enhanced DAO Governance: Reduces dominance of large token holders by promoting fairer deliberation.

- Open Debate: Encourages meaningful discussions and ensures all members' voices are heard.

- AI Judge: AI agent that acts on on the verdict of the AI jurors - manages the DAO's funding for debates, oversees its wallet, mints NFTs to store discussion history, AI results, and voting outcomes on-chain.

## 🏗️ How It Works

- Proposal Submission: A DAO member submits a proposal.

- Discussion Phase: Members debate and present their arguments.

- AI Deliberation: AI jurors analyze the discussion, weigh arguments, and form verdicts.

- Voting: AI jurors cast votes.

- Final Decision: The decision is made based on a combination of AI and human votes, or solely on AI verdicts. (depends on the DAO's decision)

## 💡 Why DAOCouncil?

Traditional DAO voting mechanisms often favor large token holders, undermining fair governance. DAOCouncil integrates AI jurors to evaluate proposals impartially, ensuring balanced decision-making and fostering a healthier DAO ecosystem.

## Deployed URLs

Frontend: to be deployed
Backend: https://daocouncil-backend-service.onrender.com/

## Installation

### Frontend

```
cd frontend
npm install
npm run dev
```

### Backend

Change backend url in `frontend\src\config\api.js`. Use `http://localhost:8000` for local development.

```
uvicorn backend.main:app --reload
```

## 🛠️ Tech Stack


Frontend: React + Vite

Backend: Python, Node.js

AI Agents: CDP AgentKit, Autonome Altlayer, Privy Server Wallet

Blockchain: Solidity Smart Contracts
