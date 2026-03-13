import streamlit as st
import pandas as pd
import os
import numpy as np
from mplsoccer import Pitch, VerticalPitch
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from matplotlib.colors import LinearSegmentedColormap
import plotly.express as px
import plotly.graph_objects as go

# --- Page Config & Theme ---
st.set_page_config(page_title="EURO 2024 | Tactical Intelligence Pro", layout="wide", initial_sidebar_state="expanded")

# --- Custom CSS for Premium Design ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .main { background-color: #0b0e14; color: #e6edf3; }
    
    /* Premium Metric Cards */
    .metric-container { display: flex; gap: 1rem; flex-wrap: wrap; margin: 1.5rem 0; }
    .metric-box {
        background: rgba(22, 27, 34, 0.6);
        backdrop-filter: blur(10px);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(88, 166, 255, 0.15);
        text-align: center;
        flex: 1;
        min-width: 200px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .metric-box:hover { 
        transform: translateY(-8px); 
        border-color: #58a6ff; 
        background: rgba(30, 41, 59, 0.7);
        box-shadow: 0 8px 30px rgba(88, 166, 255, 0.2);
    }
    .metric-title { color: #8b949e; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .metric-val { 
        background: linear-gradient(90deg, #58a6ff, #bc8cf2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem; font-weight: 800; 
    }
    .metric-sub { color: #3fb950; font-size: 0.8rem; font-weight: 600; margin-top: 4px; }
    
    /* Modern Titles */
    h1, h2, h3 { 
        font-weight: 700 !important;
        letter-spacing: -0.5px;
        margin-bottom: 20px;
    }
    .gradient-text {
        background: linear-gradient(90deg, #58a6ff, #bc8cf2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Professional Tabs */
    .stTabs [data-baseweb="tab-list"] { background: transparent; border-bottom: 1px solid #30363d; gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        height: 54px; font-weight: 600; color: #8b949e; border-radius: 8px 8px 0 0; padding: 0 24px;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] { 
        background: rgba(88, 166, 255, 0.05) !important;
        color: #58a6ff !important; 
        border-bottom: 3px solid #58a6ff !important; 
    }
    
    /* Report Styling */
    .report-card {
        background: rgba(13, 17, 23, 0.8);
        border-left: 5px solid #58a6ff;
        padding: 24px;
        border-radius: 12px;
        margin: 20px 0;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    .pass-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        background: rgba(22, 27, 34, 0.4);
        border-radius: 8px;
        overflow: hidden;
    }
    .pass-table th {
        background: rgba(88, 166, 255, 0.1);
        color: #58a6ff;
        text-align: left;
        padding: 12px;
        font-weight: 600;
        border-bottom: 2px solid rgba(88, 166, 255, 0.2);
    }
    .pass-table td {
        padding: 10px 12px;
        color: #e6edf3;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .pass-table tr:hover {
        background: rgba(88, 166, 255, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- Optimized Data Engine ---
@st.cache_data
def load_and_optimize():
    if not os.path.exists("data/euro_matches.csv") or not os.path.exists("data/euro_events.csv"):
        st.error("🚨 Missing database files in /data directory.")
        st.stop()
        
    m_df = pd.read_csv("data/euro_matches.csv")
    cols_essential = [
        'match_id', 'id', 'type', 'team', 'player', 
        'location', 'pass_end_location', 'pass_outcome', 'pass_recipient',
        'carry_end_location', 'shot_statsbomb_xg', 'shot_outcome', 'period'
    ]
    e_df = pd.read_csv("data/euro_events.csv", low_memory=False, usecols=lambda x: x in cols_essential)
    
    def parse_coords(df, col, prefix):
        if col not in df.columns: return df
        p = f"{prefix}_" if prefix else ""
        df[f'{p}x'] = np.nan
        df[f'{p}y'] = np.nan
        mask = df[col].notna()
        if not mask.any(): return df
        try:
            coords = df.loc[mask, col].str.strip('[]').str.split(',', expand=True).astype(float)
            if coords.shape[1] >= 2:
                df.loc[mask, f'{p}x'] = coords[0]
                df.loc[mask, f'{p}y'] = coords[1]
        except: pass
        return df

    e_df = parse_coords(e_df, 'location', '')
    e_df = parse_coords(e_df, 'pass_end_location', 'pass_end')
    e_df = parse_coords(e_df, 'carry_end_location', 'carry_end')

    cat_cols = ['type', 'team', 'shot_outcome', 'pass_outcome']
    for col in cat_cols:
        if col in e_df.columns:
            e_df[col] = e_df[col].astype('category')
            
    return m_df, e_df

matches, events = load_and_optimize()

# --- Visual Helpers ---
def render_metric(label, val, sub=""):
    st.markdown(f"""
    <div class="metric-box">
        <div class="metric-title">{label}</div>
        <div class="metric-val">{val}</div>
        <div class="metric-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

@st.cache_data
def get_team_stats(team_name):
    return events[events['team'] == team_name].copy()

# --- Sidebar Hub ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/5/52/UEFA_Euro_2024_Logo.svg/1200px-UEFA_Euro_2024_Logo.svg.png", width=200)
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/thumb/5/5e/UEFA_logo.svg/1200px-UEFA_logo.svg.png", width=100)
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Strategic Filtering")
all_nations = sorted(events['team'].unique())
target_nation = st.sidebar.selectbox("🎯 Focus Nation", all_nations, index=all_nations.index("England") if "England" in all_nations else 0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Database Status")
st.sidebar.write(f"**Matches:** {len(matches)}")
st.sidebar.write(f"**Events:** {len(events):,}")
st.sidebar.caption("High-Performance Mode Active")

# --- Main Intelligence Hub ---
st.markdown(f"<h1>🏆 <span class='gradient-text'>EURO 2024 Tactical Intelligence</span></h1>", unsafe_allow_html=True)

tabs = st.tabs([
    "📂 Global Overview",
    "🛡️ Team Intelligence", 
    "🕵️ Player Profiler", 
    "⚔️ Duel Comparison",
    "🕸️ Spatial Tactics"
])

TOUCH_ACTIONS = ["Pass", "Ball Receipt*", "Carry", "Ball Recovery", "Dribble", "Interception", "Shot", "Clearance", "Duel"]

# -- TAB 1: GLOBAL LANDSCAPE --
with tabs[0]:
    st.header("Tournament Statistical Landscape")
    
    # Global Metrics Grid
    m1, m2, m3, m4 = st.columns(4)
    with m1: render_metric("Total Goals", len(events[events['shot_outcome'] == 'Goal']), "Tournament Total")
    with m2: render_metric("Expected Goals", f"{events['shot_statsbomb_xg'].sum():.1f}", "Total xG Created")
    with m3: render_metric("Pass Accuracy", f"{(len(events[(events['type'] == 'Pass') & (events['pass_outcome'].isna())]) / max(1, len(events[events['type'] == 'Pass']))):.1%}", "Success Rate")
    with m4: render_metric("Intensity", f"{len(events)/len(matches):.0f}", "Events per Match")

    st.divider()
    
    # Global Visuals
    col_v1, col_v2 = st.columns([2, 1])
    with col_v1:
        st.subheader("Efficiency Matrix: Shot Quality vs Conversion")
        team_perf = events[events['type'] == 'Shot'].groupby('team', observed=True).agg(
            goals=('shot_outcome', lambda x: (x == 'Goal').sum()),
            xg=('shot_statsbomb_xg', 'sum')
        ).reset_index()
        fig_perf = px.scatter(team_perf, x='xg', y='goals', text='team', color='goals',
                             size='goals', color_continuous_scale='Magma', height=500,
                             labels={'xg': 'Created Expected Goals (xG)', 'goals': 'Actual Goals Scored'})
        fig_perf.add_shape(type='line', x0=0, y0=0, x1=max(team_perf.xg), y1=max(team_perf.xg), line=dict(dash='dash', color='rgba(255,255,255,0.2)'))
        fig_perf.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="#e6edf3")
        st.plotly_chart(fig_perf, use_container_width=True)
    
    with col_v2:
        st.subheader("Leaderboard: Scoring Nations")
        top_nations = team_perf.sort_values('goals', ascending=False).head(10)
        fig_bar = px.bar(top_nations, x='goals', y='team', orientation='h', color='goals', color_continuous_scale='Blues')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="#e6edf3")
        st.plotly_chart(fig_bar, use_container_width=True)

# -- TAB 2: TEAM INTELLIGENCE --
with tabs[1]:
    t_data = get_team_stats(target_nation)
    st.header(f"Team Deep Dive: {target_nation}")
    
    # Advanced Team Stats Calculation
    total_shots = len(t_data[t_data['type'] == 'Shot'])
    shots_on_target = len(t_data[(t_data['type'] == 'Shot') & (t_data['shot_outcome'].isin(['Goal', 'Saved', 'Post']))])
    shot_acc = (shots_on_target / max(1, total_shots))
    f3_actions = len(t_data[t_data['x'] > 80])
    f3_dominance = (f3_actions / max(1, len(t_data)))

    # Pillar Leaders Calculation
    top_scorer_df = t_data[t_data['shot_outcome'] == 'Goal'].groupby('player', observed=True)['id'].count().sort_values(ascending=False)
    top_passer_df = t_data[(t_data['type'] == 'Pass') & (t_data['pass_outcome'].isna())].groupby('player', observed=True)['id'].count().sort_values(ascending=False)
    top_recovery_df = t_data[t_data['type'].isin(['Ball Recovery', 'Interception'])].groupby('player', observed=True)['id'].count().sort_values(ascending=False)

    # Pillars & Advanced Metrics Grid
    st.subheader("🛡️ Team Pillars & Advanced Analytics")
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1: render_metric("Shot Accuracy", f"{shot_acc:.1%}", f"{shots_on_target}/{total_shots} on target")
    with m_col2: render_metric("Final 3rd Dominance", f"{f3_dominance:.1%}", "Share of total actions")
    with m_col3: render_metric("Expected Threat", f"{t_data['shot_statsbomb_xg'].sum():.2f}", "Total xG Accumulated")

    st.markdown("<br>", unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3)
    with p1: render_metric("Top Finisher", top_scorer_df.index[0] if not top_scorer_df.empty else "N/A", f"{top_scorer_df.values[0] if not top_scorer_df.empty else 0} Goals")
    with p2: render_metric("Playmaker", top_passer_df.index[0] if not top_passer_df.empty else "N/A", f"{top_passer_df.values[0] if not top_passer_df.empty else 0} Succ. Passes")
    with p3: render_metric("The Shield", top_recovery_df.index[0] if not top_recovery_df.empty else "N/A", f"{top_recovery_df.values[0] if not top_recovery_df.empty else 0} Recoveries")

    st.divider()
    
    col_t1, col_t2 = st.columns([1.2, 1])
    with col_t1:
        st.subheader("🎯 Offensive Strike Zone (Shot Map)")
        pitch = VerticalPitch(pitch_type='statsbomb', half=True, pitch_color='#0b0e14', line_color='#30363d', goal_type='box')
        fig, ax = pitch.draw(figsize=(8, 10))
        t_shots = t_data[t_data['type'] == 'Shot']
        goals = t_shots[t_shots['shot_outcome'] == 'Goal']
        non_goals = t_shots[t_shots['shot_outcome'] != 'Goal']
        pitch.scatter(non_goals.x, non_goals.y, s=(non_goals['shot_statsbomb_xg'] * 900) + 60, alpha=0.4, c='#8b949e', edgecolors='white', ax=ax, label='Shot (Non-Goal)')
        pitch.scatter(goals.x, goals.y, s=(goals['shot_statsbomb_xg'] * 900) + 120, alpha=0.9, c='#3FB950', marker='*', edgecolors='white', ax=ax, label='Goal')
        ax.legend(facecolor='#161b22', labelcolor='white', loc='lower center', bbox_to_anchor=(0.5, -0.05), ncol=2, fontsize=10)
        st.pyplot(fig)
        
    with col_t2:
        st.subheader("🛡️ Defensive Phase (Pressing & Interceptions)")
        def_layers = ["Ball Recovery", "Interception", "Duel", "Clearance", "Block"]
        sel_def = st.multiselect("Defensive Layers", def_layers, default=["Ball Recovery", "Interception"])
        if sel_def:
            pitch_d = Pitch(pitch_type='statsbomb', pitch_color='#0b0e14', line_color='#30363d')
            fig_d, ax_d = pitch_d.draw()
            d_data = t_data[t_data['type'].isin(sel_def)]
            if not d_data.empty:
                pitch_d.kdeplot(d_data['x'], d_data['y'], ax=ax_d, cmap='magma', fill=True, levels=50, alpha=0.5)
                pitch_d.scatter(d_data['x'], d_data['y'], s=10, c='white', alpha=0.1, ax=ax_d)
            st.pyplot(fig_d)

    st.divider()
    
    # Trends and Style Verdict
    col_tr1, col_tr2 = st.columns([1.5, 1])
    with col_tr1:
        st.subheader("📉 Campaign Performance Trend")
        t_matches = matches[(matches['home_team'] == target_nation) | (matches['away_team'] == target_nation)].copy()
        trend_data = []
        for _, m in t_matches.iterrows():
            m_id = m['match_id']
            m_events = events[events['match_id'] == m_id]
            opp = m['away_team'] if m['home_team'] == target_nation else m['home_team']
            txg = m_events[m_events['team'] == target_nation]['shot_statsbomb_xg'].sum()
            oxg = m_events[m_events['team'] == opp]['shot_statsbomb_xg'].sum()
            trend_data.append({'Opponent': str(opp), 'xG Created': txg, 'xG Conceded': oxg})
        
        df_trend = pd.DataFrame(trend_data)
        if not df_trend.empty:
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(x=df_trend['Opponent'], y=df_trend['xG Created'], name='xG For', line=dict(color='#58a6ff', width=3), mode='lines+markers'))
            fig_trend.add_trace(go.Scatter(x=df_trend['Opponent'], y=df_trend['xG Conceded'], name='xG Against', line=dict(color='#e34c26', width=3, dash='dot'), mode='lines+markers'))
            fig_trend.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="#e6edf3", height=380, margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig_trend, use_container_width=True)
            
    with col_tr2:
        st.subheader("🧠 Strategic Style Verdict")
        avg_xg_created = t_data['shot_statsbomb_xg'].sum() / max(1, len(t_matches))
        pass_ratio_val = len(t_data[t_data['type'] == 'Pass']) / max(1, len(t_data))
        
        style_verdict = f"**{target_nation}** displays a "
        if pass_ratio_val > 0.6: style_verdict += "Control-based identity with heavy emphasis on possession and slow build-up. "
        else: style_verdict += "Direct and transition-heavy style with rapid vertical movements. "
        
        if avg_xg_created > 1.5: style_verdict += "They are highly creative, consistently generating high-quality scoring chances. "
        else: style_verdict += "They often struggle to break through compact blocks, relying more on individual brilliance or set pieces. "
        
        st.markdown(f"<div class='report-card' style='font-size: 0.95rem; margin-top: 20px;'>{style_verdict}</div>", unsafe_allow_html=True)

# -- TAB 3: PLAYER PROFILER --
with tabs[2]:
    p_data_ref = get_team_stats(target_nation)
    p_names = sorted(p_data_ref['player'].dropna().unique())
    selected_p = st.selectbox("Select Player Profile", p_names, index=0)
    p_data = events[events['player'] == selected_p].copy()
    
    st.header(f"Scout Intelligence: {selected_p}")
    
    # --- Advanced Stats Calculation ---
    p_passes = p_data[p_data['type'] == 'Pass']
    p_succ_passes = p_passes[p_passes['pass_outcome'].isna()]
    p_acc = len(p_succ_passes) / max(1, len(p_passes))
    
    p_shots = p_data[p_data['type'] == 'Shot']
    p_sot = len(p_shots[p_shots['shot_outcome'].isin(['Goal', 'Saved', 'Post', 'Saved Off Target', 'Saved to Post'])])
    p_shot_acc = p_sot / max(1, len(p_shots))
    
    p_dribbles = p_data[p_data['type'] == 'Dribble']
    p_recoveries = len(p_data[p_data['type'] == 'Ball Recovery'])
    p_interceptions = len(p_data[p_data['type'] == 'Interception'])
    p_clearances = len(p_data[p_data['type'] == 'Clearance'])
    p_blocks = len(p_data[p_data['type'] == 'Block'])
    p_duels = len(p_data[p_data['type'] == 'Duel'])
    p_fouls_won = len(p_data[p_data['type'] == 'Foul Won'])
    p_carries = len(p_data[p_data['type'] == 'Carry'])
    p_receipts = len(p_data[p_data['type'] == 'Ball Receipt*'])
    p_miscontrols = len(p_data[p_data['type'] == 'Miscontrol'])
    p_vol_val = len(p_data)
    p_control_sec = 1 - (p_miscontrols / max(1, p_vol_val))
    
    p_xg_val = p_data['shot_statsbomb_xg'].sum()
    p_prog_val = len(p_data[p_data['x'] > 80])
    p_def_vol = p_recoveries + p_interceptions + p_blocks + p_clearances

    # --- KPI Grid (16 Metrics) ---
    st.subheader("⚡ Mega Scout Efficiency Benchmarks (16 KPIs)")
    
    # Row 1: Attack
    r1_1, r1_2, r1_3, r1_4 = st.columns(4)
    with r1_1: render_metric("Pass Accuracy", f"{p_acc:.1%}", f"{len(p_succ_passes)} Successful")
    with r1_2: render_metric("Expected Goals", f"{p_xg_val:.2f} xG", f"{len(p_shots)} Shots")
    with r1_3: render_metric("Shot Accuracy", f"{p_shot_acc:.0%}", f"{p_sot} on Target")
    with r1_4: render_metric("Goal Contribution", len(p_shots[p_shots['shot_outcome'] == 'Goal']), "Actual Goals")

    # Row 2: Defense
    r2_1, r2_2, r2_3, r2_4 = st.columns(4)
    with r2_1: render_metric("Ball Recoveries", f"{p_recoveries}", "Possession Won")
    with r2_2: render_metric("Interceptions", f"{p_interceptions}", "Lanes Blocked")
    with r2_3: render_metric("Clearances", f"{p_clearances}", "Danger Personal")
    with r2_4: render_metric("Blocks", f"{p_blocks}", "Shots/Passes Stopped")

    # Row 3: Physical & Skill
    r3_1, r3_2, r3_3, r3_4 = st.columns(4)
    with r3_1: render_metric("Duels", f"{p_duels}", "Physical Battles")
    with r3_2: render_metric("Dribbles", f"{len(p_dribbles)}", "Successful Take-ons")
    with r3_3: render_metric("Fouls Won", f"{p_fouls_won}", "Free Kicks Earned")
    with r3_4: render_metric("Defensive Vol.", f"{p_def_vol}", "Total Def. Actions")

    # Row 4: Influence & Control
    r4_1, r4_2, r4_3, r4_4 = st.columns(4)
    with r4_1: render_metric("Total Touches", f"{p_vol_val}", "Action Volume")
    with r4_2: render_metric("Ball Receipts", f"{p_receipts}", "Successful Links")
    with r4_3: render_metric("Carries", f"{p_carries}", "Progressive Runs")
    with r4_4: render_metric("Control Security", f"{p_control_sec:.1%}", f"{p_miscontrols} Miscontrols")

    st.divider()

    cp1, cp2, cp3 = st.columns([1.2, 1, 1])
    
    with cp1:
        st.subheader("📍 Positional Influence (Heatmap)")
        pitch_h = Pitch(pitch_type='statsbomb', pitch_color='#0b0e14', line_color='#30363d')
        fig_h, ax_h = pitch_h.draw()
        if not p_data.empty:
            pitch_h.kdeplot(p_data['x'], p_data['y'], ax=ax_h, cmap='viridis', fill=True, levels=50, alpha=0.5)
            pitch_h.scatter(p_data['x'], p_data['y'], s=15, c='white', alpha=0.1, ax=ax_h)
        st.pyplot(fig_h)
        st.caption("Density map showing where the player is most active.")

    with cp2:
        st.subheader("📊 Tactical Radar (8-Axis)")
        # Normalization factors
        max_vol_ref = events.groupby('player', observed=True).size().max()
        max_xg_ref = events.groupby('player', observed=True)['shot_statsbomb_xg'].sum().max()
        
        r_stats = [
            (p_vol_val / max_vol_ref) * 100,
            p_acc * 100,
            (p_xg_val / max(0.1, max_xg_ref)) * 100,
            (p_prog_val / 100) * 100,
            (p_recoveries / 20) * 100,
            (p_duels / 30) * 100,
            (len(p_dribbles) / 20) * 100,
            (len(p_data[p_data['type'] == 'Shot']) / 10) * 100
        ]
        
        theta_stats = ["Volume", "Accuracy", "Creativity", "Verticality", "Defensive", "Duels", "Dribbles", "Shooting"]
        fig_radar_p = go.Figure(data=go.Scatterpolar(r=r_stats, theta=theta_stats, fill='toself', marker_color='#bc8cf2'))
        fig_radar_p.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100])), paper_bgcolor='rgba(0,0,0,0)', font_color="#e6edf3", height=400, margin=dict(l=40, r=40, t=20, b=20))
        st.plotly_chart(fig_radar_p, use_container_width=True)

    with cp3:
        st.subheader("🎯 Primary Pass Links")
        partners_df = p_succ_passes['pass_recipient'].value_counts().head(5).reset_index()
        partners_df.columns = ['Teammate', 'Passes']
        if not partners_df.empty:
            table_html = """
            <table class="pass-table">
                <thead>
                    <tr><th>Teammate</th><th>Passes</th></tr>
                </thead>
                <tbody>
            """
            for _, r_pass in partners_df.iterrows():
                table_html += f"<tr><td>{r_pass['Teammate']}</td><td><b style='color:#58a6ff'>{r_pass['Passes']}</b></td></tr>"
            table_html += "</tbody></table>"
            st.markdown(table_html, unsafe_allow_html=True)
            st.caption("Top 5 teammates receiving successful passes.")
        else:
            st.write("No pass data available.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🕵️ Scout's Role Verdict")
        role_verdict = f"**{selected_p}** is currently operating as a "
        if p_acc > 0.85 and p_vol_val > 50: role_verdict += "**Metronome Playmaker**, ensuring ball security and tempo control. "
        elif p_prog_val > 15: role_verdict += "**Vertical Engine**, focused on breaking lines and territory gain. "
        elif p_recoveries + p_interceptions > 10: role_verdict += "**Defensive Anchor**, specializing in breaking up opposition play. "
        elif p_xg_val > 0.5: role_verdict += "**Shadow Striker**, constantly threatining the goal from advanced positions. "
        else: role_verdict += "**Balanced Contributor**, filling gaps across the tactical setup. "
        
        st.markdown(f"<div class='report-card' style='font-size: 0.95rem; border-left-color: #bc8cf2;'>{role_verdict}</div>", unsafe_allow_html=True)

    st.divider()
    
    # --- Action Specific Event Map (User Request) ---
    col_map1, col_map2 = st.columns([1.5, 1])
    with col_map1:
        st.subheader("🎨 Multi-Action Event Map")
        from matplotlib.colors import LinearSegmentedColormap
        
        touches_list = ["Pass", "Ball Receipt*", "Carry", "Clearance", "Foul Won", "Block", "Ball Recovery", "Duel", "Dribble", "Interception", "Miscontrol", "Shot"]
        
        # Color palette from user
        cmaplist = ["white", "#c3c3c3", "#e21017"]
        cmap_user = LinearSegmentedColormap.from_list("", cmaplist)
        
        pitch_e = Pitch(pitch_type='statsbomb', pitch_color='#0b0e14', line_color='#30363d')
        fig_e, ax_e = pitch_e.draw(figsize=(10, 8))
        
        # Consistent colors for legend
        event_colors = [cmap_user(0.3 + (i / len(touches_list))) for i in range(len(touches_list))]
        
        legend_handles = [
            plt.Line2D([], [], color=event_colors[i], marker='o', linestyle='', markersize=8, label=touches_list[i], markeredgecolor='black')
            for i in range(len(touches_list))
        ]
        
        # Filter and plot
        for i, etype in enumerate(touches_list):
            edf = p_data[p_data['type'] == etype]
            if not edf.empty:
                ax_e.scatter(edf['x'], edf['y'], color=event_colors[i], s=60, edgecolor='black', alpha=0.7, label=etype)
        
        ax_e.legend(handles=legend_handles, fontsize=8, loc='upper left', title="Action Types", facecolor='#161b22', labelcolor='white')
        st.pyplot(fig_e)
        
    with col_map2:
        st.subheader("🏹 Success Pass Vectors")
        pitch_p = Pitch(pitch_type='statsbomb', pitch_color='#0b0e14', line_color='#30363d')
        fig_p, ax_p = pitch_p.draw(figsize=(8, 10))
        if not p_succ_passes.empty:
            pitch_p.arrows(p_succ_passes['x'], p_succ_passes['y'], p_succ_passes['pass_end_x'], p_succ_passes['pass_end_y'], width=1.2, color='#58a6ff', alpha=0.4, ax=ax_p)
        st.pyplot(fig_p)
        st.caption("Visualization of successful pass directionality.")

# -- TAB 4: DUEL COMPARISON --
with tabs[3]:
    st.header("⚔️ Player Battle Arena: Head-to-Head Scout")
    coldu1, coldu2 = st.columns(2)
    with coldu1:
        team_a = st.selectbox("Select Team A", all_nations, index=all_nations.index("England") if "England" in all_nations else 0, key="ca")
        player_a = st.selectbox("Select Player A", sorted(events[events['team'] == team_a]['player'].dropna().unique()), key="pa")
    with coldu2:
        team_b = st.selectbox("Select Team B", all_nations, index=all_nations.index("Spain") if "Spain" in all_nations else 0, key="cb")
        player_b = st.selectbox("Select Player B", sorted(events[events['team'] == team_b]['player'].dropna().unique()), key="pb")

    da = events[events['player'] == player_a].copy()
    db = events[events['player'] == player_b].copy()

    # --- Calculation Function for Duel ---
    def get_detailed_stats(df):
        passes = df[df['type'] == 'Pass']
        shots = df[df['type'] == 'Shot']
        sot = len(shots[shots['shot_outcome'].isin(['Goal', 'Saved', 'Post', 'Saved Off Target', 'Saved to Post'])])
        recoveries = len(df[df['type'] == 'Ball Recovery'])
        interceptions = len(df[df['type'] == 'Interception'])
        blocks = len(df[df['type'] == 'Block'])
        clearances = len(df[df['type'] == 'Clearance'])
        
        return {
            'Vol': len(df),
            'Acc': len(passes[passes['pass_outcome'].isna()]) / max(1, len(passes)),
            'xG': df['shot_statsbomb_xg'].sum(),
            'SOT': sot,
            'Goals': len(shots[shots['shot_outcome'] == 'Goal']),
            'Rec': recoveries,
            'Int': interceptions,
            'Clr': clearances,
            'Blk': blocks,
            'Duel': len(df[df['type'] == 'Duel']),
            'Drib': len(df[df['type'] == 'Dribble']),
            'Foul': len(df[df['type'] == 'Foul Won']),
            'Prog': len(df[df['x'] > 80]),
            'Carry': len(df[df['type'] == 'Carry']),
            'Receipt': len(df[df['type'] == 'Ball Receipt*']),
            'DefVol': recoveries + interceptions + blocks + clearances
        }
    sa = get_detailed_stats(da)
    sb = get_detailed_stats(db)

    # --- 1. Comparative Heatmaps ---
    st.subheader("📍 Positional Face-Off")
    h_col1, h_col2 = st.columns(2)
    with h_col1:
        st.caption(f"{player_a} Activity")
        p1 = Pitch(pitch_type='statsbomb', pitch_color='#0b0e14', line_color='#30363d')
        f1, a1 = p1.draw(figsize=(6, 4))
        if not da.empty: p1.kdeplot(da['x'], da['y'], ax=a1, cmap='Blues', fill=True, levels=50, alpha=0.5)
        st.pyplot(f1)
    with h_col2:
        st.caption(f"{player_b} Activity")
        p2 = Pitch(pitch_type='statsbomb', pitch_color='#0b0e14', line_color='#30363d')
        f2, a2 = p2.draw(figsize=(6, 4))
        if not db.empty: p2.kdeplot(db['x'], db['y'], ax=a2, cmap='Reds', fill=True, levels=50, alpha=0.5)
        st.pyplot(f2)

    st.divider()

    # --- 2. Radar & Bars ---
    r_col1, r_col2 = st.columns([1.5, 1])
    with r_col1:
        st.subheader("📊 8-Axis Tactical Overlay")
        m_v = max(events.groupby('player', observed=True).size().max(), 1)
        m_xg = max(events.groupby('player', observed=True)['shot_statsbomb_xg'].sum().max(), 0.1)
        
        def radar_vals(s):
            return [
                (s['Vol']/m_v)*100, s['Acc']*100, (s['xG']/m_xg)*100, (s['Prog']/100)*100,
                (s['Rec']/20)*100, (s['Duel']/30)*100, (s['Drib']/20)*100, (s['Goals']*20)
            ]
        
        theta = ["Volume", "Accuracy", "Creativity", "Verticality", "Recovery", "Duels", "Dribbles", "Goals"]
        fig_r = go.Figure()
        fig_r.add_trace(go.Scatterpolar(r=radar_vals(sa), theta=theta, fill='toself', name=player_a, marker_color='#58a6ff'))
        fig_r.add_trace(go.Scatterpolar(r=radar_vals(sb), theta=theta, fill='toself', name=player_b, marker_color='#ff4b4b'))
        fig_r.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100])), paper_bgcolor='rgba(0,0,0,0)', font_color="#e6edf3", height=450)
        st.plotly_chart(fig_r, use_container_width=True)

    with r_col2:
        st.subheader("🎯 Direct KPI Matchup")
        metrics = ["Vol", "xG", "Acc", "Prog", "DefVol"]
        for m in metrics:
            val_a = sa[m]
            val_b = sb[m]
            st.write(f"**{m}**")
            total = max(val_a + val_b, 0.1)
            p_a = (val_a / total) * 100
            p_b = (val_b / total) * 100
            display_a = f"{val_a:.2f}" if isinstance(val_a, float) else val_a
            display_b = f"{val_b:.2f}" if isinstance(val_b, float) else val_b
            st.markdown(f"""
                <div style="display:flex; height:12px; border-radius:6px; overflow:hidden; margin-bottom:15px;">
                    <div style="width:{p_a}%; background:#58a6ff;"></div>
                    <div style="width:{p_b}%; background:#ff4b4b;"></div>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-top:-10px;">
                    <span>{display_a}</span>
                    <span>{display_b}</span>
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    # --- 3. 16-KPI Battle Grid ---
    st.subheader("🏆 The Stats Hall of Fame")
    
    def render_duel_kpi(label, val1, val2, rev=False):
        win1 = val1 > val2 if not rev else val1 < val2
        color1 = "#3fb950" if win1 else "#8b949e"
        color2 = "#3fb950" if not win1 and val1 != val2 else "#8b949e"
        v1_disp = f"{val1:.1f}" if isinstance(val1, float) else val1
        v2_disp = f"{val2:.1f}" if isinstance(val2, float) else val2
        return f"""
        <div style='background:rgba(22,27,33,0.4); padding:10px; border-radius:8px; border:1px solid rgba(88,166,255,0.1); margin-bottom:10px;'>
            <div style='font-size:0.75rem; color:#8b949e; text-align:center; font-weight:600;'>{label}</div>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-top:5px;'>
                <span style='color:{color1}; font-weight:700; font-size:1.1rem;'>{v1_disp}</span>
                <span style='color:#58a6ff; font-weight:800;'>VS</span>
                <span style='color:{color2}; font-weight:700; font-size:1.1rem;'>{v2_disp}</span>
            </div>
        </div>
        """

    dk1, dk2, dk3, dk4 = st.columns(4)
    with dk1:
        st.markdown(render_duel_kpi("Accuracy (%)", sa['Acc']*100, sb['Acc']*100), unsafe_allow_html=True)
        st.markdown(render_duel_kpi("Recoveries", sa['Rec'], sb['Rec']), unsafe_allow_html=True)
        st.markdown(render_duel_kpi("Dribbles", sa['Drib'], sb['Drib']), unsafe_allow_html=True)
        st.markdown(render_duel_kpi("Carries", sa['Carry'], sb['Carry']), unsafe_allow_html=True)
    with dk2:
        st.markdown(render_duel_kpi("Expected Goals", sa['xG'], sb['xG']), unsafe_allow_html=True)
        st.markdown(render_duel_kpi("Interceptions", sa['Int'], sb['Int']), unsafe_allow_html=True)
        st.markdown(render_duel_kpi("Duels", sa['Duel'], sb['Duel']), unsafe_allow_html=True)
        st.markdown(render_duel_kpi("Ball Receipts", sa['Receipt'], sb['Receipt']), unsafe_allow_html=True)
    with dk3:
        st.markdown(render_duel_kpi("Shots on Target", sa['SOT'], sb['SOT']), unsafe_allow_html=True)
        st.markdown(render_duel_kpi("Blocks", sa['Blk'], sb['Blk']), unsafe_allow_html=True)
        st.markdown(render_duel_kpi("Fouls Won", sa['Foul'], sb['Foul']), unsafe_allow_html=True)
        st.markdown(render_duel_kpi("Total Touches", sa['Vol'], sb['Vol']), unsafe_allow_html=True)
    with dk4:
        st.markdown(render_duel_kpi("Actual Goals", sa['Goals'], sb['Goals']), unsafe_allow_html=True)
        st.markdown(render_duel_kpi("Clearances", sa['Clr'], sb['Clr']), unsafe_allow_html=True)
        st.markdown(render_duel_kpi("Defensive Vol.", sa['DefVol'], sb['DefVol']), unsafe_allow_html=True)
        st.markdown(render_duel_kpi("Progression", sa['Prog'], sb['Prog']), unsafe_allow_html=True)

    # --- 4. Strategic Duel Summary ---
    st.markdown("### 📝 Strategic Context Summary")
    w_sum = sum(1 for k in sa if sa[k] > sb[k]) - sum(1 for k in sa if sa[k] < sb[k])
    win_p = player_a if w_sum > 0 else player_b
    
    report_duel = f"Tactical analysis indicates **{win_p}** as the more statistically dominant player in this head-to-head. "
    report_duel += f"While {player_a} shows proficiency in its movement patterns, {player_b} counters with significant volume in key areas. "
    st.markdown(f"<div class='report-card' style='border-left-color: #ff4b4b;'>{report_duel}</div>", unsafe_allow_html=True)

# -- TAB 5: SPATIAL TACTICS --
with tabs[4]:
    st.header("Match Intelligence: Positional Nets")
    tm_matches = matches[(matches['home_team'] == target_nation) | (matches['away_team'] == target_nation)].copy()
    tm_matches['opp'] = tm_matches.apply(lambda r: r['away_team'] if r['home_team'] == target_nation else r['home_team'], axis=1)
    
    c_spatial1, c_spatial2 = st.columns([1, 2])
    with c_spatial1:
        sel_opp_val = st.selectbox("Select Match Environment", tm_matches['opp'].unique())
        sel_period = st.radio("Select Match Period", [1, 2], format_func=lambda x: f"{x}st Half" if x==1 else f"{x}nd Half", horizontal=True)

    m_sel_info = tm_matches[tm_matches['opp'] == sel_opp_val]
    
    if not m_sel_info.empty:
        mid_val = m_sel_info['match_id'].iloc[0]
        # Successful passes for the selected period
        me_events = events[(events['match_id'] == mid_val) & (events['team'] == target_nation) & (events['type'] == 'Pass') & (events['pass_outcome'].isna()) & (events['period'] == sel_period)]
        
        if not me_events.empty:
            col_net1, col_net2 = st.columns([2, 1])
            
            # 1. Calculate Node Positions
            avg_nodes_df = me_events.groupby('player').agg(x=('x', 'mean'), y=('y', 'mean'), count=('id', 'size')).reset_index()
            
            # 2. Calculate Pass Links
            pass_links = me_events.groupby(['player', 'pass_recipient']).agg(count=('id', 'size')).reset_index()
            pass_links = pass_links.merge(avg_nodes_df[['player', 'x', 'y']], on='player')
            pass_links = pass_links.merge(avg_nodes_df[['player', 'x', 'y']], left_on='pass_recipient', right_on='player', suffixes=('', '_end'))
            # Filter for density (e.g., at least 2 passes)
            pass_links = pass_links[pass_links['count'] > 2]

            with col_net1:
                pitch_n = Pitch(pitch_type='statsbomb', pitch_color='#0b0e14', line_color='#c1c1c1')
                fig_n, ax_n = pitch_n.draw(figsize=(12, 8))
                
                # Draw Links (Arrows)
                if not pass_links.empty:
                    # Scale arrow width by pass count
                    max_passes = pass_links['count'].max()
                    for _, link in pass_links.iterrows():
                        alpha_val = min(0.1 + (link['count'] / max_passes) * 0.5, 0.6)
                        width_val = (link['count'] / max_passes) * 5
                        pitch_n.arrows(link['x'], link['y'], link['x_end'], link['y_end'], color='#58a6ff', alpha=alpha_val, width=width_val, headwidth=2, headlength=2, ax=ax_n, zorder=1)

                # Draw Nodes
                pitch_n.scatter(avg_nodes_df['x'], avg_nodes_df['y'], s=avg_nodes_df['count']*20, color='#58a6ff', edgecolors='white', linewidth=2, zorder=2, ax=ax_n)
                
                for _, r_node in avg_nodes_df.iterrows():
                    try: 
                        name_display = r_node['player'].split()[-1]
                        pitch_n.annotate(name_display, (r_node['x'], r_node['y'] + 2), c='white', size=11, weight='bold', ax=ax_n, ha='center', zorder=3, path_effects=[path_effects.withStroke(linewidth=3, foreground='#0b0e14')])
                    except: pass
                
                st.pyplot(fig_n)
                st.caption(f"Tactical Network: Successful passes (min. 3) and avg. positions vs {sel_opp_val} ({sel_period}H).")
            
            with col_net2:
                st.subheader("Structure Analytics")
                
                # Top Combinations Table
                st.markdown("#### 🔗 Top Combinations")
                top_combos = pass_links.sort_values('count', ascending=False).head(5)
                if not top_combos.empty:
                    combo_html = "<div style='background:rgba(22,27,33,0.4); padding:10px; border-radius:8px;'>"
                    for _, combo in top_combos.iterrows():
                        p1 = combo['player'].split()[-1]
                        p2 = combo['pass_recipient'].split()[-1]
                        combo_html += f"<div style='display:flex; justify-content:space-between; margin-bottom:5px; border-bottom:1px solid rgba(88,166,255,0.1); padding-bottom:3px;'><span>{p1} ➔ {p2}</span><b style='color:#58a6ff'>{combo['count']}</b></div>"
                    combo_html += "</div>"
                    st.markdown(combo_html, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("Pass Efficiency")
                match_passes = events[(events['match_id'] == mid_val) & (events['team'] == target_nation) & (events['type'] == 'Pass') & (events['period'] == sel_period)]
                pass_dist = match_passes['pass_outcome'].astype(object).fillna('Successful').value_counts().reset_index()
                pass_dist.columns = ['Outcome', 'Count']
                fig_out = px.bar(pass_dist, x='Outcome', y='Count', color='Outcome', color_discrete_map={'Successful': '#3FB950', 'Incomplete': '#e34c26', 'Out': '#8b949e'})
                fig_out.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color="#e6edf3", showlegend=False, height=300)
                st.plotly_chart(fig_out, use_container_width=True)
        else:
            st.warning(f"No successful pass data for {target_nation} in the {sel_period}nd Half.")
    else:
        st.warning("Match configuration not found.")

st.sidebar.caption("Tactical Hub v5.1 | Elite Intelligence")
