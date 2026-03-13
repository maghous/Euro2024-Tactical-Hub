# ⚽ EURO 2024 | Tactical Intelligence Pro

![Logo UEFA Euro 2024](Logo_UEFA_Euro_2024.svg)

A high-performance tactical analysis dashboard for **EURO 2024**, built with **Python** and **Streamlit**. This application provides deep insights into match events, player performances, and team strategies using advanced data visualization.

## 🚀 Live Demo
Experience the tactical hub live on Streamlit Cloud:  
**[Link to your deployed app]**

## ✨ Key Features
-   **🌍 Global Landscape**: Tournament-wide statistics including total goals, xG, and event intensity.
-   **🎯 Team Focus**: Detailed analysis for each nation:
    -   **Shot Maps**: Visualizing offensive strike zones and goal outcomes.
    -   **Performance Benchmarks**: Radar charts comparing team metrics.
    -   **Tactical Reports**: Automated insights based on tournament data.
-   **👤 Player Profiler**: Individual performance metrics, volume analysis, and tactical role identification.
-   **⚔️ Duel Comparison**: Side-by-side KPI matchup between two players with interactive visualizations.
-   **🕸️ Spatial Tactics (Pass Networks)**: 
    -   Interactive pass networks with connection intensity.
    -   Average player positions and top pass combinations.
    -   Filter by 1st or 2nd half for temporal tactical shifts.

## 🛠️ Technology Stack
-   **Framework**: [Streamlit](https://streamlit.io/)
-   **Data Analysis**: [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
-   **Visualizations**: [Plotly](https://plotly.com/), [Matplotlib](https://matplotlib.org/)
-   **Football Analytics**: [mplsoccer](https://mplsoccer.readthedocs.io/) (for pitch rendering and pass networks)

## 📦 Installation & Local Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/maghous/Euro2024-Tactical-Hub.git
    cd Euro2024-Tactical-Hub
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application**:
    ```bash
    streamlit run app.py
    ```

## 📊 Data Source
The application uses tournament data (matches and events) stored in the `data/` directory. 
-   `data/euro_matches.csv`: Detailed match information.
-   `data/euro_events.csv`: Granular event-level data for all matches.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/maghous/Euro2024-Tactical-Hub/issues).

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.

---
*Created with ❤️ for football fans and data analysts.*
