import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim, ArcGIS # 引入双重定位引擎

# --- 1. 设置基础配置 ---
ox.settings.user_agent = "student-map-project/2.0"
ox.settings.requests_timeout = 60

st.set_page_config(page_title="城市地图海报生成器", layout="centered")
st.title("🗺️ 城市地图海报生成器 (自动转换版)")

# --- 2. 定义智能定位函数 (核心黑科技) ---
def get_lat_lon(city_name):
    """
    自动尝试多种方式获取经纬度
    1. 尝试 Nominatim (OSM官方)
    2. 失败则切换 ArcGIS (非常稳定)
    """
    # 方案 A: 官方接口
    try:
        geolocator = Nominatim(user_agent="my_map_app_v2")
        location = geolocator.geocode(city_name, timeout=10)
        if location:
            return (location.latitude, location.longitude), "OSM官方接口"
    except:
        pass # 如果失败，不要报错，默默进入方案 B

    # 方案 B: ArcGIS 接口 (备用通道，防封锁神器)
    try:
        geolocator = ArcGIS()
        location = geolocator.geocode(city_name, timeout=10)
        if location:
            return (location.latitude, location.longitude), "ArcGIS备用接口"
    except:
        pass

    # 如果都失败了
    return None, None

# --- 3. 侧边栏设置 ---
st.sidebar.header("参数设置")
city_input = st.sidebar.text_input("输入城市名称 (中文/英文)", "Shanghai, China")
radius = st.sidebar.slider("地图半径 (米)", 1000, 5000, 2000, step=500)
style_select = st.sidebar.selectbox("配色风格", ["Dark Mode", "Light Mode"])

# --- 4. 绘图逻辑 ---
def create_poster(point, dist, mode):
    # 使用获取到的坐标直接下载数据
    G = ox.graph_from_point(point, dist=dist, dist_type='bbox', network_type='all')
    
    if mode == "Dark Mode":
        bgcolor = '#212121'
        edge_color = '#ffffff'
    else:
        bgcolor = '#fdfdfd'
        edge_color = '#000000'
        
    fig, ax = ox.plot_graph(
        G, node_size=0, edge_color=edge_color, edge_linewidth=0.5,
        bgcolor=bgcolor, figsize=(10, 14), show=False, close=False
    )
    return fig

# --- 5. 主程序 ---
if st.button("🚀 自动转换并生成"):
    with st.spinner(f"正在定位 '{city_input}' ..."):
        # 第一步：自动转换经纬度
        point, source = get_lat_lon(city_input)
        
        if point:
            st.success(f"✅ 定位成功！(使用源: {source}) | 坐标: {point[0]:.4f}, {point[1]:.4f}")
            
            # 第二步：开始绘图
            with st.spinner("正在下载卫星地图数据并渲染..."):
                try:
                    fig = create_poster(point, radius, style_select)
                    st.pyplot(fig)
                    
                    # 下载功能
                    fn = "poster.png"
                    fig.savefig(fn, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
                    with open(fn, "rb") as file:
                        st.download_button("📥 下载海报", data=file, file_name=f"map_{city_input}.png", mime="image/png")
                except Exception as e:
                    st.error(f"绘图时出错: {e}")
        else:
            st.error(f"❌ 找不到城市: '{city_input}'")
            st.warning("建议尝试：\n1. 使用英文名称 (e.g. Beijing)\n2. 加上国家名 (e.g. Paris, France)")
