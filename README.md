<div align="center">

# ⚽ EURO 2024 | Tactical Intelligence Pro

![Logo UEFA Euro 2024](Logo_UEFA_Euro_2024.svg)

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Click_Here-success?style=for-the-badge)](https://your-app-link.streamlit.app)

> **A high-performance tactical analysis dashboard for EURO 2024** — turning raw match data into actionable football intelligence.

[🚀 Live Demo](#-live-demo) • [✨ Features](#-key-features) • [🛠️ Installation](#️-installation--local-setup) • [📊 Data](#-data-source) • [🤝 Contributing](#-contributing)

</div>

---

## 🚀 Live Demo

Experience the full tactical hub live on Streamlit Cloud:

🔗 **[Launch App → your-app-link.streamlit.app](https://your-app-link.streamlit.app)**

> No installation required — explore EURO 2024 data directly in your browser.

---

## ✨ Key Features

### 🌍 Tournament Overview
Get a bird's-eye view of EURO 2024 with tournament-wide statistics:
- Total goals, xG aggregates, and event intensity heatmaps
- Competition trends across all group and knockout stages

### 🎯 Team Focus
Deep-dive into any nation's tactical DNA:
- **Shot Maps** — Offensive strike zones with goal outcome overlays
- **Performance Benchmarks** — Radar charts comparing key team metrics across the tournament
- **Automated Tactical Reports** — AI-generated insights derived from match event data

### 👤 Player Profiler
Understand individual contributions at a granular level:
- Performance metrics and volume statistics per 90 minutes
- Tactical role identification based on event positioning
- Progressive actions, duels, and chance creation breakdown

### ⚔️ Head-to-Head Duel Comparison
Go beyond the stats with interactive player matchups:
- Side-by-side KPI comparison between any two players
- Visual overlays for shooting, passing, and defensive metrics

### 🕸️ Spatial Tactics — Pass Networks
Uncover team structure and tactical shape:
- Interactive pass networks with connection intensity weighting
- Average player positions plotted on a real pitch
- Top pass combinations by frequency and progression
- **Half-time filter** — compare 1st vs 2nd half tactical shifts

---

## 🛠️ Technology Stack

| Category | Technology |
|---|---|
| **Framework** | [Streamlit](https://streamlit.io/) |
| **Data Analysis** | [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/) |
| **Visualizations** | [Plotly](https://plotly.com/), [Matplotlib](https://matplotlib.org/) |
| **Football Analytics** | [mplsoccer](https://mplsoccer.readthedocs.io/) |

---

## 📦 Installation & Local Setup

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Step-by-step

**1. Clone the repository**
```bash
git clone https://github.com/maghous/Euro2024-Tactical-Hub.git
cd Euro2024-Tactical-Hub
```

**2. Create a virtual environment** *(recommended)*
```bash
python -m venv venv
source venv/bin/activate        # On macOS/Linux
venv\Scripts\activate           # On Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Launch the application**
```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501` 🎉

---

## 📊 Data Source

All match and event data is stored locally in the `data/` directory:
```
data/
├── euro_matches.csv    # Match-level information (teams, scores, venues, dates)
└── euro_events.csv     # Granular event-level data (shots, passes, duels, etc.)
```

| File | Description | Key Fields |
|---|---|---|
| `euro_matches.csv` | Match metadata | Teams, scores, formations, xG |
| `euro_events.csv` | Event-level detail | Type, location, outcome, player, minute |

> 📌 Data covers all EURO 2024 matches from the group stage through the final.

---

## 📁 Project Structure
```
Euro2024-Tactical-Hub/
├── app.py                  # Main Streamlit entry point
├── requirements.txt        # Python dependencies
├── Logo_UEFA_Euro_2024.svg # Tournament logo
├── data/
│   ├── euro_matches.csv
│   └── euro_events.csv
└── README.md
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/AmazingFeature`
3. Commit your changes: `git commit -m 'Add AmazingFeature'`
4. Push to the branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

Feel free to check the [issues page](https://github.com/maghous/Euro2024-Tactical-Hub/issues) for open tasks.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

<div align="center">

**Built with ❤️ for football fans and data analysts**

⭐ If you find this project useful, please consider giving it a star!

[![GitHub stars](https://img.shields.io/github/stars/maghous/Euro2024-Tactical-Hub?style=social)](https://github.com/maghous/Euro2024-Tactical-Hub/stargazers)

</div>
