import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="US Top 50 Music Analytics",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    df = pd.read_csv("us_top50_cleaned.csv")

    # Convert date
    df["date"] = pd.to_datetime(
        df["date"],
        dayfirst=True,
        errors="coerce"
    )

    # Numeric columns
    numeric_columns = [
        "position",
        "popularity",
        "duration_ms",
        "total_tracks",
        "duration_min",
        "popularity_trend",
        "previous_rank",
        "rank_movement"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    # Explicit status
    df["is_explicit"] = (
        df["is_explicit"]
        .astype(str)
        .str.lower()
        .map({
            "true": True,
            "false": False,
            "1": True,
            "0": False
        })
        .fillna(False)
    )

    return df


df = load_data()

# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown("""
<style>

/* ----------------------------------------------------------
   MAIN BACKGROUND
---------------------------------------------------------- */

.stApp {
    background:
        radial-gradient(
            circle at 10% 10%,
            rgba(99,102,241,0.15),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 90%,
            rgba(20,184,166,0.12),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #070B16 0%,
            #0B1220 50%,
            #101827 100%
        );

    color: #F8FAFC;
}

/* ----------------------------------------------------------
   SIDEBAR
---------------------------------------------------------- */

section[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            #060A13 0%,
            #0C1322 100%
        );

    border-right: 1px solid #263246;
}

/* Sidebar text */

section[data-testid="stSidebar"] * {
    color: #E5E7EB !important;
}

/* ----------------------------------------------------------
   TITLES
---------------------------------------------------------- */

.dashboard-title {

    font-size: 44px;
    font-weight: 850;
    letter-spacing: -1.5px;

    margin-bottom: 5px;

    background:
        linear-gradient(
            90deg,
            #F8FAFC,
            #A5B4FC,
            #5EEAD4
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.page-title {

    font-size: 38px;
    font-weight: 800;
    letter-spacing: -1px;

    margin-bottom: 5px;
}

.subtitle {

    color: #94A3B8;
    font-size: 16px;
    margin-bottom: 25px;
}

/* ----------------------------------------------------------
   KPI CARDS
---------------------------------------------------------- */

.kpi {

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,0.075),
            rgba(255,255,255,0.025)
        );

    border: 1px solid rgba(255,255,255,0.10);

    border-radius: 18px;

    padding: 20px;

    min-height: 110px;

    box-shadow:
        0 10px 35px rgba(0,0,0,0.20);
}

.kpi-label {

    color: #94A3B8;
    font-size: 13px;
    margin-bottom: 8px;
}

.kpi-value {

    color: #F8FAFC;
    font-size: 29px;
    font-weight: 800;
}

.kpi-small {

    color: #64748B;
    font-size: 12px;
}

/* ----------------------------------------------------------
   SECTION HEADERS
---------------------------------------------------------- */

.section {

    font-size: 22px;
    font-weight: 750;

    margin-top: 30px;
    margin-bottom: 15px;

    color: #F1F5F9;
}

/* ----------------------------------------------------------
   FILTER CONTAINER
---------------------------------------------------------- */

.filter-card {

    background:
        rgba(255,255,255,0.035);

    border: 1px solid #263246;

    border-radius: 16px;

    padding: 16px;

    margin-bottom: 15px;
}

/* ----------------------------------------------------------
   SONG CARDS
---------------------------------------------------------- */

.song-card {

    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,0.07),
            rgba(255,255,255,0.025)
        );

    border: 1px solid rgba(255,255,255,0.08);

    border-radius: 18px;

    padding: 15px;

    margin-bottom: 10px;
}

/* ----------------------------------------------------------
   NAVIGATION
---------------------------------------------------------- */

.nav-header {

    font-size: 13px;
    font-weight: 700;

    color: #64748B;

    text-transform: uppercase;

    letter-spacing: 1px;

    margin-bottom: 8px;
}

/* ----------------------------------------------------------
   DIVIDER
---------------------------------------------------------- */

hr {

    border-color: #263246 !important;

}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            font-size:28px;
            font-weight:800;
            margin-bottom:5px;">
            🎧 Music Analytics
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
            color:#64748B;
            font-size:13px;
            margin-bottom:20px;">
            US Top 50 • Interactive Dashboard
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown(
        '<div class="nav-header">Dashboard Modules</div>',
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigate",
        [
            "🏠 Dashboard Overview",
            "🎵 Playlist Timeline Explorer",
            "📈 Song Ranking Trends",
            "👑 Artist Dominance",
            "🎯 Popularity vs Rank",
            "🔥 Explicit Performance"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.markdown("### 📌 Dataset")

    st.write(f"**Records:** {len(df):,}")
    st.write(f"**Songs:** {df['song'].nunique():,}")
    st.write(f"**Artists:** {df['artist'].nunique():,}")

    st.markdown("---")

    st.caption(
        "Built with Python • Pandas • Plotly • Streamlit"
    )


# ============================================================
# COMMON FILTER FUNCTION
# ============================================================

def sidebar_filters(
    show_date=True,
    show_artist=True,
    show_song=True,
    show_rank=True,
    show_album=True
):

    filtered = df.copy()

    st.sidebar.markdown("### 🎛️ Filters")

    # --------------------------------------------------------
    # DATE FILTER
    # --------------------------------------------------------

    if show_date:

        min_date = df["date"].min().date()
        max_date = df["date"].max().date()

        date_range = st.sidebar.date_input(
            "📅 Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        if len(date_range) == 2:

            filtered = filtered[
                (filtered["date"].dt.date >= date_range[0]) &
                (filtered["date"].dt.date <= date_range[1])
            ]

    # --------------------------------------------------------
    # ARTIST FILTER
    # --------------------------------------------------------

    if show_artist:

        artists = sorted(
            df["artist"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_artists = st.sidebar.multiselect(
            "🎤 Artist",
            artists,
            placeholder="All artists"
        )

        if selected_artists:

            filtered = filtered[
                filtered["artist"].isin(
                    selected_artists
                )
            ]

    # --------------------------------------------------------
    # SONG FILTER
    # --------------------------------------------------------

    if show_song:

        songs = sorted(
            df["song"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_songs = st.sidebar.multiselect(
            "🎵 Song",
            songs,
            placeholder="All songs"
        )

        if selected_songs:

            filtered = filtered[
                filtered["song"].isin(
                    selected_songs
                )
            ]

    # --------------------------------------------------------
    # RANK FILTER
    # --------------------------------------------------------

    if show_rank:

        rank_range = st.sidebar.slider(
            "🏆 Rank Range",
            min_value=1,
            max_value=50,
            value=(1, 50)
        )

        filtered = filtered[
            filtered["position"].between(
                rank_range[0],
                rank_range[1]
            )
        ]

    # --------------------------------------------------------
    # ALBUM TYPE
    # --------------------------------------------------------

    if show_album:

        album_types = sorted(
            df["album_type"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_album_types = st.sidebar.multiselect(
            "💿 Album Type",
            album_types,
            default=album_types
        )

        filtered = filtered[
            filtered["album_type"].isin(
                selected_album_types
            )
        ]

    return filtered


# ============================================================
# KPI FUNCTION
# ============================================================
# IMPORTANT:
# Native Streamlit st.metric() is used here.
# Do NOT use HTML <div class="kpi-value"> blocks for KPI values,
# otherwise the HTML can appear as literal text in the app.
# ============================================================

def show_kpis(data):

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "📊 Chart Records",
            f"{len(data):,}"
        )
        st.caption("Filtered records")

    with c2:
        st.metric(
            "🎵 Unique Songs",
            f"{data['song'].nunique():,}"
        )
        st.caption("Songs represented")

    with c3:
        st.metric(
            "🎤 Artists",
            f"{data['artist'].nunique():,}"
        )
        st.caption("Unique artists")

    with c4:
        avg_pop = pd.to_numeric(
            data["popularity"],
            errors="coerce"
        ).mean()

        st.metric(
            "🔥 Avg Popularity",
            f"{avg_pop:.1f}" if pd.notna(avg_pop) else "0.0"
        )
        st.caption("Popularity score")


# ============================================================
# PAGE 1 — DASHBOARD OVERVIEW
# ============================================================

if page == "🏠 Dashboard Overview":

    st.markdown(
        '<div class="dashboard-title">'
        '🎧 US Top 50 Music Analytics'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Explore playlist movement, song rankings, artist dominance '
        'and popularity performance'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # OVERVIEW KPIs
    # --------------------------------------------------------

    show_kpis(df)

    # --------------------------------------------------------
    # TOP SONGS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section">🔥 Top Songs by Popularity</div>',
        unsafe_allow_html=True
    )

    top_songs = (
        df.groupby(["song", "artist"])
        .agg(
            popularity=("popularity", "max"),
            best_rank=("position", "min")
        )
        .reset_index()
        .sort_values(
            "popularity",
            ascending=False
        )
        .head(10)
    )

    fig = px.bar(
        top_songs.sort_values("popularity"),
        x="popularity",
        y="song",
        orientation="h",
        hover_data=[
            "artist",
            "best_rank"
        ],
        title="Top 10 Songs by Popularity"
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=550
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # TWO CHARTS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        artist_counts = (
            df["artist"]
            .value_counts()
            .head(10)
            .reset_index()
        )

        artist_counts.columns = [
            "artist",
            "appearances"
        ]

        fig_artist = px.bar(
            artist_counts.sort_values(
                "appearances"
            ),
            x="appearances",
            y="artist",
            orientation="h",
            title="👑 Top Artists"
        )

        fig_artist.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig_artist,
            use_container_width=True
        )

    with col2:

        explicit_data = (
            df["is_explicit"]
            .map({
                True: "Explicit",
                False: "Non-Explicit"
            })
            .value_counts()
            .reset_index()
        )

        explicit_data.columns = [
            "status",
            "count"
        ]

        fig_exp = px.pie(
            explicit_data,
            names="status",
            values="count",
            hole=0.55,
            title="🔥 Explicit vs Non-Explicit"
        )

        fig_exp.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig_exp,
            use_container_width=True
        )


# ============================================================
# PAGE 2 — PLAYLIST TIMELINE EXPLORER
# ============================================================

elif page == "🎵 Playlist Timeline Explorer":

    st.markdown(
        '<div class="page-title">'
        '🎵 Playlist Timeline Explorer'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Track how songs move through the US Top 50 over time.'
        '</div>',
        unsafe_allow_html=True
    )

    filtered = sidebar_filters(
        show_date=True,
        show_artist=True,
        show_song=True,
        show_rank=True,
        show_album=True
    )

    show_kpis(filtered)

    if len(filtered) == 0:

        st.warning(
            "No songs match the selected filters."
        )

    else:

        st.markdown(
            '<div class="section">'
            '📈 Playlist Ranking Timeline — Clean View'
            '</div>',
            unsafe_allow_html=True
        )

        # ----------------------------------------------------
        # CLEAN SONG SELECTION
        # ----------------------------------------------------
        # A single selected song keeps the timeline simple and
        # avoids overlapping "spaghetti" lines.

        available_songs = sorted(
            filtered["song"].dropna().unique().tolist()
        )

        if available_songs:

            selected_timeline_song = st.selectbox(
                "🎵 Select a song to view",
                available_songs,
                index=0,
                help="Choose one song to see its ranking movement clearly over time."
            )

            timeline_df = filtered[
                filtered["song"] == selected_timeline_song
            ].copy().sort_values("date")

            fig = px.line(
                timeline_df,
                x="date",
                y="position",
                markers=True,
                hover_data=[
                    "artist",
                    "popularity",
                    "rank_movement",
                    "movement_type"
                ],
                title=f"Ranking Movement — {selected_timeline_song}"
            )

            fig.update_yaxes(
                autorange="reversed",
                title="Chart Position",
                dtick=5,
                range=[50.5, 0.5]
            )

            fig.update_xaxes(
                title="Date",
                showgrid=False
            )

            fig.update_traces(
                line=dict(width=3),
                marker=dict(size=7)
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=500,
                hovermode="closest",
                showlegend=False,
                margin=dict(
                    l=55,
                    r=25,
                    t=75,
                    b=55
                )
            )

            st.caption(
                "Clean single-song timeline: rank 1 is shown at the top. "
                "Select another song above to change the view."
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # ----------------------------------------------------
        # MOVEMENT ANALYSIS
        # ----------------------------------------------------

        st.markdown(
            '<div class="section">'
            '↕️ Ranking Movement Analysis'
            '</div>',
            unsafe_allow_html=True
        )

        movement = (
            filtered["movement_type"]
            .value_counts()
            .reset_index()
        )

        movement.columns = [
            "movement",
            "count"
        ]

        fig2 = px.bar(
            movement,
            x="movement",
            y="count",
            title="Movement Type Distribution"
        )

        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )


# ============================================================
# PAGE 3 — SONG RANKING TRENDS
# ============================================================

elif page == "📈 Song Ranking Trends":

    st.markdown(
        '<div class="page-title">'
        '📈 Song Ranking Trends'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Analyze how individual songs rise and fall within the Top 50.'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------

    st.sidebar.markdown("### 🎛️ Song Controls")

    selected_song = st.sidebar.selectbox(
        "🎵 Select Song",
        sorted(
            df["song"]
            .dropna()
            .unique()
        )
    )

    rank_range = st.sidebar.slider(
        "🏆 Rank Range",
        1,
        50,
        (1, 50)
    )

    song_df = df[
        df["song"] == selected_song
    ].copy()

    song_df = song_df[
        song_df["position"].between(
            rank_range[0],
            rank_range[1]
        )
    ]

    # --------------------------------------------------------
    # SONG INFORMATION
    # --------------------------------------------------------

    if len(song_df) > 0:

        artist_name = song_df["artist"].iloc[0]

        best_rank = int(
            song_df["position"].min()
        )

        avg_rank = song_df["position"].mean()

        max_popularity = song_df["popularity"].max()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "🎵 Song",
            selected_song
        )

        c2.metric(
            "🎤 Artist",
            artist_name
        )

        c3.metric(
            "🏆 Best Rank",
            best_rank
        )

        c4.metric(
            "🔥 Peak Popularity",
            int(max_popularity)
        )

        # ----------------------------------------------------
        # RANK TREND
        # ----------------------------------------------------

        st.markdown(
            '<div class="section">'
            '🏆 Ranking Journey'
            '</div>',
            unsafe_allow_html=True
        )

        fig = px.line(
            song_df,
            x="date",
            y="position",
            markers=True,
            hover_data=[
                "popularity",
                "rank_movement",
                "movement_type"
            ]
        )

        fig.update_yaxes(
            autorange="reversed",
            title="Chart Position",
            dtick=5
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ----------------------------------------------------
        # POPULARITY TREND
        # ----------------------------------------------------

        st.markdown(
            '<div class="section">'
            '🔥 Popularity Trend'
            '</div>',
            unsafe_allow_html=True
        )

        fig2 = px.area(
            song_df,
            x="date",
            y="popularity",
            title="Popularity Over Time"
        )

        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        # ----------------------------------------------------
        # MOVEMENT TABLE
        # ----------------------------------------------------

        st.markdown(
            '<div class="section">'
            '↕️ Ranking Movement History'
            '</div>',
            unsafe_allow_html=True
        )

        movement_table = song_df[
            [
                "date",
                "position",
                "previous_rank",
                "rank_movement",
                "movement_type",
                "popularity"
            ]
        ].sort_values(
            "date",
            ascending=False
        )

        st.dataframe(
            movement_table,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "No data available for the selected rank range."
        )


# ============================================================
# PAGE 4 — ARTIST DOMINANCE
# ============================================================

elif page == "👑 Artist Dominance":

    st.markdown(
        '<div class="page-title">'
        '👑 Artist Dominance Leaderboard'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Discover which artists dominate the US Top 50.'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    filtered = sidebar_filters(
        show_date=True,
        show_artist=False,
        show_song=False,
        show_rank=True,
        show_album=True
    )

    st.sidebar.markdown("### 👑 Leaderboard")

    top_n = st.sidebar.slider(
        "Show Top Artists",
        5,
        30,
        10
    )

    # --------------------------------------------------------
    # LEADERBOARD
    # --------------------------------------------------------

    leaderboard = (
        filtered
        .groupby("artist")
        .agg(
            appearances=("song", "count"),
            unique_songs=("song", "nunique"),
            avg_rank=("position", "mean"),
            best_rank=("position", "min"),
            avg_popularity=("popularity", "mean")
        )
        .reset_index()
        .sort_values(
            "appearances",
            ascending=False
        )
        .head(top_n)
    )

    if len(leaderboard) > 0:

        # ----------------------------------------------------
        # KPI
        # ----------------------------------------------------

        top_artist = leaderboard.iloc[0]

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "👑 #1 Artist",
            top_artist["artist"]
        )

        c2.metric(
            "📊 Appearances",
            int(top_artist["appearances"])
        )

        c3.metric(
            "🎵 Songs",
            int(top_artist["unique_songs"])
        )

        c4.metric(
            "🏆 Best Rank",
            int(top_artist["best_rank"])
        )

        # ----------------------------------------------------
        # BAR CHART
        # ----------------------------------------------------

        fig = px.bar(
            leaderboard.sort_values(
                "appearances"
            ),
            x="appearances",
            y="artist",
            orientation="h",
            hover_data=[
                "unique_songs",
                "avg_rank",
                "best_rank",
                "avg_popularity"
            ],
            title="Artist Dominance by Chart Appearances"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=600
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ----------------------------------------------------
        # AVG POPULARITY
        # ----------------------------------------------------

        fig2 = px.scatter(
            leaderboard,
            x="avg_rank",
            y="avg_popularity",
            size="appearances",
            hover_name="artist",
            hover_data=[
                "unique_songs",
                "best_rank"
            ],
            title="Artist Average Rank vs Popularity"
        )

        fig2.update_xaxes(
            autorange="reversed"
        )

        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=500
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        # ----------------------------------------------------
        # TABLE
        # ----------------------------------------------------

        st.markdown(
            '<div class="section">'
            '📋 Complete Artist Leaderboard'
            '</div>',
            unsafe_allow_html=True
        )

        st.dataframe(
            leaderboard,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "No artist data matches your filters."
        )


# ============================================================
# PAGE 5 — POPULARITY VS RANK
# ============================================================

elif page == "🎯 Popularity vs Rank":

    st.markdown(
        '<div class="page-title">'
        '🎯 Popularity vs Rank'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Understand the relationship between popularity and chart ranking.'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    filtered = sidebar_filters(
        show_date=True,
        show_artist=True,
        show_song=False,
        show_rank=True,
        show_album=True
    )

    if len(filtered) > 0:

        # ----------------------------------------------------
        # SCATTER
        # ----------------------------------------------------

        fig = px.scatter(
            filtered,
            x="position",
            y="popularity",
            color="album_type",
            size="popularity",
            hover_name="song",
            hover_data=[
                "artist",
                "date",
                "rank_movement",
                "movement_type"
            ],
            title="Popularity vs Chart Position"
        )

        # Rank 1 at left/top interpretation
        fig.update_xaxes(
            autorange="reversed",
            title="Chart Rank"
        )

        fig.update_yaxes(
            title="Popularity Score"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=650
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ----------------------------------------------------
        # CORRELATION
        # ----------------------------------------------------

        correlation = filtered[
            ["position", "popularity"]
        ].corr().iloc[0, 1]

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "📊 Correlation",
            f"{correlation:.2f}"
        )

        c2.metric(
            "🔥 Avg Popularity",
            f"{filtered['popularity'].mean():.1f}"
        )

        c3.metric(
            "🏆 Avg Rank",
            f"{filtered['position'].mean():.1f}"
        )

        # ----------------------------------------------------
        # ALBUM TYPE COMPARISON
        # ----------------------------------------------------

        st.markdown(
            '<div class="section">'
            '💿 Album Type Performance'
            '</div>',
            unsafe_allow_html=True
        )

        album_summary = (
            filtered
            .groupby("album_type")
            .agg(
                avg_rank=("position", "mean"),
                avg_popularity=("popularity", "mean"),
                songs=("song", "nunique")
            )
            .reset_index()
        )

        fig2 = px.bar(
            album_summary,
            x="album_type",
            y="avg_popularity",
            hover_data=[
                "avg_rank",
                "songs"
            ],
            title="Average Popularity by Album Type"
        )

        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    else:

        st.warning(
            "No data matches the selected filters."
        )


# ============================================================
# PAGE 6 — EXPLICIT VS NON-EXPLICIT PERFORMANCE
# ============================================================

elif page == "🔥 Explicit Performance":

    st.markdown(
        '<div class="page-title">'
        '🔥 Explicit vs Non-Explicit Performance'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Compare ranking and popularity performance between '
        'explicit and non-explicit songs.'
        '</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    filtered = sidebar_filters(
        show_date=True,
        show_artist=True,
        show_song=False,
        show_rank=True,
        show_album=True
    )

    if len(filtered) > 0:

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        filtered = filtered.copy()

        filtered["Explicit Status"] = (
            filtered["is_explicit"]
            .map({
                True: "Explicit",
                False: "Non-Explicit"
            })
        )

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        summary = (
            filtered
            .groupby("Explicit Status")
            .agg(
                songs=("song", "nunique"),
                appearances=("song", "count"),
                avg_rank=("position", "mean"),
                best_rank=("position", "min"),
                avg_popularity=("popularity", "mean"),
                max_popularity=("popularity", "max")
            )
            .reset_index()
        )

        # ----------------------------------------------------
        # KPI CARDS
        # ----------------------------------------------------
        # Native Streamlit metrics are used instead of custom HTML.

        col1, col2 = st.columns(2)

        for i, (_, row) in enumerate(summary.iterrows()):

            if i >= 2:
                break

            target_col = col1 if i == 0 else col2

            with target_col:

                status = row["Explicit Status"]

                label = (
                    "🔥 Explicit"
                    if status == "Explicit"
                    else "🎵 Non-Explicit"
                )

                st.metric(
                    label,
                    f"{int(row['songs']):,} Songs"
                )

                st.caption(
                    f"Avg Rank: {row['avg_rank']:.1f}  •  "
                    f"Avg Popularity: {row['avg_popularity']:.1f}"
                )

        # ----------------------------------------------------
        # POPULARITY BOX PLOT
        # ----------------------------------------------------

        st.markdown(
            '<div class="section">'
            '📊 Popularity Comparison'
            '</div>',
            unsafe_allow_html=True
        )

        fig = px.box(
            filtered,
            x="Explicit Status",
            y="popularity",
            points="outliers",
            hover_data=[
                "song",
                "artist"
            ],
            title="Popularity Distribution"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ----------------------------------------------------
        # RANK COMPARISON
        # ----------------------------------------------------

        st.markdown(
            '<div class="section">'
            '🏆 Ranking Performance'
            '</div>',
            unsafe_allow_html=True
        )

        rank_summary = (
            filtered
            .groupby("Explicit Status")
            .agg(
                avg_rank=("position", "mean"),
                best_rank=("position", "min")
            )
            .reset_index()
        )

        fig2 = px.bar(
            rank_summary,
            x="Explicit Status",
            y="avg_rank",
            text_auto=".1f",
            title="Average Chart Position"
        )

        fig2.update_yaxes(
            autorange="reversed"
        )

        fig2.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        # ----------------------------------------------------
        # SONG COUNT
        # ----------------------------------------------------

        st.markdown(
            '<div class="section">'
            '🎵 Song Distribution'
            '</div>',
            unsafe_allow_html=True
        )

        song_count = (
            filtered
            .groupby("Explicit Status")["song"]
            .nunique()
            .reset_index()
        )

        song_count.columns = [
            "status",
            "songs"
        ]

        fig3 = px.pie(
            song_count,
            names="status",
            values="songs",
            hole=0.55,
            title="Explicit vs Non-Explicit Songs"
        )

        fig3.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            fig3,
            use_container_width=True
        )

        # ----------------------------------------------------
        # SUMMARY TABLE
        # ----------------------------------------------------

        st.markdown(
            '<div class="section">'
            '📋 Performance Summary'
            '</div>',
            unsafe_allow_html=True
        )

        st.dataframe(
            summary,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "No data matches the selected filters."
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align:center;
        color:#64748B;
        font-size:12px;
        padding:10px;">
        🎧 US Top 50 Music Analytics Dashboard
        &nbsp; • &nbsp;
        Python + Pandas + Plotly + Streamlit
    </div>
    """,
    unsafe_allow_html=True
)