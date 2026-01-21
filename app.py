import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim, ArcGIS

# --- 1. 基础配置 ---
ox.settings.user_agent = "art-map-poster/3.0"
ox.settings.requests_timeout = 60

st.set_page_config(page_title="艺术地图海报工坊", layout="wide")

# --- 2. 主题配置 ---
THEMES = {
    "✨ 黑金奢华 (Dubai Style)": {"bg": "#06131d", "edge": "#ffd700", "text": "#ffdb4d"},
    "🔮 赛博霓虹 (Cyberpunk)": {"bg": "#050510", "edge": "#00ffff", "text": "#ffffff"},
    "🎀 胭脂粉黛 (Pink)": {"bg": "#2b080e", "edge": "#ff69b4", "text": "#ffc0cb"},
    "🐼 极简黑白 (Classic)": {"bg": "#000000", "edge": "#ffffff", "text": "#ffffff"}
}

# --- 3. 核心优化：使用缓存装饰器 ---
# 只有当城市、半径或道路类型改变时，才会重新下载。否则直接读取内存，速度起飞！
@st.cache_data(show_spinner=False)
def get_map_data(point, radius, network_type):
    # 根据用户选择下载不同类型的路网
    return ox.graph_from_point(point, dist=radius, dist_type='bbox', network_type=network_type, retain_all=True)

@st.cache_data(show_spinner=False)
def get_location(city_name):
    # 缓存定位结果，不用每次都去问服务器
    try:
        loc = Nominatim(user_agent="poster_app_v4").geocode(city_name, timeout=10)
        if loc: return loc.latitude, loc.longitude
    except:
        pass
    try:
        loc = ArcGIS().geocode(city_name, timeout=10)
        if loc: return loc.latitude, loc.longitude
    except:
        return None, None

def format_title(text):
    return "  ".join(list(text.upper()))

# --- 4. 绘图逻辑 ---
def render_poster(G, theme_key, city_text, sub_text):
    theme = THEMES[theme_key]
    
    # 绘图
    fig, ax = ox.plot_graph(
        G, node_size=0, edge_color=theme["edge"], edge_linewidth=0.4,
        bgcolor=theme["bg"], figsize=(12, 16), show=False, close=False
    )
    
    # 添加文字
    ax.text(0.5, 0.12, format_title(city_text), transform=ax.transAxes, 
            ha='center', va='center', fontsize=40, color=theme["text"], 
            fontname='DejaVu Sans', fontweight='bold', alpha=0.9)
    
    ax.text(0.5, 0.08, sub_text.upper(), transform=ax.transAxes, 
            ha='center', va='center', fontsize=12, color=theme["text"], 
            alpha=0.7, letter_spacing=2)
            
    ax.axhline(y=0.15, xmin=0.3, xmax=0.7, color=theme["edge"], linewidth=1, alpha=0.5)
    return fig

# --- 5. 界面 ---
col1, col2 = st.columns([1, 2])

with col1:
    st.title("🎨 艺术地图 ")
    
    city_input = st.text_input("城市名", "Singapore")
    poster_title = st.text_input("海报主标题", value="")
    poster_subtitle = st.text_input("海报副标题", "1.3521° N / 103.8198° E")
    
    # 性能优化选项
    radius = st.slider("视野范围 (米) - 越小越快", 1000, 5000, 2000, step=500)
    
    detail_mode = st.radio(
        "细节程度 (觉得慢请选'仅车道')",
        ["全部道路 (慢，细节多)", "仅车道 (快，极简)"],
        index=0
    )
    net_type = 'all' if "全部" in detail_mode else 'drive'
    
    selected_theme = st.selectbox("设计风格", list(THEMES.keys()))
    
    btn = st.button("🚀 生成海报", type="primary")

with col2:
    if btn:
        # 第一阶段：定位
        lat, lon = get_location(city_input)
        if lat:
            final_title = poster_title if poster_title else city_input.split(",")[0]
            
            # 第二阶段：下载数据 (最慢的一步，但现在有缓存了！)
            with st.spinner("💾 正在下载地图数据... (运行较慢，敬请谅解)"):
                try:
                    G = get_map_data((lat, lon), radius, net_type)
                    
                    # 第三阶段：渲染
                    with st.spinner("🎨 正在渲染图片..."):
                        fig = render_poster(G, selected_theme, final_title, poster_subtitle)
                        st.pyplot(fig)
                        
                        fn = f"poster_{city_input}.png"
                        fig.savefig(fn, dpi=150, bbox_inches='tight', facecolor=THEMES[selected_theme]["bg"])
                        with open(fn, "rb") as f:
                            st.download_button("📥 下载原图", data=f, file_name=fn, mime="image/png")
                except Exception as e:
                    st.error(f"数据量太大，内存爆了！请尝试减小半径或选择'仅车道'模式。错误: {e}")
        else:
            st.error("❌ 找不到该城市")
