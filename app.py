import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim, ArcGIS

# --- 1. 基础配置 ---
ox.settings.user_agent = "art-map-poster/4.0"
ox.settings.requests_timeout = 60

st.set_page_config(page_title="艺术地图海报工坊", layout="wide")

# --- 2. 主题配置 ---
THEMES = {
    "✨ 黑金奢华 (Dubai Style)": {"bg": "#06131d", "edge": "#ffd700", "text": "#ffdb4d"},
    "🔮 赛博霓虹 (Cyberpunk)": {"bg": "#050510", "edge": "#00ffff", "text": "#ffffff"},
    "🎀 胭脂粉黛 (Pink)": {"bg": "#2b080e", "edge": "#ff69b4", "text": "#ffc0cb"},
    "🐼 极简黑白 (Classic)": {"bg": "#000000", "edge": "#ffffff", "text": "#ffffff"}
}

# --- 3. 缓存优化 ---
@st.cache_data(show_spinner=False)
def get_map_data(point, radius, network_type):
    return ox.graph_from_point(point, dist=radius, dist_type='bbox', network_type=network_type, retain_all=True)

@st.cache_data(show_spinner=False)
def get_location(city_name):
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

# 辅助函数：手动给文字加空格，模拟 letter_spacing 效果
def space_out_text(text, spacing=1):
    return (" " * spacing).join(list(text.upper()))

# --- 4. 绘图逻辑 (修复报错版) ---
def render_poster(G, theme_key, city_text, sub_text):
    theme = THEMES[theme_key]
    
    # 绘图
    fig, ax = ox.plot_graph(
        G, node_size=0, edge_color=theme["edge"], edge_linewidth=0.4,
        bgcolor=theme["bg"], figsize=(12, 16), show=False, close=False
    )
    
    # 添加文字 - 主标题 (大字)
    ax.text(0.5, 0.12, space_out_text(city_text, 2), transform=ax.transAxes, 
            ha='center', va='center', fontsize=40, color=theme["text"], 
            fontname='DejaVu Sans', fontweight='bold', alpha=0.9)
    
    # 添加文字 - 副标题 (小字) - ❌ 删除了报错的 letter_spacing 参数
    # 改用 space_out_text 函数来模拟间距
    ax.text(0.5, 0.08, space_out_text(sub_text, 1), transform=ax.transAxes, 
            ha='center', va='center', fontsize=12, color=theme["text"], 
            alpha=0.7) 
            
    # 装饰线
    ax.axhline(y=0.15, xmin=0.3, xmax=0.7, color=theme["edge"], linewidth=1, alpha=0.5)
    return fig

# --- 5. 界面 ---
col1, col2 = st.columns([1, 2])

with col1:
    st.title("🎨 艺术地图工坊")
    st.info("💡 提示：'极简黑白'风格渲染最快，'赛博霓虹'最酷炫。")
    
    city_input = st.text_input("城市名", "Shanghai")
    poster_title = st.text_input("海报主标题", value="")
    poster_subtitle = st.text_input("海报副标题", "31.2304° N / 121.4737° E")
    
    radius = st.slider("视野范围 (米)", 1000, 5000, 2000, step=500)
    
    detail_mode = st.radio(
        "细节程度",
        ["全部道路 (细节多)", "仅车道 (极速)"],
        index=1 # 默认选仅车道，体验更好
    )
    net_type = 'all' if "全部" in detail_mode else 'drive'
    
    selected_theme = st.selectbox("设计风格", list(THEMES.keys()))
    
    btn = st.button("🚀 生成海报", type="primary")

with col2:
    if btn:
        lat, lon = get_location(city_input)
        if lat:
            final_title = poster_title if poster_title else city_input.split(",")[0]
            
            with st.spinner("💾 正在获取地图数据..."):
                try:
                    G = get_map_data((lat, lon), radius, net_type)
                    
                    with st.spinner("🎨 正在绘制海报..."):
                        fig = render_poster(G, selected_theme, final_title, poster_subtitle)
                        st.pyplot(fig)
                        
                        fn = f"poster_{city_input}.png"
                        fig.savefig(fn, dpi=150, bbox_inches='tight', facecolor=THEMES[selected_theme]["bg"])
                        with open(fn, "rb") as f:
                            st.download_button("📥 下载原图", data=f, file_name=fn, mime="image/png")
                except Exception as e:
                    # 这次如果报错，才是真的内存或者网络问题
                    st.error(f"生成失败: {e}")
        else:
            st.error("❌ 找不到该城市，请输入英文名称重试。")
