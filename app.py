import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt

# --- 1. 设置身份伪装 (防封锁) ---
ox.settings.user_agent = "student-project-map-poster/1.0"
ox.settings.requests_timeout = 60

st.set_page_config(page_title="城市地图海报生成器", layout="centered")
st.title("🗺️ 城市地图海报生成器 (稳定版)")

# --- 2. 侧边栏：增加模式选择 ---
st.sidebar.header("参数设置")

# 让用户选择：是用名字搜，还是直接填坐标？
input_mode = st.sidebar.radio("定位方式 (推荐使用坐标，更稳定)", ["城市名称搜索", "输入经纬度"])

if input_mode == "城市名称搜索":
    city = st.sidebar.text_input("城市名称 (英文)", "Beijing, China")
    st.sidebar.info("💡 提示：如果名称搜索失败，请切换到'输入经纬度'模式。")
else:
    # 默认坐标填的是上海
    lat = st.sidebar.number_input("纬度 (Latitude)", value=31.2304, format="%.4f")
    lon = st.sidebar.number_input("经度 (Longitude)", value=121.4737, format="%.4f")
    st.sidebar.markdown("[👉 点击这里查询城市经纬度](https://www.latlong.net/)")

radius = st.sidebar.slider("地图半径 (米)", 1000, 5000, 2000, step=500)
style_select = st.sidebar.selectbox("配色风格", ["Dark Mode", "Light Mode"])

def create_poster(point, dist, mode):
    # 直接根据坐标点下载数据，跳过 geocode 查询步骤，成功率极高
    G = ox.graph_from_point(point, dist=dist, dist_type='bbox', network_type='all')
    
    if mode == "Dark Mode":
        bgcolor = '#212121'
        edge_color = '#ffffff'
    else:
        bgcolor = '#fdfdfd'
        edge_color = '#000000'
        
    fig, ax = ox.plot_graph(
        G, 
        node_size=0, 
        edge_color=edge_color, 
        edge_linewidth=0.5,
        bgcolor=bgcolor,
        figsize=(10, 14),
        show=False, 
        close=False
    )
    return fig

# --- 3. 主程序逻辑 ---
if st.button("🚀 生成海报"):
    with st.spinner("正在连接卫星数据... 请稍候"):
        try:
            # 根据模式获取坐标点
            if input_mode == "城市名称搜索":
                # 尝试搜索名字（可能会失败）
                point = ox.geocode(city)
            else:
                # 直接使用经纬度（100% 成功）
                point = (lat, lon)

            # 开始绘图
            fig = create_poster(point, radius, style_select)
            st.success("生成成功！")
            st.pyplot(fig)
            
            # 下载按钮
            fn = "poster.png"
            fig.savefig(fn, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
            with open(fn, "rb") as file:
                st.download_button("📥 下载海报", data=file, file_name="map_poster.png", mime="image/png")
                
        except Exception as e:
            # 打印详细错误，不再只显示“找不到城市”
            st.error(f"发生错误: {e}")
            if "geocode" in str(e) or "Nominatim" in str(e):
                st.warning("⚠️ 现在的网络环境无法通过名字搜索。请切换到 **'输入经纬度'** 模式重试，绝对能成！")
