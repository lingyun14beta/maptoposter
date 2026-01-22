import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from geopy.geocoders import Nominatim, ArcGIS
import os
import requests  # 使用 Python 原生库下载，更稳定

# --- 1. 基础配置 ---
ox.settings.user_agent = "art-map-poster/12.0"
ox.settings.requests_timeout = 60

st.set_page_config(page_title="艺术地图海报工坊", layout="wide")

# --- 2. 核心修复：强力字体下载器 ---
@st.cache_resource
def get_chinese_font():
    """
    下载开源中文字体 (文泉驿微米黑)，解决乱码和报错问题
    """
    font_name = "wqy-microhei.ttc"
    # 使用 Google Fonts 或 GitHub 稳定源
    font_url = "https://github.com/anthonyfok/fonts-wqy-microhei/raw/master/wqy-microhei.ttc"
    
    if not os.path.exists(font_name):
        try:
            # 使用 requests 下载，显示进度
            with st.spinner("正在下载中文字体包 (约 5MB)... 请耐心等待..."):
                response = requests.get(font_url, timeout=30)
                with open(font_name, "wb") as f:
                    f.write(response.content)
            print("字体下载成功！")
        except Exception as e:
            st.warning(f"⚠️ 中文字体下载失败，将使用默认字体（中文可能会显示方框）。错误: {e}")
            return None # 下载失败返回空，避免程序崩溃

    # 返回字体路径
    return fm.FontProperties(fname=font_name)

# 加载字体
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

# --- 5. 绘图逻辑 (带错误保护) ---
def render_poster(G, theme_key, city_text, sub_text):
    theme = THEMES[theme_key]
    
    fig, ax = ox.plot_graph(
        G, node_size=0, edge_color=theme["edge"], edge_linewidth=0.4,
        bgcolor=theme["bg"], figsize=(12, 16), show=False, close=False
    )
    
    # 智能选择字体：如果有中文字体就用，没有就用默认
    font_prop = zh_font if zh_font else None
    
    # 1. 主标题
    ax.text(0.5, 0.12, space_out_text(city_text, 1), transform=ax.transAxes, 
            ha='center', va='center', fontsize=40, color=theme["text"], 
            fontproperties=font_prop, # 应用字体
            alpha=0.9)
    
    # 2. 副标题
    if sub_text and sub_text.strip() != "":
        ax.text(0.5, 0.08, space_out_text(sub_text, 1), transform=ax.transAxes, 
                ha='center', va='center', fontsize=12, color=theme["text"], 
                fontproperties=font_prop, # 应用字体
                alpha=0.7) 
            
    ax.axhline(y=0.15, xmin=0.3, xmax=0.7, color=theme["edge"], linewidth=1, alpha=0.5)
    return fig

# --- 6. 界面布局 ---
col1, col2 = st.columns([1, 2])

with col1:
    st.title("🎨 艺术地图工坊")
    st.caption("✅ 正在运行 v12.0 ")
    
    city_input = st.text_input("城市名 ", "上海", key="city_key", on_change=update_subtitle)
    poster_title = st.text_input("海报主标题 ", value="")
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
            <div> Web Adaptation by <span class='gemini-text'>Gemini 3 Pro</span></div>
            <div style='font-size: 12px; margin-top: 5px;'>Built with <a href='https://streamlit.io' target='_blank' style='text-decoration: none; color: #ff4b4b;'>Streamlit 🎈</a></div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    if btn:
        lat, lon = get_location(city_input)
        if lat:
            final_title = poster_title if poster_title else city_input
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
