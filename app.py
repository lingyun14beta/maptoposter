import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim, ArcGIS

# --- 1. 基础配置 & 防封锁 ---
ox.settings.user_agent = "art-map-poster/3.0"
ox.settings.requests_timeout = 60

st.set_page_config(page_title="艺术地图海报工坊", layout="wide") # 改宽屏布局

# --- 2. 定义高级配色主题 ---
THEMES = {
    "✨ 黑金奢华 (Dubai Style)": {
        "bg": "#06131d",       # 深海蓝黑背景
        "edge": "#ffd700",     # 金色线条
        "text": "#ffdb4d",     # 浅金文字
        "font_weight": "bold"
    },
    "🔮 赛博霓虹 (Cyberpunk)": {
        "bg": "#050510",       # 极深紫黑
        "edge": "#00ffff",     # 青色荧光线 (也可以换成洋红)
        "text": "#ffffff",     # 白色文字
        "font_weight": "normal"
    },
    "🎀 胭脂粉黛 (Pink)": {
        "bg": "#2b080e",       # 深红褐
        "edge": "#ff69b4",     # 亮粉色
        "text": "#ffc0cb",     # 浅粉字
        "font_weight": "bold"
    },
    "🐼 极简黑白 (Classic)": {
        "bg": "#000000",
        "edge": "#ffffff",
        "text": "#ffffff",
        "font_weight": "normal"
    }
}

# --- 3. 辅助函数：文字加宽处理 ---
def format_title(text):
    """把 'Singapore' 变成 'S  I  N  G  A  P  O  R  E' 的效果"""
    text = text.upper() # 转大写
    return "  ".join(list(text)) # 每个字母中间加两个空格

def get_location_data(city_name):
    """智能定位：先试OSM，不行换ArcGIS"""
    try:
        geolocator = Nominatim(user_agent="poster_app_v3")
        loc = geolocator.geocode(city_name, timeout=10)
        if loc: return loc.latitude, loc.longitude, loc.address
    except:
        pass
    try:
        geolocator = ArcGIS()
        loc = geolocator.geocode(city_name, timeout=10)
        if loc: return loc.latitude, loc.longitude, loc.address
    except:
        return None, None, None

# --- 4. 核心绘图逻辑 (海报级渲染) ---
def create_art_poster(lat, lon, city_text, sub_text, radius, theme_key):
    # 获取主题颜色
    theme = THEMES[theme_key]
    
    # 下载数据
    point = (lat, lon)
    # 增加 retain_all=True 可以保留更多细节道路，画面更丰满
    G = ox.graph_from_point(point, dist=radius, dist_type='bbox', network_type='all', retain_all=True)
    
    # 绘图
    fig, ax = ox.plot_graph(
        G,
        node_size=0,
        edge_color=theme["edge"],
        edge_linewidth=0.4, # 线条细一点更精致
        bgcolor=theme["bg"],
        figsize=(12, 16),   # 典型的海报比例 (3:4)
        show=False,
        close=False
    )
    
    # --- 关键：添加文字装饰 ---
    # 1. 主标题 (城市名)
    formatted_city = format_title(city_text)
    ax.text(
        0.5, 0.12, # 坐标位置 (0.5是水平居中, 0.12是底部靠上一点)
        formatted_city,
        transform=ax.transAxes, # 使用相对坐标系
        ha='center', va='center',
        fontsize=40,
        color=theme["text"],
        fontname='DejaVu Sans', # 使用通用无衬线字体
        fontweight='bold',
        alpha=0.9 # 轻微透明
    )
    
    # 2. 副标题 (国家/坐标/描述)
    ax.text(
        0.5, 0.08, 
        sub_text.upper(),
        transform=ax.transAxes,
        ha='center', va='center',
        fontsize=12,
        color=theme["text"],
        fontweight='light',
        alpha=0.7,
        letter_spacing=2 # 这一项 matplotlib 原生不支持，靠间距模拟
    )
    
    # 3. 装饰线 (标题上下的小横线，增加设计感)
    ax.axhline(y=0.15, xmin=0.3, xmax=0.7, color=theme["edge"], linewidth=1, alpha=0.5)

    return fig

# --- 5. 网页界面布局 ---
col1, col2 = st.columns([1, 2]) # 左窄右宽布局

with col1:
    st.title("🎨 艺术地图工坊")
    st.markdown("生成类似 **Displate** 风格的金属海报图")
    
    city_input = st.text_input("城市名", "Singapore")
    
    # 让用户自定义海报上的文字
    poster_title = st.text_input("海报主标题 (默认跟城市名一样)", value="")
    poster_subtitle = st.text_input("海报副标题 (例如坐标或国家)", "1.3521° N / 103.8198° E")
    
    radius = st.slider("视野范围 (米)", 1000, 8000, 3000, step=500)
    selected_theme = st.selectbox("选择设计风格", list(THEMES.keys()))
    
    generate_btn = st.button("🚀 生成艺术海报", type="primary")

with col2:
    if generate_btn:
        with st.spinner("🎨 正在设计海报... (下载路网数据中)"):
            lat, lon, address = get_location_data(city_input)
            
            if lat:
                # 如果用户没填标题，就自动用城市名
                final_title = poster_title if poster_title else city_input.split(",")[0]
                
                # 生成海报
                fig = create_art_poster(lat, lon, final_title, poster_subtitle, radius, selected_theme)
                
                st.pyplot(fig)
                
                # 下载
                fn = f"poster_{city_input}.png"
                fig.savefig(fn, dpi=150, bbox_inches='tight', facecolor=THEMES[selected_theme]["bg"])
                with open(fn, "rb") as f:
                    st.download_button("📥 下载高清原图", data=f, file_name=fn, mime="image/png")
            else:
                st.error("❌ 找不到该城市，请尝试输入英文名称。")
    else:
        st.info("👈 请在左侧输入参数，点击生成按钮。")
        st.markdown("### ✨ 效果预览")
        st.markdown("- **黑金奢华**: 适合迪拜、纽约、上海等繁华都市")
        st.markdown("- **赛博霓虹**: 适合东京、重庆、香港等立体城市")
