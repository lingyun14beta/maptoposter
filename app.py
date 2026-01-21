import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt

st.set_page_config(page_title="城市地图海报生成器", layout="centered")
st.title("🗺️ 城市地图海报生成器")

# 侧边栏
st.sidebar.header("参数设置")
city = st.sidebar.text_input("城市名称 (英文)", "Beijing, China")
radius = st.sidebar.slider("地图半径 (米)", 1000, 5000, 2000, step=500)
style_select = st.sidebar.selectbox("配色风格", ["Dark Mode", "Light Mode"])

def create_poster(place_name, dist, mode):
    # 下载数据
    point = ox.geocode(place_name)
    G = ox.graph_from_point(point, dist=dist, dist_type='bbox', network_type='all')
    
    # 设定颜色
    if mode == "Dark Mode":
        bgcolor = '#000000'
        edge_color = '#ffffff'
    else:
        bgcolor = '#ffffff'
        edge_color = '#000000'
        
    # 绘图
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

if st.button("🚀 生成海报"):
    with st.spinner(f"正在绘制 {city}... 请耐心等待"):
        try:
            fig = create_poster(city, radius, style_select)
            st.pyplot(fig)
            
            # 保存下载
            fn = "poster.png"
            fig.savefig(fn, dpi=100, bbox_inches='tight', facecolor=fig.get_facecolor())
            with open(fn, "rb") as file:
                st.download_button("📥 下载海报", data=file, file_name=f"map_{city}.png", mime="image/png")
        except Exception as e:
            st.error(f"出错：{e}")
            st.warning("提示：请检查城市拼写是否正确")
