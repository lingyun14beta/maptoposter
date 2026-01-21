import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim, ArcGIS

# --- 1. 基础配置 ---
ox.settings.user_agent = "art-map-poster/6.0"
ox.settings.requests_timeout = 60

st.set_page_config(page_title="艺术地图海报工坊", layout="wide")

# --- 2. 主题配置 ---
THEMES = {
    "✨ 黑金奢华 (Dubai Style)": {"bg": "#06131d", "edge": "#ffd700", "text": "#ffdb4d"},
    "🔮 赛博霓虹 (Cyberpunk)": {"bg": "#050510", "edge": "#00ffff", "text": "#ffffff"},
    "🎀 胭脂粉黛 (Pink)": {"bg": "#2b080e", "edge": "#ff69b4", "text": "#ffc0cb"},
    "🐼 极简黑白 (Classic)": {"bg": "#000000", "edge": "#ffffff", "text": "#ffffff"}
}

# --- 3. 核心功能 ---
@st.cache_data(show_spinner=False)
def get_location(city_name):
    try:
        loc = Nominatim(user_agent="poster_app_auto").geocode(city_name, timeout=10)
        if loc: return loc.latitude, loc.longitude
    except:
        pass
    try:
        loc = ArcGIS().geocode(city_name, timeout=10)
        if loc: return loc.latitude, loc.longitude
    except:
        return None, None

@st.cache_data(show_spinner=False)
def get_map_data(point, radius, network_type):
    return ox.graph_from_point(point, dist=radius, dist_type='bbox', network_type=network_type, retain_all=True)

def space_out_text(text, spacing=1):
    if not text: return ""
    return (" " * spacing).join(list(text.upper()))

def format_coords(lat, lon):
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    return f"{abs(lat):.4f}° {ns} / {abs(lon):.4f}° {ew}"

def update_subtitle():
    """城市改变时自动填坐标，但允许用户事后删掉"""
    city = st.session_state.city_key
    if city:
        lat, lon = get_location(city)
        if lat:
            st.session_state.sub_key = format_coords(lat, lon)

# --- 4. 绘图逻辑 ---
def render_poster(G, theme_key, city_text, sub_text):
    theme = THEMES[theme_key]
    
    fig, ax = ox.plot_graph(
        G, node_size=0, edge_color=theme["edge"], edge_linewidth=0.4,
        bgcolor=theme["bg"], figsize=(12, 16), show=False, close=False
    )
    
    # 1. 主标题
    ax.text(0.5, 0.12, space_out_text(city_text, 2), transform=ax.transAxes, 
            ha='center', va='center', fontsize=40, color=theme["text"], 
            fontname='DejaVu Sans', fontweight='bold', alpha=0.9)
    
    # 2. 副标题 (修正：只有当不为空时才绘制)
    if sub_text and sub_text.strip() != "":
        ax.text(0.5, 0.08, space_out_text(sub_text, 1), transform=ax.transAxes, 
                ha='center', va='center', fontsize=12, color=theme["text"], 
                alpha=0.7) 
            
    # 3. 装饰线 (一直保留，或者你也可以设为没有副标题时隐藏)
    ax.axhline(y=0.15, xmin=0.3, xmax=0.7, color=theme["edge"], linewidth=1, alpha=0.5)
    
    return fig

# --- 5. 界面布局 ---
col1, col2 = st.columns([1, 2])

with col1:
    st.title("🎨 艺术地图工坊")
    
    city_input = st.text_input(
        "城市名 (输完按回车自动填坐标)", 
        "Shanghai", 
        key="city_key",
        on_change=update_subtitle 
    )
    
    poster_title = st.text_input("海报主标题", value="")
    
    # 👇 这里是关键：即使自动填了，你也可以手动删掉，生成时就会变空
    poster_subtitle = st.text_input(
        "海报副标题 (清空则不显示)", 
        "31.2304° N / 121.4737° E",
        key="sub_key"
    )
    
    radius = st.slider("视野范围 (米)", 1000, 5000, 2000, step=500)
    detail_mode = st.radio("细节程度", ["全部道路 (美)", "仅车道 (快)"], index=1)
    net_type = 'all' if "全部" in detail_mode else 'drive'
    selected_theme = st.selectbox("设计风格", list(THEMES.keys()))
    
    btn = st.button("🚀 生成海报", type="primary")

with col2:
    if btn:
        lat, lon = get_location(city_input)
        if lat:
            final_title = poster_title if poster_title else city_input.split(",")[0]
            
            # 👇 修正：直接使用用户输入框里的内容，即使用户把它删空了，也照样传空值进去
            final_sub = poster_subtitle 
            
            with st.spinner(f"💾 正在下载..."):
                try:
                    G = get_map_data((lat, lon), radius, net_type)
                    
                    with st.spinner("🎨 正在渲染..."):
                        fig = render_poster(G, selected_theme, final_title, final_sub)
                        st.pyplot(fig)
                        
                        fn = f"poster_{city_input}.png"
                        fig.savefig(fn, dpi=150, bbox_inches='tight', facecolor=THEMES[selected_theme]["bg"])
                        with open(fn, "rb") as f:
                            st.download_button("📥 下载原图", data=f, file_name=fn, mime="image/png")
                except Exception as e:
                    st.error(f"出错: {e}")
        else:
            st.error("❌ 找不到城市")
