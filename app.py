import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from geopy.geocoders import Nominatim, ArcGIS
import os

# --- 1. 基础配置 ---
ox.settings.user_agent = "art-map-poster/11.0"
ox.settings.requests_timeout = 60

st.set_page_config(page_title="艺术地图海报工坊", layout="wide")

# --- 2. 关键修复：自动下载并加载中文字体 ---
@st.cache_resource
def get_chinese_font():
    """下载 SimHei 字体，解决中文乱码问题"""
    font_path = "SimHei.ttf"
    # 如果本地没有字体文件，就从网上下一个
    if not os.path.exists(font_path):
        # 使用 GitHub 镜像源下载字体
        os.system("wget https://github.com/StellarCN/scp_zh/raw/master/fonts/SimHei.ttf -O SimHei.ttf")
    
    # 返回字体属性对象
    return fm.FontProperties(fname=font_path)

# 加载字体 (这一步只会运行一次)
zh_font = get_chinese_font()

# --- 3. 主题配置 ---
THEMES = {
    "✨ 黑金奢华 (Dubai Style)": {"bg": "#06131d", "edge": "#ffd700", "text": "#ffdb4d"},
    "🔮 赛博霓虹 (Cyberpunk)": {"bg": "#050510", "edge": "#00ffff", "text": "#ffffff"},
    "🎀 胭脂粉黛 (Pink)": {"bg": "#2b080e", "edge": "#ff69b4", "text": "#ffc0cb"},
    "🐼 极简黑白 (Classic)": {"bg": "#000000", "edge": "#ffffff", "text": "#ffffff"}
}

# --- 4. 核心功能函数 ---
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
    # 稍微改动：如果是中文，字间距不用太大；英文保持原样
    return (" " * spacing).join(list(text))

def format_coords(lat, lon):
    ns = "N" if lat >= 0 else "S"
    ew = "E" if lon >= 0 else "W"
    return f"{abs(lat):.4f}° {ns} / {abs(lon):.4f}° {ew}"

def update_subtitle():
    city = st.session_state.city_key
    if city:
        lat, lon = get_location(city)
        if lat:
            st.session_state.sub_key = format_coords(lat, lon)

# --- 5. 绘图逻辑 (已修复中文显示) ---
def render_poster(G, theme_key, city_text, sub_text):
    theme = THEMES[theme_key]
    
    fig, ax = ox.plot_graph(
        G, node_size=0, edge_color=theme["edge"], edge_linewidth=0.4,
        bgcolor=theme["bg"], figsize=(12, 16), show=False, close=False
    )
    
    # 1. 主标题 (应用中文字体)
    ax.text(0.5, 0.12, space_out_text(city_text, 1), transform=ax.transAxes, 
            ha='center', va='center', fontsize=40, color=theme["text"], 
            fontproperties=zh_font, # 👈 关键点：指定中文字体
            alpha=0.9)
    
    # 2. 副标题 (应用中文字体)
    if sub_text and sub_text.strip() != "":
        ax.text(0.5, 0.08, space_out_text(sub_text, 1), transform=ax.transAxes, 
                ha='center', va='center', fontsize=12, color=theme["text"], 
                fontproperties=zh_font, # 👈 关键点：指定中文字体
                alpha=0.7) 
            
    ax.axhline(y=0.15, xmin=0.3, xmax=0.7, color=theme["edge"], linewidth=1, alpha=0.5)
    return fig

# --- 6. 界面布局 ---
col1, col2 = st.columns([1, 2])

with col1:
    st.title("🎨 艺术地图工坊")
    st.caption("✅ 现在完美支持中文标题了！")
    
    city_input = st.text_input("城市名 (自动定位)", "Shanghai", key="city_key", on_change=update_subtitle)
    
    # 这里你可以随意输入中文了
    poster_title = st.text_input("海报主标题 (支持中文)", value="")
    poster_subtitle = st.text_input("海报副标题", "31.2304° N / 121.4737° E", key="sub_key")
    
    radius = st.slider("视野范围 (米)", 1000, 5000, 2000, step=500)
    detail_mode = st.radio("细节程度", ["全部道路 (美)", "仅车道 (快)"], index=1)
    net_type = 'all' if "全部" in detail_mode else 'drive'
    selected_theme = st.selectbox("设计风格", list(THEMES.keys()))
    
    btn = st.button("🚀 生成海报", type="primary")

    # 页脚
    st.markdown("---")
    st.markdown(
        """
        <style>
        .footer-link { text-decoration: none; color: #444; font-weight: bold; }
        .gemini-text { background: linear-gradient(90deg, #4b90ff, #ff5546); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: bold; }
        </style>
        <div style='text-align: center; color: #666; font-size: 13px; line-height: 2.0;'>
            <div>🌟 Core Concept by <a href='https://github.com/originalankur/maptoposter' target='_blank' class='footer-link'>originalankur</a></div>
            <div>🤖 Web Adaptation by <span class='gemini-text'>Gemini 3 Pro</span></div>
            <div style='font-size: 12px; margin-top: 5px;'>Built with <a href='https://streamlit.io' target='_blank' style='text-decoration: none; color: #ff4b4b;'>Streamlit 🎈</a></div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    if btn:
        lat, lon = get_location(city_input)
        if lat:
            final_title = poster_title if poster_title else city_input # 不强制大写，保留中文原样
            final_sub = poster_subtitle
            with st.spinner(f"💾 正在下载数据..."):
                try:
                    G = get_map_data((lat, lon), radius, net_type)
                    with st.spinner("🎨 正在渲染 (首次运行会自动下载字体)..."):
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
