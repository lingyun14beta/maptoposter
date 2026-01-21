import streamlit as st
import osmnx as ox
import matplotlib.pyplot as plt

# --- 关键修复：伪装身份，防止被 OSM 封锁 ---
# 这一步告诉服务器我们是谁，避免被当成机器人拒绝连接
ox.settings.user_agent = "student-project-map-poster/1.0 (contact: yourname@example.com)"
ox.settings.requests_timeout = 30  # 增加超时时间，防止网络卡顿

# --- 页面设置 ---
st.set_page_config(page_title="城市地图海报生成器", layout="centered")
st.title("🗺️ 城市地图海报生成器")

# --- 侧边栏 ---
st.sidebar.header("参数设置")
city = st.sidebar.text_input("城市名称 (英文)", "Beijing, China")
radius = st.sidebar.slider("地图半径 (米)", 1000, 5000, 2000, step=500)
style_select = st.sidebar.selectbox("配色风格", ["Dark Mode", "Light Mode"])

def create_poster(place_name, dist, mode):
    # 1. 获取坐标 (增加错误处理)
    try:
        point = ox.geocode(place_name)
    except Exception:
        # 如果搜索失败，抛出更直观的错误
        raise ValueError(f"找不到城市: {place_name}。请尝试使用 'City, Country' 的格式（例如: Shanghai, China）")

    # 2. 下载路网数据
    # network_type='all' 包含所有道路，'drive' 只包含车道
    G = ox.graph_from_point(point, dist=dist, dist_type='bbox', network_type='all')
    
    # 3. 设定颜色
    if mode == "Dark Mode":
        bgcolor = '#212121' # 深灰背景
        edge_color = '#ffffff' # 白色线条
    else:
        bgcolor = '#fdfdfd' # 纯白背景
        edge_color = '#000000' # 黑色线条
        
    # 4. 绘图 (关闭显示以加速)
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

# --- 主逻辑 ---
if st.button("🚀 生成海报"):
    # 显示加载动画
    with st.spinner(f"正在连接卫星数据... 绘制 {city} 需要约 15-30 秒"):
        try:
            # 调用绘图函数
            fig = create_poster(city, radius, style_select)
            
            # 成功展示
            st.success("绘制完成！")
            st.pyplot(fig)
            
            # 生成下载文件
            fn = "poster.png"
            fig.savefig(fn, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
            
            with open(fn, "rb") as file:
                st.download_button(
                    label="📥 下载高清海报",
                    data=file,
                    file_name=f"map_{city}.png",
                    mime="image/png"
                )
                
        except ValueError as ve:
            st.warning(str(ve))
        except Exception as e:
            st.error(f"网络连接错误或内存不足: {e}")
            st.info("提示：如果是连接超时，请多点几次按钮重试。Streamlit 的免费服务器网络有时会波动。")
