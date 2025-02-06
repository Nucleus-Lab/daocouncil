# DAO Council Frontend

A modern web application for decentralized debate and decision-making.

## Features

- Welcome page with wallet connection
- Create new debates with customizable parameters
- Join existing debates using debate IDs
- Real-time debate chat with stance indication
- AI Juror opinions and voting visualization
- Interactive courtroom visualization

## Project Structure

```
frontend/
├── src/
│   ├── assets/           # Static assets (images, backgrounds)
│   │   ├── bg.jpg              # Courtroom background
│   │   └── character.png       # Character sprite
│   ├── components/       # React components
│   │   ├── CourtRoom.jsx       # Courtroom visualization
│   │   ├── CreateDebateForm.jsx # New debate creation form
│   │   ├── Header.jsx          # Application header
│   │   ├── JoinDebateForm.jsx  # Join debate form
│   │   ├── JurorOpinions.jsx   # AI Jurors' opinions display
│   │   ├── Messages.jsx        # Debate chat interface
│   │   ├── UserAvatar.jsx      # User avatar component
│   │   ├── VotingTrends.jsx    # Voting trends visualization
│   │   └── WelcomePage.jsx     # Welcome/landing page
│   ├── config/          # Configuration files
│   │   └── privy-client.ts     # Privy wallet configuration
│   ├── constants/       # Application constants
│   │   └── avatarColors.js     # Avatar color definitions
│   ├── hooks/           # Custom React hooks
│   │   ├── useJurorOpinions.js # Juror opinions management
│   │   └── useMessages.js      # Chat messages management
│   ├── utils/           # Utility functions
│   │   └── avatarUtils.js      # Avatar-related utilities
│   ├── App.css          # Global styles
│   ├── App.jsx          # Main application component
│   ├── index.css        # Base styles and Tailwind imports
│   └── main.jsx         # Application entry point
├── public/             # Public assets
├── .env.local          # Local environment variables
├── index.html          # HTML entry point
├── package.json        # Project dependencies
├── postcss.config.js   # PostCSS configuration
├── tailwind.config.js  # Tailwind CSS configuration
└── README.md           # Project documentation
```

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Access the application at `http://localhost:5173`

## Usage

1. Connect your wallet (demo mode available)
2. Choose to create a new debate or join an existing one
3. For new debates:
   - Enter topic, number of jurors, funding amount, and action prompt
   - Submit to create the debate
4. For joining debates:
   - Enter the debate ID (e.g., ABC12345 for demo)
   - Join the ongoing discussion
5. Participate in the debate:
   - Choose your stance (Yes/No)
   - Send messages
   - View AI Jurors' opinions
   - Track voting progress

## Technologies Used

- React
- Tailwind CSS
- Vite
- Web3 (Coming soon)