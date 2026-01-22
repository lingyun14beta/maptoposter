import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from geopy.geocoders import Nominatim, ArcGIS
import os
import requests
import re # 用于检测是不是坐标格式

# --- 1. 基础配置 ---
ox.settings.user_agent = "art-map-poster/13.0"
ox.settings.requests_timeout = 60

st.set_page_config(page_title="艺术地图海报工坊", layout="wide")

# --- 2. 字体下载器 ---
@st.cache_resource
def get_chinese_font():
    font_name = "wqy-microhei.ttc"
    font_url = "https://github.com/anthonyfok/fonts-wqy-microhei/raw/master/wqy-microhei.ttc"
    if not os.path.exists(font_name):
        try:
            with st.spinner("正在初始化字体资源..."):
                response = requests.get(font_url, timeout=30)
                with open(font_name, "wb") as f:
                    f.write(response.content)
        except:
            return None
    return fm.FontProperties(fname=font_name)

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
    """输入框回车触发的更新"""
    city = st.session_state.city_key
    if city:
        lat, lon = get_location(city)
        if lat:
            st.session_state.sub_key = format_coords(lat, lon)

def is_coordinate_format(text):
    """判断一段文字长得像不像坐标（包含数字和度数符号）"""
    if not text: return False
    # 如果包含数字和 ° 符号，或者 N/S/E/W，就认为是自动生成的坐标
    return any(char.isdigit() for char in text) and ("°" in text or "/" in text)

# --- 5. 绘图逻辑 ---
def render_poster(G, theme_key, city_text, sub_text):
    theme = THEMES[theme_key]
    fig, ax = ox.plot_graph(
        G, node_size=0, edge_color=theme["edge"], edge_linewidth=0.4,
        bgcolor=theme["bg"], figsize=(12, 16), show=False, close=False
    )
    
    font_prop = zh_font if zh_font else None
    
    # 主标题
    ax.text(0.5, 0.12, space_out_text(city_text, 1), transform=ax.transAxes, 
            ha='center', va='center', fontsize=40, color=theme["text"], 
            fontproperties=font_prop, alpha=0.9)
    
    # 副标题
    if sub_text and sub_text.strip() != "":
        ax.text(0.5, 0.08, space_out_text(sub_text, 1), transform=ax.transAxes, 
                ha='center', va='center', fontsize=12, color=theme["text"], 
                fontproperties=font_prop, alpha=0.7) 
            
    ax.axhline(y=0.15, xmin=0.3, xmax=0.7, color=theme["edge"], linewidth=1, alpha=0.5)
    return fig

# --- 6. 界面布局 ---
col1, col2 = st.columns([1, 2])

with col1:
    st.title("🎨 艺术地图工坊")
    st.caption("✅ v13.0 ")
    
    city_input = st.text_input("城市名", "上海", key="city_key", on_change=update_subtitle)
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
            <div> Web Adaptation by <span class='gemini-text'>Gemini 3 Pro</span></div>
            <div style='font-size: 12px; margin-top: 5px;'>Built with <a href='https://streamlit.io' target='_blank' style='text-decoration: none; color: #ff4b4b;'>Streamlit 🎈</a></div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    if btn:
        # 1. 先获取当前输入城市的真实坐标
        lat, lon = get_location(city_input)
        
        if lat:
            final_title = poster_title if poster_title else city_input
            
            # --- 🔥 智能纠错逻辑 ---
            # 如果用户没有写自定义的文字（输入框里看起来还是坐标格式），
            # 那么强制用当前城市的真实坐标覆盖它！防止出现"北京地图+上海坐标"的乌龙。
            current_real_coords = format_coords(lat, lon)
            
            # 判断逻辑：如果用户填的是坐标格式，且跟真实坐标不一样，那就修成真实的
            if is_coordinate_format(poster_subtitle) and poster_subtitle != current_real_coords:
                final_sub = current_real_coords
                # 可选：提示用户纠错
                st.toast(f"📍 已自动修正为 {city_input} 的正确坐标", icon="🔧")
            else:
                final_sub = poster_subtitle
            # ---------------------

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
