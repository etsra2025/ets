import streamlit as st
import random
import pandas as pd
from typing import Dict, List, Optional, Callable

def render_tile(tile_idx: int, tile: Dict):
    """Render a single tile"""
    players_here = [p for p in st.session_state.players if p.position == tile_idx]
    player_indicators = " ".join(["⚫" if p.color == COLORS['red'] else "⚪" for p in players_here])
    
    text_color = 'white' if tile['color'] in [COLORS['black'], COLORS['dark_gray'], COLORS['cyan']] else 'black'
    
    st.markdown(f"""
    <div class="tile-card" style="background-color:{tile['color']}; color:{text_color}; text-align: center; padding: 8px; border-radius: 8px; border: 2px solid #000; height: 80px; display: flex; flex-direction: column; justify-content: center; align-items: center; font-size: 0.75rem; font-weight: bold;">
        <div style="line-height: 1.1;">{tile['text']}</div>
        <div style="margin-top: 4px; font-size: 1rem;">{player_indicators}</div>
    </div>
    """, unsafe_allow_html=True)

# Page configuration
st.set_page_config(
    page_title="Gujarat ETS - Emission Trading Simulation",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# JPAL Color Scheme
COLORS = {
    'black': '#000000',
    'white': '#FFFFFF', 
    'dark_gray': '#646464',
    'medium_gray': '#919191',
    'light_gray': '#CACACA',
    'red': '#E35925',
    'teal': '#2FAA9F',
    'yellow': '#F4C300',
    'green': '#4A9C65',
    'cyan': '#2D616E'
}

# Game Parameters
LARGE = {"produce": 10000.0, "pollution": 100000.0}
SMALL = {"produce": 2000.0, "pollution": 20000.0}
PERMIT_PRICE = 5.0
PRODUCE_PRICE = 1000.0
DEFAULT_MARKET_CAP = 200000
INDUSTRY_ALLOCATION_PERCENT = 80
MARKET_ALLOCATION_PERCENT = 20
MAX_PERMIT_HOLDING_PERCENT = 150

# Cached CSS to avoid re-rendering
@st.cache_data
def get_custom_css():
    return f"""
    <style>
        /* Force light theme for the entire app */
        .stApp {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }}

        /* Universal text color override - most aggressive approach */
        * {{
            color: #000000 !important;
        }}

        /* Make only H1 white - override universal rule */
        .main .block-container h1,
        .main-header h1, 
        .main-header p {{
            color: #FFFFFF !important;
        }}

        /* Sidebar text should be black for better readability */
        .css-1d391kg *,
        .css-1d391kg .stMarkdown *, 
        .css-1d391kg .stText *,
        .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, 
        .css-1d391kg h4, .css-1d391kg h5, .css-1d391kg h6,
        .css-1d391kg p, .css-1d391kg div, .css-1d391kg span,
        .css-1d391kg label,
        section[data-testid="stSidebar"] *,
        .stSidebar * {{
            color: #000000 !important;
            text-shadow: none !important;
        }}

        /* Fix input boxes to be white with black text like buttons */
        .stNumberInput input,
        .stTextInput input,
        .stSelectbox select,
        input[type="number"],
        input[type="text"],
        select {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 2px solid #333333 !important;
        }}

        /* Fix the +/- increment/decrement buttons on number inputs */
        .stNumberInput button,
        .stNumberInput [data-testid="stNumberInputStepUp"],
        .stNumberInput [data-testid="stNumberInputStepDown"],
        [data-testid="stNumberInput"] button,
        input[type="number"]::-webkit-outer-spin-button,
        input[type="number"]::-webkit-inner-spin-button {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 2px solid #333333 !important;
        }}

        /* Target the step buttons more specifically */
        .step-up,
        .step-down,
        [class*="step"] {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 2px solid #333333 !important;
        }}

        /* Target Streamlit's input containers */
        [data-testid="stNumberInput"] input,
        [data-testid="stTextInput"] input,
        [data-testid="stSelectbox"] select {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 2px solid #333333 !important;
        }}

        /* Also target the input wrapper divs */
        .stNumberInput > div > div > input,
        .stTextInput > div > div > input {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 2px solid #333333 !important;
        }}

        /* Target any input elements in the sidebar specifically */
        .css-1d391kg input,
        section[data-testid="stSidebar"] input,
        .stSidebar input {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 2px solid #333333 !important;
        }}

        /* Also target sidebar +/- buttons */
        .css-1d391kg button,
        section[data-testid="stSidebar"] button,
        .stSidebar button {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
            border: 2px solid #333333 !important;
        }}

        /* Main content area - VERY aggressive black text enforcement */
        .main .block-container *:not(.main-header *),
        .main .element-container *,
        .main [data-testid="stText"] *,
        .main [data-testid="stMarkdown"] *,
        .main [data-testid="stInfo"] *,
        .main [data-testid="stWarning"] *,
        .main [data-testid="stAlert"] *,
        .main [data-testid="stSuccess"] *,
        .main [data-testid="stError"] *,
        .main div:not(.main-header *),
        .main p:not(.main-header *),
        .main span:not(.main-header *) {{
            color: #000000 !important;
        }}

        /* Force all text elements in main to be black - nuclear option */
        .main {{
            color: #000000 !important;
        }}
        
        .main * {{
            color: #000000 !important;
        }}

        /* Re-override for header and sidebar after nuclear option */
        .main-header,
        .main-header * {{
            color: #FFFFFF !important;
        }}

        /* Success/Error/Warning custom classes should keep their colors */
        .success,
        .success * {{
            color: white !important;
        }}
        
        .danger,
        .danger * {{
            color: white !important;
        }}
        
        .warning,
        .warning * {{
            color: black !important;
        }}

                
        /* Main content area */
        .main .block-container {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }}
        
        /* Sidebar styling - more comprehensive selectors */
        .css-1d391kg,
        section[data-testid="stSidebar"],
        .stSidebar {{
            background-color: #FFFFFF !important;
        }}
        
        /* Fix the top right toolbar/header bar to be white */
        .stApp > header,
        [data-testid="stHeader"],
        .css-18e3th9,
        .css-1544g2n,
        .main > div:first-child,
        .block-container > div:first-child {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }}

        /* Target the specific top toolbar elements */
        .stApp > header *,
        [data-testid="stHeader"] *,
        .css-18e3th9 *,
        .css-1544g2n * {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }}

        /* Also target any fixed position elements that might be the black bar */
        [style*="position: fixed"],
        [style*="position:fixed"] {{
            background-color: #FFFFFF !important;
            color: #000000 !important;
        }}
        
        .main-header {{
            background: linear-gradient(90deg, {COLORS['teal']}, {COLORS['cyan']});
            padding: 1rem;
            border-radius: 10px;
            color: white !important;
            text-align: center;
            margin-bottom: 2rem;
        }}
        
        .main-header h1, .main-header p {{
            color: white !important;
        }}
        
        .player-card {{
            border: 2px solid {COLORS['medium_gray']};
            border-radius: 10px;
            padding: 1rem;
            margin: 0.5rem 0;
            background-color: #F8F9FA;
            color: #000000 !important;
        }}
        
        .player-card h3, .player-card p, .player-card strong {{
            color: #000000 !important;
        }}
        
        .active-player {{
            border-color: {COLORS['green']};
            background-color: #e8f5e8;
            color: #000000 !important;
        }}
        
        .active-player h3, .active-player p, .active-player strong {{
            color: #000000 !important;
        }}
        
        .tile-card {{
            border: 2px solid {COLORS['black']};
            border-radius: 8px;
            padding: 0.5rem;
            margin: 0.2rem;
            text-align: center;
            font-size: 0.8rem;
            font-weight: bold;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }}
        
        .metric-card {{
            background-color: #F0F2F6;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
            color: #000000 !important;
        }}
        
        .metric-card h2, .metric-card h4 {{
            color: #000000 !important;
        }}
        
        .success {{
            background-color: {COLORS['green']};
            color: white !important;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }}
        
        .warning {{
            background-color: {COLORS['yellow']};
            color: black !important;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }}
        
        .danger {{
            background-color: {COLORS['red']};
            color: white !important;
            padding: 1rem;
            border-radius: 8px;
            text-align: center;
        }}
        
        /* Primary buttons - Green for Start Game */
        .stButton > button[kind="primary"] {{
            background-color: {COLORS['green']} !important;
            color: white !important;
            border: none !important;
            font-weight: bold;
        }}
        
        
        /* Style ONLY Buy Equipment and Skip Investment buttons */
        div[data-testid="stButton"] > button[aria-label="buy_equipment_btn"],
        div[data-testid="stButton"] > button[aria-label="skip_investment_btn"] {{
            background-color: #f8f9fa !important;
            color: #000000 !important;
            border: 2px solid #333333 !important;
            font-weight: bold;}}
        
        /* All other buttons - Light background with black text for better contrast */
        .stButton > button {{
            background-color: #f8f9fa !important;
            color: #000000 !important;
            border: 2px solid #333333 !important;
            font-weight: bold;
        }}
        
        /* Force text color on all button text spans */
        .stButton > button span {{
            color: #000000 !important;
        }}
        
        /* Override for primary and secondary button text */
        .stButton > button[kind="primary"] span {{
            color: white !important;
        }}
        
        .stButton > button[kind="secondary"] span {{
            color: white !important;
        }}
        
        /* Hover effects */
        .stButton > button:hover {{
            opacity: 0.8;
        }}
        
        /* Ensure dataframes are readable */
        .dataframe {{
            background-color: white !important;
            color: black !important;
        }}
        
        /* Metrics styling */
        [data-testid="metric-container"] {{
            background-color: #F0F2F6;
            border: 1px solid #E1E5E9;
            padding: 1rem;
            border-radius: 8px;
        }}
        
        [data-testid="metric-container"] > div {{
            color: #000000 !important;
        }}
    </style>
    """

# Helper functions
def rint(x: float) -> int:
    return int(round(x))

def money(x: float) -> str:
    return f"₹{rint(x):,}"

def format_number(x: float) -> str:
    return f"{rint(x):,}"

# Player class
class Player:
    def __init__(self, name: str, kind_dict: Dict, color: str, market_cap: int, num_players: int):
        self.name = name
        self.kind_name = "Large" if kind_dict is LARGE else "Small"
        self.produce = float(kind_dict["produce"])
        self.pollution = float(kind_dict["pollution"])
        
        # Calculate initial allocation
        total_pollution = LARGE["pollution"] + SMALL["pollution"] if num_players == 2 else kind_dict["pollution"]
        pollution_share = self.pollution / total_pollution if num_players == 2 else 1.0
        industry_allocation = market_cap * (INDUSTRY_ALLOCATION_PERCENT / 100)
        
        self.initial_permits = rint(industry_allocation * pollution_share)
        self.permits = self.initial_permits
        self.max_permits = rint(self.initial_permits * (MAX_PERMIT_HOLDING_PERCENT / 100))
        
        self.revenue = self.produce * PRODUCE_PRICE
        self.earnings = float(self.revenue)
        self.total_cost = 0.0
        self.permit_cost = 0.0
        
        self.position = 0
        self.color = color
        self.finished = False

    def roll(self) -> int:
        return random.randint(1, 6)

# Effect functions
def client_order_effect(p: Player, multiplier: float):
    pre = p.produce
    p.produce *= (1 + multiplier)
    p.pollution *= (1 + multiplier)
    p.earnings += multiplier * pre * PRODUCE_PRICE

def abatement_effect(p: Player, cost: float, multiplier: float):
    st.session_state.pending_investment = {
        'player': p, 'cost': cost, 'multiplier': multiplier, 'type': 'abatement'
    }

def maintenance_effect(p: Player, cost: float, multiplier: float):
    st.session_state.pending_investment = {
        'player': p, 'cost': cost, 'multiplier': multiplier, 'type': 'maintenance'
    }

def cost_effect(p: Player, cost: float):
    p.earnings -= cost
    p.total_cost += cost

def tax_effect(p: Player):
    loss = 200.0 * 0.5 * p.produce
    p.earnings -= loss
    p.total_cost += loss

def order_cancel_effect(p: Player, multiplier: float):
    pre = p.produce
    p.produce *= multiplier
    p.pollution *= multiplier
    p.earnings -= (1 - multiplier) * pre * PRODUCE_PRICE

# Tile definitions - cached for better performance - Updated for 5x5 grid
@st.cache_data
def get_tile_rules():
    return [
        {"text": "Uniform Auction GO\nTrue-up period", "color": COLORS['dark_gray']},  # 0 (corner)
        {"text": "Unseasonal Rains\nPollution -0.1%", "color": COLORS['white']},      # 1
        {"text": "CEMS Issue\nEmissions +20%", "color": COLORS['white']},           # 2
        {"text": "Client Order\nProduction +30%", "color": COLORS['white']},        # 3
        {"text": "Abatement\n₹20L, -40%", "color": COLORS['teal']},                 # 4 (corner)
        {"text": "Advanced Abate\n₹40L, -60%", "color": COLORS['teal']},            # 5
        {"text": "CEMS Issue\nEmissions +10%", "color": COLORS['white']},           # 6
        {"text": "Bird's Nest\nPay ₹5,000", "color": COLORS['white']},              # 7
        {"text": "Client Order\nProduction +10%", "color": COLORS['white']},        # 8 (corner)
        {"text": "Tax Issue\n50% at ₹800", "color": COLORS['white']},               # 9
        {"text": "CEMS Issue\nEmissions +30%", "color": COLORS['white']},           # 10
        {"text": "Hire Additional Maintenance\n₹1L, -10%", "color": COLORS['cyan']}, # 11
        {"text": "Hire Additional Maintenance Staff\n₹1.5L, -15%", "color": COLORS['cyan']}, # 12 (corner)
        {"text": "Client Order Cancel, -5%", "color": COLORS['white']},             # 13
        {"text": "CEMS Data Quality Issue\nImputation, +10%", "color": COLORS['white']}, # 14
        {"text": "Client Order Cancel, -5%", "color": COLORS['white']},             # 15
    ]

def get_tile_effects():
    return [
        lambda p: None,  # GO
        lambda p: setattr(p, "pollution", p.pollution * 0.999),  # Rain
        lambda p: setattr(p, "pollution", p.pollution * 1.20),   # CEMS +20%
        lambda p: client_order_effect(p, 0.30),                  # Client +30%
        lambda p: abatement_effect(p, 2000000, 0.6),            # Abatement
        lambda p: abatement_effect(p, 4000000, 0.4),            # Advanced
        lambda p: setattr(p, "pollution", p.pollution * 1.10),  # CEMS +10%
        lambda p: cost_effect(p, 5000),                         # Bird's Nest
        lambda p: client_order_effect(p, 0.10),                 # Client +10%
        lambda p: tax_effect(p),                                # Tax
        lambda p: setattr(p, "pollution", p.pollution * 1.30),  # CEMS +30%
        lambda p: maintenance_effect(p, 100000, 0.9),           # Maintenance
        lambda p: maintenance_effect(p, 150000, 0.85),          # Maintenance Staff
        lambda p: order_cancel_effect(p, 0.95),                 # Order Cancel
        lambda p: setattr(p, "pollution", p.pollution * 1.10),  # Data Quality
        lambda p: order_cancel_effect(p, 0.95),                 # Order Cancel
    ]

# Initialize session state
def init_session_state():
    defaults = {
        'players': [],
        'current_turn': 0,
        'market_permits': 0,
        'game_started': False,
        'game_over': False,
        'tile_rules': get_tile_rules(),
        'tile_effects': get_tile_effects(),
        'pending_investment': None,
        'last_roll': None,
        'game_log': []
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def render_game_board():
    """Render the game board as a 5x5 square grid using Streamlit columns"""
    st.header("Game Board")
    
    tiles = st.session_state.tile_rules
    
    # Create a 5x5 grid layout
    # The board follows this pattern (like Monopoly):
    # Row 1 (top): tiles 12, 11, 10, 9, 8 (reverse order)
    # Row 2: tile 13, empty, empty, empty, 7
    # Row 3: tile 14, empty, empty, empty, 6
    # Row 4: tile 15, empty, empty, empty, 5
    # Row 5 (bottom): tiles 0, 1, 2, 3, 4 (normal order)
    
    # Row 1 (top): tiles 12, 11, 10, 9, 8
    cols1 = st.columns(5)
    top_tiles = [12, 11, 10, 9, 8]
    for i, tile_idx in enumerate(top_tiles):
        with cols1[i]:
            render_tile(tile_idx, tiles[tile_idx])
    
    # Row 2: tile 13, empty, empty, empty, 7
    cols2 = st.columns(5)
    with cols2[0]:
        render_tile(13, tiles[13])
    for i in range(1, 4):
        with cols2[i]:
            st.markdown('<div style="height: 80px;"></div>', unsafe_allow_html=True)
    with cols2[4]:
        render_tile(7, tiles[7])
    
    # Row 3: tile 14, empty, empty, empty, 6
    cols3 = st.columns(5)
    with cols3[0]:
        render_tile(14, tiles[14])
    for i in range(1, 4):
        with cols3[i]:
            st.markdown('<div style="height: 80px;"></div>', unsafe_allow_html=True)
    with cols3[4]:
        render_tile(6, tiles[6])
    
    # Row 4: tile 15, empty, empty, empty, 5
    cols4 = st.columns(5)
    with cols4[0]:
        render_tile(15, tiles[15])
    for i in range(1, 4):
        with cols4[i]:
            st.markdown('<div style="height: 80px;"></div>', unsafe_allow_html=True)
    with cols4[4]:
        render_tile(5, tiles[5])
    
    # Row 5 (bottom): tiles 0, 1, 2, 3, 4
    cols5 = st.columns(5)
    bottom_tiles = [0, 1, 2, 3, 4]
    for i, tile_idx in enumerate(bottom_tiles):
        with cols5[i]:
            render_tile(tile_idx, tiles[tile_idx])

def render_player_status():
    """Render player status cards"""
    st.header("Industry Status")
    
    cols = st.columns(2)
    for i, player in enumerate(st.session_state.players):
        with cols[i]:
            is_active = (i == st.session_state.current_turn and 
                        st.session_state.game_started and 
                        not st.session_state.game_over)
            card_class = "active-player" if is_active else "player-card"
            
            st.markdown(f"""
            <div class="{card_class}">
                <h3>{player.name} ({player.kind_name}) {'🟩' if is_active else ''}</h3>
                <p><strong>Position:</strong> Tile {player.position}</p>
                <p><strong>Production:</strong> {format_number(player.produce)} units</p>
                <p><strong>Pollution:</strong> {format_number(player.pollution)} kg</p>
                <p><strong>Permits:</strong> {player.permits:,} / {player.max_permits:,}</p>
                <p><strong>Revenue:</strong> {money(player.revenue)}</p>
                <p><strong>Earnings:</strong> {money(player.earnings)}</p>
            </div>
            """, unsafe_allow_html=True)

def render_market_status(market_cap: int, permit_price: float):
    """Render market status"""
    st.header("Market Status")
    
    cols = st.columns(3)
    metrics = [
        ("Market Cap", f"{format_number(market_cap)} kg"),
        ("Available Permits", f"{st.session_state.market_permits:,}"),
        ("Permit Price", f"₹{permit_price:.1f}")
    ]
    
    for col, (title, value) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <h4>{title}</h4>
                <h2>{value}</h2>
            </div>
            """, unsafe_allow_html=True)

def handle_dice_roll():
    """Handle dice rolling logic"""
    current_player = st.session_state.players[st.session_state.current_turn]
    roll = current_player.roll()
    st.session_state.last_roll = roll
    
    # Move player
    old_pos = current_player.position
    current_player.position = (current_player.position + roll) % len(st.session_state.tile_rules)
    
    # Apply tile effect
    st.session_state.tile_effects[current_player.position](current_player)
    
    # Normalize values
    current_player.produce = float(rint(current_player.produce))
    current_player.pollution = float(rint(current_player.pollution))
    
    # Log the move
    tile_name = st.session_state.tile_rules[current_player.position]["text"].split('\n')[0]
    st.session_state.game_log.append(f"{current_player.name} rolled {roll} and moved to {tile_name}")
    
    # Check if completed circuit
    if old_pos != 0 and current_player.position == 0:
        current_player.finished = True
        st.session_state.game_log.append(f"{current_player.name} completed the circuit!")
        
        if all(p.finished for p in st.session_state.players):
            st.session_state.game_over = True
    
    # Next turn
    if not st.session_state.game_over:
        st.session_state.current_turn = (st.session_state.current_turn + 1) % 2

def render_final_results(market_cap: int):
    """Render final game results"""
    st.header("Final Results")
    
    total_pollution = sum(p.pollution for p in st.session_state.players)
    total_permits = sum(p.permits for p in st.session_state.players)
    all_compliant = all(p.pollution <= p.permits for p in st.session_state.players)
    
    # Results summary
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Pollution", f"{format_number(total_pollution)} kg")
        st.metric("Total Permits", f"{format_number(total_permits)}")
    
    with col2:
        st.metric("Market Cap", f"{format_number(market_cap)} kg")
        excess = max(0, total_pollution - market_cap)
        st.metric("Excess Pollution", f"{format_number(excess)} kg")
    
    # Victory conditions
    if total_pollution <= market_cap:
        if all_compliant:
            st.markdown("""
            <div class="success">
                🎉 EVERYONE WINS! 🎉<br>
                The cap-and-trade system worked!<br>
                Environmental goals achieved with economic flexibility.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning">
                ⚠️ PARTIAL SUCCESS ⚠️<br>
                Market cap achieved but compliance issues exist.<br>
                Some regulatory enforcement needed.
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="danger">
            ❌ EVERYONE LOSES ❌<br>
            Market cap exceeded - environmental damage occurred!<br>
            The cap-and-trade system failed to control pollution.
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed player results
    st.subheader("Player Details")
    results_data = []
    for player in st.session_state.players:
        compliance = "✅ Compliant" if player.pollution <= player.permits else "❌ Deficit"
        deficit = max(0, player.pollution - player.permits)
        
        results_data.append({
            "Industry": player.name,
            "Type": player.kind_name,
            "Pollution (kg)": format_number(player.pollution),
            "Permits": format_number(player.permits),
            "Status": compliance,
            "Deficit (kg)": format_number(deficit) if deficit > 0 else "0",
            "Final Earnings": money(player.earnings)
        })
    
    results_df = pd.DataFrame(results_data)
    st.dataframe(results_df, use_container_width=True)

# Main application
def main():
    init_session_state()
    
    # Apply CSS
    st.markdown(get_custom_css(), unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>Gujarat ETS - Emission Trading Simulation</h1>
        <p>Learn cap-and-trade through interactive gameplay</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Game Configuration")
        
        # Market settings
        st.subheader("Market Settings")
        market_cap = st.number_input("Total Market Cap (kg)", 
                                    value=DEFAULT_MARKET_CAP, 
                                    min_value=100000, 
                                    max_value=500000, 
                                    step=10000)
        
        permit_price = st.number_input("Permit Floor Price (₹)", 
                                      value=float(PERMIT_PRICE), 
                                      min_value=1.0, 
                                      max_value=20.0, 
                                      step=0.5)
        
        # Player names
        st.subheader("Industry Setup")
        player1_name = st.text_input("Player 1 Name", value="Industry A")
        player2_name = st.text_input("Player 2 Name", value="Industry B")
        
        # Game controls
        st.subheader("Game Controls")
        
        if st.button("Assign Industry Types", type="primary"):
            # Reset game state
            st.session_state.players = []
            st.session_state.game_started = False
            st.session_state.game_over = False
            st.session_state.current_turn = 0
            st.session_state.game_log = []
            
            # Assign industry types randomly
            kinds = [LARGE, SMALL]
            random.shuffle(kinds)
            colors = [COLORS['red'], COLORS['teal']]
            names = [player1_name or "Industry A", player2_name or "Industry B"]
            
            for i in range(2):
                player = Player(names[i], kinds[i], colors[i], market_cap, 2)
                st.session_state.players.append(player)
            
            st.session_state.market_permits = rint(market_cap * (MARKET_ALLOCATION_PERCENT / 100))
            st.success("Industries assigned successfully!")
            st.rerun()
        
        if len(st.session_state.players) == 2 and not st.session_state.game_started:
            if st.button("Start Game", type="secondary"):
                st.session_state.game_started = True
                st.session_state.current_turn = 0
                st.success("Game started!")
                st.rerun()
        
        if st.session_state.game_started and not st.session_state.game_over:
            current_player = st.session_state.players[st.session_state.current_turn]
            if st.button(f"🎲 {current_player.name}: Roll Dice", type="secondary"):
                handle_dice_roll()
                st.rerun()
        
        # Trading section
        if st.session_state.game_started:
            st.subheader("Permit Trading")
            
            for i, player in enumerate(st.session_state.players):
                max_affordable = int(player.earnings // permit_price) if permit_price > 0 else 0
                max_by_limit = player.max_permits - player.permits
                max_possible = min(st.session_state.market_permits, max_by_limit, max_affordable)
                
                if max_possible > 0:
                    qty = st.number_input(f"Permits for {player.name}", 
                                        min_value=0, 
                                        max_value=max_possible, 
                                        key=f"permits_{i}")
                    
                    if st.button(f"Buy {qty} permits", key=f"buy_{i}") and qty > 0:
                        cost = qty * permit_price
                        player.earnings -= cost
                        player.permit_cost += cost
                        player.total_cost += cost
                        player.permits += qty
                        st.session_state.market_permits -= qty
                        
                        st.success(f"{player.name} bought {qty:,} permits for {money(cost)}")
                        st.rerun()
        
        # Reset button
        if st.button("New Game", type="secondary"):
            for key in list(st.session_state.keys()):
                if key not in ['tile_rules', 'tile_effects']:
                    del st.session_state[key]
            init_session_state()
            st.rerun()
        
        # Display last roll
        if st.session_state.last_roll:
            st.success(f"Last roll: {st.session_state.last_roll}")
        
        if st.session_state.game_started and not st.session_state.game_over:
            current_player = st.session_state.players[st.session_state.current_turn]
            st.info(f"Current turn: {current_player.name}")
    
    # Handle pending investments
    if st.session_state.pending_investment:
        investment = st.session_state.pending_investment
        player = investment['player']
        cost = investment['cost']
        multiplier = investment['multiplier']
        inv_type = investment['type']
        
        reduction = int((1 - multiplier) * 100)
        
        st.warning(f"Investment Decision for {player.name}")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button(f"Buy {inv_type.title()} Equipment", key="buy_equipment_btn"):
                if player.earnings >= cost:
                    player.earnings -= cost
                    player.total_cost += cost
                    player.pollution *= multiplier
                    st.success(f"Equipment purchased! Pollution reduced by {reduction}%")
                else:
                    st.error(f"Insufficient funds! Need {money(cost)}, have {money(player.earnings)}")
                st.session_state.pending_investment = None
                st.rerun()
        
        with col2:
            if st.button("Skip Investment", key="skip_investment_btn"):
                st.session_state.pending_investment = None
                st.rerun()
        
        st.info(f"Cost: {money(cost)} | Pollution Reduction: {reduction}% | Current Earnings: {money(player.earnings)}")
    
    # Main game area - REORDERED: Market Status first, then Game Board, then Industry Status, then Game Log
    if len(st.session_state.players) > 0:
        render_market_status(market_cap, permit_price)
        render_game_board()
        render_player_status()
        
        # Game log
        if st.session_state.game_log:
            st.header("Game Log")
            for log_entry in st.session_state.game_log[-5:]:
                st.text(log_entry)
        
        # Final results
        if st.session_state.game_over:
            render_final_results(market_cap)
    
    else:
        st.info("Configure the game settings and assign industry types to begin!")
        
        # Show game instructions
        st.header("How to Play")
        
        st.markdown("""
        ### Game Objective
        The goal is for all industries to collectively stay within the **market cap** for pollution while maintaining profitable operations.
        
        ### Key Concepts
        1. **Cap-and-Trade**: Industries receive pollution permits and can trade them
        2. **Market Cap**: Total allowed pollution for all industries combined
        3. **Permits**: Allow industries to emit a certain amount of pollution
        4. **Trading**: Industries can buy additional permits if needed
        
        ### Victory Conditions
        - **Everyone Wins**: Total pollution ≤ market cap AND all industries compliant
        - **Partial Success**: Total pollution ≤ market cap BUT some non-compliance
        - **Everyone Loses**: Total pollution > market cap (environmental failure)
        
        ### Getting Started
        1. Set market parameters in the sidebar
        2. Enter industry names
        3. Click "Assign Industry Types" to randomly assign Large/Small industries
        4. Click "Start Game" to begin
        5. Take turns rolling dice and making decisions
        6. Use permit trading to stay compliant
        """)

if __name__ == "__main__":
    main()