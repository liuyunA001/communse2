import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 文件中的环境变量
load_dotenv()

# -------------------- 字体配置（解决中文显示方块问题） --------------------
def setup_chinese_font():
    """设置 matplotlib 中文字体，避免方框乱码"""
    # 优先尝试项目内置的字体文件（跨平台兼容）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_dir = os.path.join(script_dir, "fonts")
    font_files = []
    if os.path.exists(font_dir):
        for f in os.listdir(font_dir):
            if f.lower().endswith(('.ttf', '.otf', '.ttc')):
                font_files.append(os.path.join(font_dir, f))
    
    # 如果有内置字体文件，使用它
    for font_path in font_files:
        try:
            fm.fontManager.addfont(font_path)
            font_name = fm.FontProperties(fname=font_path).get_name()
            plt.rcParams['font.sans-serif'] = [font_name, 'DejaVu Sans']
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['axes.unicode_minus'] = False
            plt.rcParams['axes.labelsize'] = 12
            plt.rcParams['axes.titlesize'] = 14
            plt.rcParams['legend.fontsize'] = 10
            plt.rcParams['xtick.labelsize'] = 10
            plt.rcParams['ytick.labelsize'] = 10
            return font_name
        except Exception as e:
            continue
    
    # 否则尝试系统中常见的字体（按平台）
    font_candidates = [
        'Noto Sans CJK SC', 'Noto Sans CJK', 'Noto Sans CJK JP',
        'WenQuanYi Micro Hei', 'WenQuanYi Zen Hei',
        'Source Han Sans SC', 'Source Han Sans CN',
        'Source Han Serif SC', 'Source Han Serif CN',
        'PingFang SC', 'Heiti SC', 'STHeiti',
        'Microsoft YaHei', 'SimHei', 'SimSun', 'FangSong', 'KaiTi',
        'Arial Unicode MS',
        'DejaVu Sans'
    ]
    
    installed_fonts = [f.name for f in fm.fontManager.ttflist]
    
    for font_name in font_candidates:
        if font_name in installed_fonts:
            try:
                plt.rcParams['font.sans-serif'] = [font_name, 'DejaVu Sans']
                plt.rcParams['font.family'] = 'sans-serif'
                plt.rcParams['axes.unicode_minus'] = False
                plt.rcParams['axes.labelsize'] = 12
                plt.rcParams['axes.titlesize'] = 14
                plt.rcParams['legend.fontsize'] = 10
                plt.rcParams['xtick.labelsize'] = 10
                plt.rcParams['ytick.labelsize'] = 10
                return font_name
            except Exception as e:
                continue
    
    # 最后使用默认
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False
    return None

selected_font = setup_chinese_font()

# -------------------- 页面配置 --------------------
st.set_page_config(page_title="校园闲置物品智能交易助手", page_icon="📦", layout="wide")

# -------------------- 自定义 CSS（校园治愈风格） --------------------
st.markdown("""
<style>
    .stApp {
        background-color: #faf8f5;
    }
    .main {
        background: linear-gradient(135deg, #faf8f5 0%, #f2f0eb 100%);
    }
    section[data-testid="stSidebar"] {
        background: rgba(200, 230, 201, 0.35);
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(255,255,255,0.5);
    }
    h1, h2, h3, h4, h5, h6 {
        color: #4a6b4a;
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }
    div.stMetric, div.stDataFrame, div[data-testid="stExpander"], div.stButton > button,
    .stTextInput input, .stSelectbox select, .stNumberInput input, .stTextArea textarea {
        border-radius: 20px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06) !important;
        transition: all 0.3s ease;
    }
    .stTextInput input:hover, .stSelectbox select:hover, .stNumberInput input:hover,
    .stTextArea textarea:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.1) !important;
        border-color: #f3b391 !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #fdd9b5 0%, #f9b482 100%) !important;
        color: #5a4a3a !important;
        font-weight: 600;
        border: none !important;
        padding: 0.6rem 2rem;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(249, 180, 130, 0.4) !important;
        background: linear-gradient(135deg, #f9b482 0%, #f58b5a 100%) !important;
    }
    .stDownloadButton > button, .st-key-settings_btn button {
        background: linear-gradient(135deg, #c8e6c9 0%, #a5d6a7 100%) !important;
        color: #4a6b4a !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #c8e6c9 !important;
        color: #4a6b4a !important;
    }
    .stDataFrame table {
        border-radius: 20px;
    }
    .glass-card {
        background: rgba(255,255,255,0.5);
        backdrop-filter: blur(8px);
        border-radius: 24px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        border: 1px solid rgba(255,255,255,0.8);
    }
    .category-tag {
        display: inline-block;
        padding: 4px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 500;
        margin: 3px 6px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        transition: all 0.2s;
        cursor: pointer;
    }
    .category-tag:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    .corner-decor {
        position: fixed;
        font-size: 60px;
        opacity: 0.15;
        z-index: 0;
        pointer-events: none;
        filter: grayscale(0.3);
    }
    .decor-bike { top: 20px; right: 30px; }
    .decor-book { bottom: 20px; left: 30px; }
    .decor-dorm { top: 50%; left: 10px; font-size: 70px; }
    .decor-cup { bottom: 80px; right: 20px; font-size: 50px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="corner-decor decor-bike">🚲</div>', unsafe_allow_html=True)
st.markdown('<div class="corner-decor decor-book">📚</div>', unsafe_allow_html=True)
st.markdown('<div class="corner-decor decor-dorm">🏠</div>', unsafe_allow_html=True)
st.markdown('<div class="corner-decor decor-cup">🥤</div>', unsafe_allow_html=True)

# -------------------- 初始化会话状态 --------------------
if "selected_items" not in st.session_state:
    st.session_state.selected_items = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "show_quick_sell" not in st.session_state:
    st.session_state.show_quick_sell = False
if "quick_filter_category" not in st.session_state:
    st.session_state.quick_filter_category = None
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "my_items" not in st.session_state:
    st.session_state.my_items = []
if "item_status" not in st.session_state:
    st.session_state.item_status = {}  # 记录商品状态：上架/下架

# -------------------- 数据加载 --------------------
@st.cache_data
def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, "data", "items.csv")
    
    if not os.path.exists(data_path):
        st.error(f"数据文件未找到：{data_path}")
        st.info("请确保 data/items.csv 文件存在于正确的位置")
        
        sample_data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['高等数学教材', '台灯', '充电宝'],
            'category': ['教材', '电器', '数码'],
            'price': [35.0, 45.0, 68.0],
            'condition': ['八成新', '九成新', '九成新'],
            'college': ['计算机学院', '材料学院', '自动化学院'],
            'seller_grade': ['大三', '大一', '大三'],
            'sales_count': [12, 18, 14],
            'post_date': pd.to_datetime(['2024-03-15', '2024-03-16', '2024-03-14']),
            'description': ['同济大学高等数学教材', 'LED护眼灯', '20000mAh快充'],
            'contact': ['QQ:123456789', 'QQ:567890123', '微信:powerbank2024']
        })
        sample_data['month'] = sample_data['post_date'].dt.month_name()
        return sample_data
    
    df = pd.read_csv(data_path)
    df['post_date'] = pd.to_datetime(df['post_date'], format='mixed')
    df['month'] = df['post_date'].dt.month_name()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"加载数据时发生错误: {str(e)}")
    st.stop()

# -------------------- AI 客户端 --------------------
def get_ai_client():
    """获取AI客户端，优先使用环境变量配置"""
    api_key = os.getenv("API_KEY") or st.session_state.get("api_key", "")
    base_url = os.getenv("BASE_URL") or st.session_state.get("base_url", "https://api.deepseek.com/v1")
    model = os.getenv("MODEL") or st.session_state.get("model", "deepseek-chat")
    
    if api_key:
        st.session_state.api_key = api_key
        st.session_state.base_url = base_url
        st.session_state.model = model
        return OpenAI(api_key=api_key, base_url=base_url)
    return None

def test_api_connection():
    """测试API连接状态"""
    client = get_ai_client()
    if not client:
        return {"status": "error", "message": "未配置API Key"}
    
    try:
        response = client.chat.completions.create(
            model=st.session_state.get("model", "deepseek-chat"),
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        if response.choices:
            return {"status": "success", "message": "API连接正常"}
        else:
            return {"status": "error", "message": "API响应异常"}
    except Exception as e:
        return {"status": "error", "message": f"连接失败: {str(e)}"}

# -------------------- 提示词 --------------------
MATCH_PROMPT = """
你是一个校园闲置物品智能匹配助手。
用户会提供他们的预算、年级和所需物品类型（如教材、电器等）。
请根据以下商品列表，为用户推荐最合适的3-5件商品。

商品列表：
{items_info}

用户需求：
{user_query}

请以友好、简洁的方式列出匹配的商品，包括：商品名称、类别、价格、成色、卖家年级。
"""

DESC_PROMPT = """
你是一个校园闲置物品文案撰写和估价专家。
请根据以下商品信息：
- 商品名称：{item_name}
- 类别：{category}
- 成色：{condition}
- 当前价格：{price}元
- 描述：{description}

请完成以下任务：
1. 撰写一段吸引人的商品介绍文案（30-50字）
2. 给出一个合理的估价范围

输出格式：
【商品文案】：xxx
【估价范围】：xxx元 - xxx元
"""

POLISH_PROMPT = """
你是一个专业的文案润色专家。请帮我把以下商品描述变得更吸引人、更有说服力：

原始描述：
{original_text}

商品名称：{item_name}
商品类别：{category}
商品成色：{condition}
商品价格：{price}元

请润色这段描述，使其：
1. 更加生动、吸引人
2. 突出商品的优点和卖点
3. 使用恰当的形容词
4. 保持在50-80字左右

润色后的文案：
"""

QA_PROMPT = """
你是一个校园闲置物品交易平台的智能客服助手。
请回答用户关于闲置物品交易的问题。

可用功能：
1. 🎯 货源匹配 - 根据用户需求推荐合适的商品
2. ✍️ 文案生成 - 为商品生成吸引人的描述
3. 💰 价格建议 - 分析商品给出合理定价
4. 🔍 智能搜索 - 语义搜索商品

常见问题：
- 如何发布闲置物品？
- 如何搜索商品？
- 交易流程是怎样的？
- 如何联系卖家？
- 如何保障交易安全？

请用友好、简洁的语言回答用户问题。如果是关于商品匹配或搜索的请求，请说明可以使用货源匹配功能。
"""

SEARCH_PROMPT = """
你是一个智能商品搜索助手。请根据用户的搜索查询，分析用户可能想要找的商品类型。

用户查询：{query}

请从以下商品列表中找出最相关的商品：
{items_info}

请列出3-5个最相关的商品，包括：商品名称、类别、价格、成色。
如果没有找到相关商品，请说明没有匹配结果。
"""

# 系统提示词 - 用于上下文理解
SYSTEM_PROMPT = """
你是一个校园闲置物品交易平台的AI助手"校园小闲"。

你的职责：
1. 理解用户的需求并提供帮助
2. 可以进行货源匹配、文案生成、价格建议、智能搜索
3. 回答关于平台使用的问题
4. 保持友好、专业的语气

对话历史：
{history}

当前用户消息：
{user_message}

请根据对话历史理解上下文，并给出合适的回复。
如果是商品匹配或搜索请求，请使用货源匹配功能；如果是文案相关请求，请使用文案生成功能。
"""

# -------------------- 管理员设置 --------------------
if "show_settings" not in st.session_state:
    st.session_state.show_settings = False
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

ADMIN_PASSWORD = "qimodazuoye123"

col1, col2 = st.columns([1, 0.1])
with col2:
    if st.button("⚙️", key="settings_btn", help="设置"):
        st.session_state.show_settings = not st.session_state.show_settings

if st.session_state.show_settings:
    with st.expander("⚙️ 系统设置", expanded=True):
        st.subheader("🔐 管理员登录")
        admin_pwd = st.text_input("管理员密码", type="password")
        if st.button("登录"):
            if admin_pwd == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.success("管理员登录成功！")
            else:
                st.error("密码错误")
        if st.session_state.is_admin:
            st.info("当前为管理员模式")

# -------------------- 侧边栏 --------------------
with st.sidebar:
    st.markdown("""
    <div class="glass-card">
        <div style="text-align: center;">
            <span style="font-size: 48px;">🧑‍🎓</span>
            <h4 style="margin: 0.5rem 0 0.2rem; color: #4a6b4a;">校园小闲</h4>
            <p style="color: #888; font-size: 14px;">游客模式 · 未登录</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🪄 快速发布闲置")
    if st.button("打开快速发布", key="toggle_quick_sell"):
        st.session_state.show_quick_sell = not st.session_state.show_quick_sell
    
    if st.session_state.show_quick_sell:
        with st.form("quick_sell_form"):
            q_name = st.text_input("物品名称", placeholder="例：高等数学教材")
            q_cat = st.selectbox("类别", ["教材", "电器", "数码", "家具", "服装", "运动", "美妆", "其他"])
            q_price = st.number_input("价格", min_value=0, step=1)
            q_contact = st.text_input("联系方式", placeholder="QQ/微信")
            if st.form_submit_button("🚀 立即发布"):
                if q_name and q_price > 0 and q_contact:
                    new_item = pd.DataFrame({
                        'id': [len(df) + 1],
                        'name': [q_name],
                        'category': [q_cat],
                        'price': [q_price],
                        'condition': ["几乎全新"],
                        'college': ["未知"],
                        'seller_grade': ["未知"],
                        'sales_count': [0],
                        'post_date': [pd.Timestamp.now()],
                        'description': [""],
                        'contact': [q_contact]
                    })
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    data_path = os.path.join(script_dir, "data", "items.csv")
                    new_item.to_csv(data_path, mode='a', header=False, index=False)
                    st.success("🎉 发布成功！")
                    st.session_state.show_quick_sell = False
                    st.rerun()
                else:
                    st.error("请填写名称、价格和联系方式")
    
    st.markdown("---")
    st.header("🔍 数据筛选")
    
    # 关键词搜索
    search_keyword = st.text_input("🔍 搜索商品", placeholder="输入商品名称关键词...")
    
    selected_college = st.selectbox("选择学院", ["全部"] + sorted(df['college'].unique()))
    price_range = st.slider("价格范围", 0, 3000, (0, 3000))
    
    st.caption("🎨 分类快捷筛选")
    categories = ["全部", "教材", "电器", "数码", "家具", "服装", "运动", "美妆", "食品", "书籍"]
    color_map = {
        "教材": "#E8F5E9", "电器": "#FFF3E0", "数码": "#E3F2FD", "家具": "#F3E5F5",
        "服装": "#FCE4EC", "运动": "#E0F7FA", "美妆": "#F1F8E9", "食品": "#FFF9C4", "书籍": "#EDE7F6"
    }
    cols = st.columns(5)
    for i, cat in enumerate(categories):
        with cols[i % 5]:
            if st.button(cat, key=f"cat_{cat}", use_container_width=True):
                if cat == "全部":
                    st.session_state.quick_filter_category = None
                else:
                    st.session_state.quick_filter_category = cat
    
    quick_cat = st.session_state.get("quick_filter_category")
    if quick_cat:
        st.info(f"当前快速筛选：{quick_cat}")
    
    filtered_df = df.copy()
    
    # 关键词搜索过滤
    if search_keyword.strip():
        filtered_df = filtered_df[filtered_df['name'].str.contains(search_keyword.strip(), case=False)]
    
    if selected_college != "全部":
        filtered_df = filtered_df[filtered_df['college'] == selected_college]
    filtered_df = filtered_df[(filtered_df['price'] >= price_range[0]) & (filtered_df['price'] <= price_range[1])]
    if quick_cat:
        filtered_df = filtered_df[filtered_df['category'] == quick_cat]

# -------------------- 主页面 --------------------
st.title("📦 校园闲置物品智能交易助手")
st.subheader("让闲置物品找到新主人")

tabs_list = ["🤖 AI智能助手", "📦 商品列表", "💰 发布商品", "👤 我的管理"]
if st.session_state.is_admin:
    tabs_list.append("📊 数据看板")

tab_objects = st.tabs(tabs_list)
tab_ai = tab_objects[0]
tab_items = tab_objects[1]
tab_sell = tab_objects[2]
tab_my = tab_objects[3]
tab_data = tab_objects[4] if st.session_state.is_admin else None

# -------------------- 数据看板（治愈系配色） --------------------
if st.session_state.is_admin and tab_data:
    # 治愈系马卡龙配色（低饱和，清新不刺眼）
    healing_colors = [
        '#A8DADC',  # 浅蓝绿
        '#F4A261',  # 暖杏橘
        '#E9C46A',  # 奶油黄
        '#A5D6A7',  # 青草绿
        '#FFCDB2',  # 浅蜜瓜
        '#B0C4DE',  # 淡钢蓝
        '#D4A5A5',  # 淡豆沙粉
        '#C3E8B0',  # 薄荷绿
        '#FBC4AB',  # 蜜桃杏
        '#B8E0D2'   # 浅薄荷蓝
    ]

    with tab_data:
        st.markdown("### 📊 数据概览")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 商品总数", len(filtered_df))
        with col2:
            st.metric("💰 总销售额", f"{(filtered_df['price'] * filtered_df['sales_count']).sum():.2f}元")
        with col3:
            st.metric("📈 平均价格", f"{filtered_df['price'].mean():.2f}元")
        with col4:
            st.metric("🔥 热销商品数", len(filtered_df[filtered_df['sales_count'] > 10]))

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📈 商品类别分布")
            category_counts = filtered_df['category'].value_counts()
            fig1, ax1 = plt.subplots(figsize=(6,5))
            wedges, texts, autotexts = ax1.pie(
                category_counts,
                labels=category_counts.index,
                autopct='%1.1f%%',
                startangle=90,
                colors=healing_colors[:len(category_counts)],   # 治愈色系
                wedgeprops={'edgecolor':'white','linewidth':2},
                textprops={'fontsize': 10}
            )
            ax1.axis('equal')
            plt.setp(autotexts, size=9, weight='bold', color='#333333')
            plt.setp(texts, fontsize=10)
            st.pyplot(fig1)

        with col2:
            st.markdown("### 💰 价格区间分布")
            bins = [0,50,100,200,500,3000]
            labels = ['0-50', '50-100', '100-200', '200-500', '500+']
            filtered_df['price_range'] = pd.cut(filtered_df['price'], bins=bins, labels=labels)
            price_dist = filtered_df['price_range'].value_counts().sort_index()
            fig2, ax2 = plt.subplots(figsize=(6,5))
            bars = ax2.bar(price_dist.index, price_dist.values, color=healing_colors[:5])  # 治愈色系
            ax2.set_xlabel('价格区间(元)', fontsize=11)
            ax2.set_ylabel('商品数量', fontsize=11)
            ax2.grid(axis='y', alpha=0.3)
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom', fontsize=10)
            st.pyplot(fig2)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📅 月度发布趋势")
            month_order = ['March','April']
            monthly_data = filtered_df['month'].value_counts().reindex(month_order, fill_value=0)
            fig3, ax3 = plt.subplots(figsize=(6,5))
            ax3.plot(monthly_data.index, monthly_data.values, marker='o', color='#F4A261', linewidth=3)  # 暖杏橘
            ax3.fill_between(monthly_data.index, monthly_data.values, alpha=0.3, color='#FFCDB2')       # 浅蜜瓜填充
            ax3.set_xlabel('月份', fontsize=11)
            ax3.set_ylabel('发布数量', fontsize=11)
            ax3.grid(axis='y', alpha=0.3)
            st.pyplot(fig3)

        with col2:
            st.markdown("### 🔥 热门商品TOP10")
            top_sales = filtered_df.sort_values('sales_count', ascending=False).head(10)
            st.dataframe(top_sales[['name','category','price','sales_count','college']],
                         hide_index=True,
                         column_config={
                             "name":"商品名称","category":"类别",
                             "price":st.column_config.NumberColumn("价格(元)", format="%.2f"),
                             "sales_count":"销量","college":"学院"
                         })

# -------------------- AI 智能助手 --------------------
def get_items_info(items_df):
    """生成商品信息字符串，用于AI提示词"""
    return "\n".join([f"- {row['name']} | {row['category']} | {row['price']}元 | {row['condition']} | {row['college']} | {row['seller_grade']}" 
                      for _, row in items_df.iterrows()])

def detect_intent(user_message):
    """检测用户意图"""
    message = user_message.lower()
    intent = "qa"  # 默认是问答
    
    # 检测货源匹配意图
    if any(keyword in message for keyword in ['预算', '需要', '想买', '求购', '推荐', '匹配', '找']):
        intent = "match"
    
    # 检测文案生成意图
    elif any(keyword in message for keyword in ['文案', '描述', '介绍', '写', '生成']):
        intent = "desc"
    
    # 检测搜索意图
    elif any(keyword in message for keyword in ['搜索', '查找', '找', '有没有']):
        intent = "search"
    
    # 检测价格相关意图
    elif any(keyword in message for keyword in ['价格', '多少钱', '定价', '估价']):
        intent = "price"
    
    return intent

def build_context_history():
    """构建对话历史上下文"""
    history = []
    for msg in st.session_state.chat_history[-5:]:  # 保留最近5条对话
        role = "用户" if msg['role'] == 'user' else "助手"
        history.append(f"{role}: {msg['content']}")
    return "\n".join(history)

with tab_ai:
    st.subheader("🤖 智能客服")
    
    # 使用示例（匹配数据库中的商品）
    st.markdown("""
    <div style="background: linear-gradient(135deg, #E8F5E9 0%, #E3F2FD 100%); padding: 1rem 1.5rem; border-radius: 12px; margin-bottom: 1rem;">
        <strong style="color: #4a6b4a;">💡 试试这些示例：</strong>
        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.8rem;">
            <span style="background: white; padding: 6px 12px; border-radius: 16px; font-size: 13px; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.08);" onclick="document.querySelector('input[placeholder*=需求]').value='需要教材'; document.querySelector('input[placeholder*=需求]').focus();">
                需要教材
            </span>
            <span style="background: white; padding: 6px 12px; border-radius: 16px; font-size: 13px; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.08);" onclick="document.querySelector('input[placeholder*=需求]').value='预算50元，需要电器'; document.querySelector('input[placeholder*=需求]').focus();">
                预算50元，需要电器
            </span>
            <span style="background: white; padding: 6px 12px; border-radius: 16px; font-size: 13px; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.08);" onclick="document.querySelector('input[placeholder*=需求]').value='需要数码产品'; document.querySelector('input[placeholder*=需求]').focus();">
                需要数码产品
            </span>
            <span style="background: white; padding: 6px 12px; border-radius: 16px; font-size: 13px; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.08);" onclick="document.querySelector('input[placeholder*=需求]').value='数学教材'; document.querySelector('input[placeholder*=需求]').focus();">
                数学教材
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 初始化对话历史
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # 显示对话历史
    for msg in st.session_state.chat_history:
        if msg['role'] == 'user':
            with st.chat_message("user", avatar="👤"):
                st.write(msg['content'])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.write(msg['content'])
    
    # 输入区域 - 使用普通输入框以便按钮能读取内容
    user_input_text = st.text_input("请输入您的需求...", key="user_input_field")
    
    # 精简按钮（仅保留核心功能）
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎯 智能匹配", use_container_width=True):
            # 获取输入框中的内容
            input_text = st.session_state.get("user_input_field", "").strip()
            if not input_text:
                input_text = "帮我推荐合适的商品"
            
            # 添加用户消息到历史
            st.session_state.chat_history.append({"role":"user","content":input_text})
            
            # 检测用户意图并处理
            intent = detect_intent(input_text)
            client = get_ai_client()
            
            if intent == "match":
                matched_items = df.copy()
                import re
                price_match = re.search(r'预算(\d+)元|价格(\d+)元|(\d+)元', input_text)
                if price_match:
                    target_price = int(price_match.group(1) or price_match.group(2) or price_match.group(3))
                    matched_items = matched_items[(matched_items['price'] >= target_price - 100) & 
                                                  (matched_items['price'] <= target_price + 100)]
                category_keywords = ['教材','电器','数码','家具','服装','运动','美妆','食品','书籍']
                matched_categories = [k for k in category_keywords if k in input_text]
                if matched_categories:
                    matched_items = matched_items[matched_items['category'].str.contains('|'.join(matched_categories))]
                
                if len(matched_items) == 0:
                    result = "😔 没有找到匹配的商品，试试其他关键词吧！"
                else:
                    items_info = get_items_info(matched_items)
                    prompt = MATCH_PROMPT.format(items_info=items_info, user_query=input_text)
                    
                    if client:
                        with st.spinner("正在匹配货源..."):
                            try:
                                response = client.chat.completions.create(
                                    model=st.session_state.model,
                                    messages=[{"role":"user","content":prompt}],
                                    temperature=0.7
                                )
                                result = response.choices[0].message.content
                            except Exception as e:
                                result = f"AI调用失败，显示原始匹配结果：\n{items_info}"
                    else:
                        result = f"API Key未配置，显示原始匹配结果：\n{items_info}"
            else:
                if client:
                    with st.spinner("正在思考..."):
                        try:
                            response = client.chat.completions.create(
                                model=st.session_state.model,
                                messages=[{"role":"user","content":input_text}],
                                temperature=0.7
                            )
                            result = response.choices[0].message.content
                        except Exception as e:
                            result = f"AI调用失败: {str(e)}"
                else:
                    result = "请先配置API Key"
            
            st.session_state.chat_history.append({"role":"assistant","content":result})
            st.rerun()
    with col2:
        if st.button("🔄 清空对话", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    # 底部API状态提示（自动检测）
    api_key = os.getenv("API_KEY") or st.session_state.get("api_key", "")
    if api_key:
        st.markdown("<p style='text-align: center; font-size: 12px; color: #4CAF50; margin-top: 1rem;'>✅ API已配置</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='text-align: center; font-size: 12px; color: #FF9800; margin-top: 1rem;'>⚠️ API未配置，部分功能受限</p>", unsafe_allow_html=True)
    
# -------------------- 商品列表 --------------------
with tab_items:
    st.subheader("📦 商品列表")
    
    # 显示筛选结果数量
    st.info(f"当前显示 {len(filtered_df)} 件商品")
    
    # 收藏列表入口
    if st.session_state.favorites:
        with st.expander(f"❤️ 我的收藏 ({len(st.session_state.favorites)})", expanded=False):
            favorite_ids = [item['id'] for item in st.session_state.favorites]
            favorite_df = df[df['id'].isin(favorite_ids)]
            st.dataframe(favorite_df[['name','category','price','condition','college','contact']],
                         hide_index=True,
                         column_config={
                             "name":"商品名称","category":"类别",
                             "price":st.column_config.NumberColumn("价格(元)", format="%.2f"),
                             "condition":"成色","college":"学院","contact":"联系方式"
                         })
    
    # 商品卡片展示
    if len(filtered_df) > 0:
        for _, row in filtered_df.iterrows():
            is_favorite = row['id'] in [item['id'] for item in st.session_state.favorites]
            
            with st.container():
                col_info, col_action = st.columns([4, 1])
                with col_info:
                    st.markdown(f"""
                    <div class="glass-card" style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="flex: 1;">
                            <h4 style="margin: 0 0 8px;">{row['name']}</h4>
                            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                                <span style="background: #E8F5E9; padding: 4px 12px; border-radius: 12px; font-size: 12px;">{row['category']}</span>
                                <span style="background: #FFF3E0; padding: 4px 12px; border-radius: 12px; font-size: 12px;">{row['condition']}</span>
                                <span style="background: #E3F2FD; padding: 4px 12px; border-radius: 12px; font-size: 12px;">{row['college']}</span>
                            </div>
                            <p style="margin: 8px 0; color: #666; font-size: 14px;">{row['description'] if row['description'] else '暂无描述'}</p>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="font-size: 20px; font-weight: bold; color: #E57373;">¥{row['price']}</span>
                                <span style="font-size: 12px; color: #888;">卖家年级: {row['seller_grade']}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_action:
                    # 收藏按钮
                    if st.button("❤️" if is_favorite else "🤍", 
                                key=f"favorite_{row['id']}",
                                help="收藏/取消收藏"):
                        if is_favorite:
                            st.session_state.favorites = [item for item in st.session_state.favorites if item['id'] != row['id']]
                        else:
                            st.session_state.favorites.append({
                                'id': row['id'],
                                'name': row['name'],
                                'category': row['category'],
                                'price': row['price']
                            })
                        st.rerun()
                    # 显示联系方式
                    st.markdown(f"""
                    <div style="margin-top: 8px; padding: 8px; background: #f8f9fa; border-radius: 8px;">
                        <small style="color: #666;">联系方式:</small>
                        <p style="margin: 4px 0; font-size: 12px;">{row['contact']}</p>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.warning("😔 没有找到符合条件的商品")

# -------------------- 发布商品 --------------------
with tab_sell:
    st.subheader("💰 发布闲置商品")
    st.markdown("填写以下信息发布您的闲置物品")
    
    # 使用 session_state 保存表单数据，以便在表单外使用
    if "sell_item_name" not in st.session_state:
        st.session_state.sell_item_name = ""
    if "sell_category" not in st.session_state:
        st.session_state.sell_category = "教材"
    if "sell_price" not in st.session_state:
        st.session_state.sell_price = 0
    if "sell_condition" not in st.session_state:
        st.session_state.sell_condition = "全新"
    if "sell_college" not in st.session_state:
        st.session_state.sell_college = sorted(df['college'].unique())[0]
    if "sell_seller_grade" not in st.session_state:
        st.session_state.sell_seller_grade = "大一"
    if "sell_contact" not in st.session_state:
        st.session_state.sell_contact = ""
    if "sell_description" not in st.session_state:
        st.session_state.sell_description = ""
    
    # 使用回调函数实时更新 session_state（不受表单提交限制）
    def update_session_state(key, value):
        st.session_state[key] = value
    
    with st.form("sell_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.sell_item_name = st.text_input("商品名称", placeholder="例如：iPhone 13", value=st.session_state.sell_item_name)
            st.session_state.sell_category = st.selectbox("商品类别",
                ["教材","电器","数码","家具","服装","运动","美妆","其他","数码配件","日用品","运动器材","乐器","鞋靴","箱包"],
                index=["教材","电器","数码","家具","服装","运动","美妆","其他","数码配件","日用品","运动器材","乐器","鞋靴","箱包"].index(st.session_state.sell_category))
            st.session_state.sell_price = st.number_input("价格（元）", min_value=0, step=1, value=st.session_state.sell_price)
            st.session_state.sell_condition = st.selectbox("商品成色", ["全新","几乎全新","轻微使用痕迹","明显使用痕迹"],
                index=["全新","几乎全新","轻微使用痕迹","明显使用痕迹"].index(st.session_state.sell_condition))
        with col2:
            st.session_state.sell_college = st.selectbox("学院", sorted(df['college'].unique()),
                index=sorted(df['college'].unique()).index(st.session_state.sell_college))
            st.session_state.sell_seller_grade = st.selectbox("卖家年级", ["大一","大二","大三","大四","研究生"],
                index=["大一","大二","大三","大四","研究生"].index(st.session_state.sell_seller_grade))
            st.session_state.sell_contact = st.text_input("联系方式", placeholder="例如：QQ:123456789 或 微信:xxx", value=st.session_state.sell_contact)
            st.session_state.sell_description = st.text_area("商品描述", placeholder="描述商品的具体情况...", height=100, value=st.session_state.sell_description)
        
        # 如果有润色后的文案，显示它
        if "polished_description" in st.session_state and st.session_state.polished_description:
            st.success("🎉 文案润色完成！")
            st.text_area("润色后的描述", value=st.session_state.polished_description, height=100, disabled=True)
        
        submit_btn = st.form_submit_button("发布商品")
        if submit_btn:
            item_name = st.session_state.sell_item_name
            category = st.session_state.sell_category
            price = st.session_state.sell_price
            condition = st.session_state.sell_condition
            college = st.session_state.sell_college
            seller_grade = st.session_state.sell_seller_grade
            contact = st.session_state.sell_contact
            description = st.session_state.sell_description
            
            # 如果有润色后的文案，使用它
            if "polished_description" in st.session_state and st.session_state.polished_description:
                description = st.session_state.polished_description
            
            if item_name and category and price > 0 and contact:
                new_item = pd.DataFrame({
                    'id': [len(df) + 1],
                    'name': [item_name],
                    'category': [category],
                    'price': [price],
                    'condition': [condition],
                    'college': [college],
                    'seller_grade': [seller_grade],
                    'sales_count': [0],
                    'post_date': [pd.Timestamp.now()],
                    'description': [description],
                    'contact': [contact]
                })
                script_dir = os.path.dirname(os.path.abspath(__file__))
                data_path = os.path.join(script_dir, "data", "items.csv")
                new_item.to_csv(data_path, mode='a', header=False, index=False)
                st.success("🎉 商品发布成功！")
                # 将商品添加到「我的商品」列表
                new_item_info = {
                    'id': len(df) + 1,
                    'name': item_name,
                    'category': category,
                    'price': price,
                    'condition': condition,
                    'college': college,
                    'seller_grade': seller_grade,
                    'contact': contact,
                    'description': description
                }
                st.session_state.my_items.append(new_item_info)
                st.session_state.item_status[str(len(df) + 1)] = '上架'
                # 清空表单和润色文案
                st.session_state.sell_item_name = ""
                st.session_state.sell_category = "教材"
                st.session_state.sell_price = 0
                st.session_state.sell_condition = "全新"
                st.session_state.sell_college = sorted(df['college'].unique())[0]
                st.session_state.sell_seller_grade = "大一"
                st.session_state.sell_contact = ""
                st.session_state.sell_description = ""
                if "polished_description" in st.session_state:
                    del st.session_state.polished_description
                st.rerun()
            else:
                st.error("请填写完整的商品信息（名称、类别、价格、联系方式为必填项）")
    
    # AI 润色文案功能（在表单外面）- 帮您撰写更吸引人的商品描述
    col_polish, col_clear = st.columns(2)
    with col_polish:
        polish_btn = st.button("✨ AI 润色描述", help="帮您将商品描述变得更吸引人，突出卖点")
    with col_clear:
        clear_polish_btn = st.button("🗑️ 清除润色")
    
    if polish_btn:
        item_name = st.session_state.sell_item_name
        description = st.session_state.sell_description
        category = st.session_state.sell_category
        condition = st.session_state.sell_condition
        price = st.session_state.sell_price
        
        # 调试信息
        st.write(f"item_name: '{item_name}', len={len(item_name) if item_name else 0}")
        st.write(f"description: '{description}', len={len(description) if description else 0}")
        
        if item_name.strip() and description.strip():
            client = get_ai_client()
            if client:
                with st.spinner("AI正在润色文案..."):
                    try:
                        prompt = POLISH_PROMPT.format(
                            original_text=description,
                            item_name=item_name,
                            category=category,
                            condition=condition,
                            price=price
                        )
                        response = client.chat.completions.create(
                            model=st.session_state.model,
                            messages=[{"role":"user","content":prompt}],
                            temperature=0.7
                        )
                        polished_text = response.choices[0].message.content.strip()
                        st.session_state.polished_description = polished_text
                        st.rerun()
                    except Exception as e:
                        st.error(f"AI润色失败: {str(e)}")
            else:
                st.warning("请先配置API Key")
        else:
            st.warning("请先填写商品名称和描述")
    
    if clear_polish_btn:
        if "polished_description" in st.session_state:
            del st.session_state.polished_description
            st.rerun()

# -------------------- 我的管理 --------------------
with tab_my:
    st.subheader("👤 我的管理")
    
    # 收藏管理
    st.markdown("### ❤️ 我的收藏")
    if st.session_state.favorites:
        for idx, item in enumerate(st.session_state.favorites):
            col_info, col_action = st.columns([4, 1])
            with col_info:
                st.markdown(f"""
                <div class="glass-card">
                    <h4>{item['name']}</h4>
                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                        <span style="background: #E8F5E9; padding: 4px 12px; border-radius: 12px; font-size: 12px;">{item['category']}</span>
                        <span style="background: #FFF3E0; padding: 4px 12px; border-radius: 12px; font-size: 12px;">¥{item['price']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col_action:
                if st.button(f"🗑️", key=f"del_fav_{idx}", help="取消收藏"):
                    st.session_state.favorites.pop(idx)
                    st.rerun()
    else:
        st.info("暂无收藏的商品")
    
    st.markdown("---")
    
    # 我的商品管理
    st.markdown("### 📦 我的商品")
    if st.session_state.my_items:
        for idx, item in enumerate(st.session_state.my_items):
            item_id_str = str(item['id'])
            status = st.session_state.item_status.get(item_id_str, '上架')
            
            with st.container():
                st.markdown(f"""
                <div class="glass-card">
                    <h4>{item['name']}</h4>
                    <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px;">
                        <span style="background: #E8F5E9; padding: 4px 12px; border-radius: 12px; font-size: 12px;">{item['category']}</span>
                        <span style="background: #FFF3E0; padding: 4px 12px; border-radius: 12px; font-size: 12px;">{item['condition']}</span>
                        <span style="background: {'#C8E6C9' if status == '上架' else '#FFCDD2'}; padding: 4px 12px; border-radius: 12px; font-size: 12px;">{status}</span>
                    </div>
                    <p style="color: #666; font-size: 14px; margin-bottom: 8px;">{item['description'] if item['description'] else '暂无描述'}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 操作区域
                col_price, col_status, col_delete = st.columns([2, 2, 1])
                with col_price:
                    new_price = st.number_input(f"修改价格（元）", min_value=0, step=1, value=item['price'], key=f"price_{item_id_str}")
                    if st.button(f"💾 保存价格", key=f"save_price_{item_id_str}"):
                        item['price'] = new_price
                        st.success("价格已更新！")
                
                with col_status:
                    if st.button(f"🔄 {'下架' if status == '上架' else '上架'}", key=f"toggle_{item_id_str}"):
                        new_status = '下架' if status == '上架' else '上架'
                        st.session_state.item_status[item_id_str] = new_status
                        st.rerun()
                
                with col_delete:
                    if st.button(f"🗑️ 删除", key=f"del_item_{item_id_str}"):
                        st.session_state.my_items.pop(idx)
                        del st.session_state.item_status[item_id_str]
                        st.rerun()
    else:
        st.info("暂无发布的商品")

st.markdown("---")
st.caption(" 提示：AI功能已自动配置，可直接使用")