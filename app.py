import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim, ArcGIS

# --- 1. 基础配置 ---
ox.settings.user_agent = "art-map-poster/8.0"
ox.settings.requests_timeout = 60

st.set_page_config(page_title="艺术地图海报工坊", layout="wide")

# --- 2. 主题配置 ---
THEMES = {
    "✨ 黑金奢华 (Dubai Style)": {"bg": "#06131d", "edge": "#ffd700", "text": "#ffdb4d"},
    "🔮 赛博霓虹 (Cyberpunk)": {"bg": "#050510", "edge": "#00ffff", "text": "#ffffff"},
    "🎀 胭脂粉黛 (Pink)": {"bg": "#2b080e", "edge": "#ff69b4", "text": "#ffc0cb"},
    "🐼 极简黑白 (Classic)": {"bg": "#000000", "edge": "#ffffff", "text": "#ffffff"}
}

# --- 3. 核心功能函数 ---
@st.cache_data(show_spinner=False)
def get_location(city_name):
    """获取经纬度 (带缓存)"""
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
    """下载路网 (带缓存)"""
    return ox.graph_from_point(point, dist=radius, dist_type='bbox', network_type=network_type, retain_all=True)

def space_out_text(text, spacing=1):
    if not text: return ""
    return (" " * spacing).join(list(text.upper()))

def format_coords(lat, lon):
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    return f"{abs(lat):.4f}° {ns} / {abs(lon):.4f}° {ew}"

# --- 4. 自动更新逻辑 ---
def update_subtitle():
    """当城市名改变时，自动查找经纬度并填入副标题"""
    city = st.session_state.city_key
    if city:
        lat, lon = get_location(city)
        if lat:
            st.session_state.sub_key = format_coords(lat, lon)

# --- 5. 绘图逻辑 ---
def render_poster(G, theme_key, city_text, sub_text):
    theme = THEMES[theme_key]
    
    fig, ax = ox.plot_graph(
        G, node_size=0, edge_color=theme["edge"], edge_linewidth=0.4,
        bgcolor=theme["bg"], figsize=(12, 16), show=False, close=False
    )
    
    # 主标题
    ax.text(0.5, 0.12, space_out_text(city_text, 2), transform=ax.transAxes, 
            ha='center', va='center', fontsize=40, color=theme["text"], 
            fontname='DejaVu Sans', fontweight='bold', alpha=0.9)
    
    # 副标题
    if sub_text and sub_text.strip() != "":
        ax.text(0.5, 0.08, space_out_text(sub_text, 1), transform=ax.transAxes, 
                ha='center', va='center', fontsize=12, color=theme["text"], 
                alpha=0.7) 
            
    # 装饰线
    ax.axhline(y=0.15, xmin=0.3, xmax=0.7, color=theme["edge"], linewidth=1, alpha=0.5)
    return fig

# --- 6. 界面布局 ---
col1, col2 = st.columns([1, 2])

with col1:
    st.title("🎨 艺术地图工坊")
    
    # 城市输入框
    city_input = st.text_input(
        "城市名 (输入并回车，自动填坐标)", 
        "Shanghai", 
        key="city_key",
        on_change=update_subtitle
    )
    
    poster_title = st.text_input("海报主标题", value="")
    
    # 副标题输入框
    poster_subtitle = st.text_input(
        "海报副标题 (可手动修改或清空)", 
        "31.2304° N / 121.4737° E",
        key="sub_key"
    )
    
    radius = st.slider("视野范围 (米)", 1000, 5000, 2000, step=500)
    detail_mode = st.radio("细节程度", ["全部道路 (美)", "仅车道 (快)"], index=1)
    net_type = 'all' if "全部" in detail_mode else 'drive'
    selected_theme = st.selectbox("设计风格", list(THEMES.keys()))
    
    btn = st.button("🚀 生成海报", type="primary")

    # --- 👇👇👇 新增：致谢原作者 + Streamlit 👇👇👇 ---
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 12px;'>
            <p style='margin-bottom: 5px;'>
                Inspired by 
                <a href='https://github.com/originalankur/maptoposter' target='_blank' style='text-decoration: none; color: #666; font-weight: bold;'>
                    originalankur
                </a>
            </p>
            <p>
                Built with 
                <a href='https://streamlit.io' target='_blank' style='text-decoration: none; color: #ff4b4b;'>
                    Streamlit 🎈
                </a>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    if btn:
        lat, lon = get_location(city_input)
        if lat:
            final_title = poster_title if poster_title else city_input.split(",")[0]
            final_sub = poster_subtitle
            
            with st.spinner(f"💾 正在下载数据..."):
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
