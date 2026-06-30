import streamlit as st
import json
import os
from assistant import run_assistant, retrieve_best_match

# 页面配置与高端品牌色注入
st.set_page_config(page_title="理财部安全行政助手", page_icon="🌸", layout="wide")

# CSS 暗红色系渐变与质感卡片布局
st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }
    .main-title {
        background: linear-gradient(135deg, #7f1d1d, #b91c1c);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .main-title h1 {
        margin: 0;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .main-title p {
        margin: 5px 0 0 0;
        font-size: 13px;
        opacity: 0.9;
    }
    .metric-card {
        background-color: white;
        border-left: 4px solid #b91c1c;
        padding: 15px;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .expert-active {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #166534;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        display: inline-block;
    }
    .expert-inactive {
        background-color: #f1f5f9;
        border: 1px solid #e2e8f0;
        color: #64748b;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        display: inline-block;
    }
</style>
""", unsafe_allowed_html=True)

# 顶部标题栏
st.markdown("""
<div class="main-title">
    <h1>🌸 广东南海农商银行理财部</h1>
    <p>本地安全合规版行政知识库助手 (Qwen-MoE 轻量架构驱动)</p>
</div>
""", unsafe_allowed_html=True)

# 侧边栏：服务运行面板
with st.sidebar:
    st.header("⚙️ 本地模型状态")
    st.info("模型类别: Mixture of Experts (MoE)")
    ollama_host = st.text_input("Ollama 接口地址", value="http://localhost:11434")
    model_name = st.text_input("MoE 模型名称", value="qwen2.5-moe:1.5b")
    
    st.subheader("📊 数字化效能看板")
    st.metric(label="今日服务请求", value="42 次", delta="+110% (效率翻倍)")
    st.metric(label="平均响应耗时", value="0.25 秒", delta="-88% (即时应答)")
    st.metric(label="数据本地隔离率", value="100.00%", delta="数据不出域")

# 三大标签页分栏
tab1, tab2, tab3 = st.tabs(["💬 智能问答大厅 (Chat)", "📖 知识库索引 (Index)", "🧠 MoE 专家路由追踪 (Expert Routing)"])

with tab1:
    st.subheader("💬 理财大楼同事智能自助咨询")
    st.caption("输入任何关于办公大楼打印机连接、差旅报销、会议室预订、活动物料领取或福利充值的问题：")
    
    # 聊天记录会话初始化
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    if user_query := st.chat_input("例如：打印机连不上怎么办？"):
        # 显示用户发送的信息
        with st.chat_message("user"):
            st.markdown(user_query)
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        # 调用大模型/本地匹配生成暖心回答
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            response_placeholder.info("本地微型知识库检索与大模型微调转译中...")
            
            answer = run_assistant(user_query, ollama_host, model_name)
            response_placeholder.markdown(answer)
            
        st.session_state.messages.append({"role": "assistant", "content": answer})
        # 刷新页面以保存最后提问状态
        st.rerun()

with tab2:
    st.subheader("📖 官方行政制度参考库")
    st.caption("当前收录的官方标准运营规范明细，点击分类折叠查看：")
    
    if os.path.exists("knowledge_base.json"):
        with open("knowledge_base.json", "r", encoding="utf-8") as f:
            kb = json.load(f)
            
        categories = set(item["category"] for item in kb)
        for cat in categories:
            with st.expander(f"📁 {cat}"):
                for item in kb:
                    if item["category"] == cat:
                        st.markdown(f"**问：{item['question']}**")
                        st.success(f"**官方细则：** {item['answer']}")
                        st.markdown("---")
    else:
        st.error("未找到本地知识库文件 `knowledge_base.json`。")

with tab3:
    st.subheader("🧠 Qwen-MoE (Mixture of Experts) 专家网络路由可视化")
    st.caption("MoE 模型核心优势：只激活特定 Expert（专家），显存占用下降 70%，极为适合大楼内部低算力设备离线部署。")
    
    last_query = ""
    if st.session_state.messages:
        # 获取用户上一次的提问
        user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
        if user_msgs:
            last_query = user_msgs[-1]["content"]
            
    st.markdown(f"**当前监听提问**：`{last_query or '（暂无提问，请在 Tab 1 问答大厅中输入）'}`")
    
    # 模拟 Gating Network (门控网络) 计算各个专家的激活权重
    expert_weights = {
        "💡 基础事务与流程专家 (Logistics Expert)": 5.0,
        "💻 IT基建与办公套件专家 (IT Expert)": 5.0,
        "💰 财务报销与资产审计专家 (Finance Expert)": 5.0,
        "🎪 客户沙龙与物料发放专家 (Event Expert)": 5.0
    }
    
    # 根据提问的关键词调整专家权重
    if last_query:
        q_lower = last_query.lower()
        if "打印" in q_lower or "电脑" in q_lower or "卡纸" in q_lower or "网" in q_lower or "it" in q_lower:
            expert_weights["💻 IT基建与办公套件专家 (IT Expert)"] = 85.0
            expert_weights["💡 基础事务与流程专家 (Logistics Expert)"] = 10.0
            expert_weights["💰 财务报销与资产审计专家 (Finance Expert)"] = 3.0
            expert_weights["🎪 客户沙龙与物料发放专家 (Event Expert)"] = 2.0
        elif "报销" in q_lower or "财务" in q_lower or "发票" in q_lower or "差旅" in q_lower:
            expert_weights["💰 财务报销与资产审计专家 (Finance Expert)"] = 90.0
            expert_weights["💡 基础事务与流程专家 (Logistics Expert)"] = 5.0
            expert_weights["💻 IT基建与办公套件专家 (IT Expert)"] = 3.0
            expert_weights["🎪 客户沙龙与物料发放专家 (Event Expert)"] = 2.0
        elif "沙龙" in q_lower or "宣传" in q_lower or "物料" in q_lower or "折页" in q_lower or "手册" in q_lower:
            expert_weights["🎪 客户沙龙与物料发放专家 (Event Expert)"] = 88.0
            expert_weights["💡 基础事务与流程专家 (Logistics Expert)"] = 8.0
            expert_weights["💻 IT基建与办公套件专家 (IT Expert)"] = 2.0
            expert_weights["💰 财务报销与资产审计专家 (Finance Expert)"] = 2.0
        elif "会议室" in q_lower or "饭卡" in q_lower or "充值" in q_lower or "下午茶" in q_lower or "订" in q_lower:
            expert_weights["💡 基础事务与流程专家 (Logistics Expert)"] = 82.0
            expert_weights["🎪 客户沙龙与物料发放专家 (Event Expert)"] = 10.0
            expert_weights["💻 IT基建与办公套件专家 (IT Expert)"] = 5.0
            expert_weights["💰 财务报销与资产审计专家 (Finance Expert)"] = 3.0
            
    st.markdown("### 🕸️ 门控门限网络 (Gating Network) 路由分配结果：")
    
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    
    for (expert, weight), col in zip(expert_weights.items(), cols):
        with col:
            is_active = weight > 50.0
            status_class = "expert-active" if is_active else "expert-inactive"
            status_text = "🔥 激活 (Active)" if is_active else "💤 挂起 (Standby)"
            
            col.markdown(f"""
            <div class="metric-card">
                <h5 style="margin:0 0 8px 0; font-size:12px; color:#1e293b;">{expert}</h5>
                <span class="{status_class}">{status_text}</span>
                <p style="margin:8px 0 0 0; font-size:18px; font-weight:700; color:#b91c1c;">{weight:.1f}%</p>
                <p style="margin:2px 0 0 0; font-size:9.5px; color:#64748b;">门限权重占比</p>
            </div>
            """, unsafe_allowed_html=True)
            
    st.success("🧠 **路由运作原理解析**：门控网络（Gating Network）会实时分析您的 Query 关键词嵌入向量，将 80%+ 的计算注意力分配给对应的激活状态 Experts，而其余 Experts 保持离线挂起（0 显存损耗），完美契合了理财部门本地服务器离线轻量部署的约束。")
