import json
import os
import urllib.request
import urllib.error

# 定义本地匹配规则（当本地大模型不可达时的快速兜底）
def get_keyword_overlap(s1, s2):
    s1_words = set(s1.lower())
    s2_words = set(s2.lower())
    return len(s1_words.intersection(s2_words))

def retrieve_best_match(query, kb_path="knowledge_base.json"):
    if not os.path.exists(kb_path):
        return None
    with open(kb_path, "r", encoding="utf-8") as f:
        kb = json.load(f)
        
    best_match = None
    max_overlap = -1
    
    # 模糊查找重合字符最多的问题条目
    for item in kb:
        overlap = get_keyword_overlap(query, item["question"])
        if overlap > max_overlap:
            max_overlap = overlap
            best_match = item
            
    # 如果字符重合度太低，返回无匹配
    if max_overlap <= 2:
        return None
    return best_match

def ask_qwen_moe(query, context_info, host="http://localhost:11434", model="qwen2.5-moe:1.5b"):
    """
    通过 Ollama 联络本地运行的 Qwen-MoE 轻量混合专家模型进行安全转译。
    数据不出大楼局域网，在保障极低计算资源（MoE架构只激活部分Expert）下运行。
    """
    print(f"\n[本地 Qwen-MoE 计算中]：调用本地接口 {host}，激活模型 [{model}]...")
    
    system_prompt = """你是一位温暖体贴、专业高效的南海农商银行理财业务部行政助理助理。请结合给定的官方制度参考回答员工的提问。
要求：
1. 语言体面得体，能体现同事间的温暖关怀。
2. 严格遵循参考文档中的政策，不能编造不存在的内线电话或政策。
3. 说明该回答已通过本地离线 MoE 模型安全检索。"""

    user_input = f"【官方制度参考】：\n分类: {context_info['category']}\n问题: {context_info['question']}\n制度规定: {context_info['answer']}\n\n【员工当前提问】: {query}"
    
    url = f"{host}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
          {"role": "system", "content": system_prompt},
          {"role": "user", "content": user_input}
        ],
        "temperature": 0.3
    }
    
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    
    try:
        with urllib.request.urlopen(req, data=json.dumps(payload).encode('utf-8'), timeout=5) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            answer = res_data['choices'][0]['message']['content'].strip()
            return answer
    except Exception as e:
        # 本地离线仿真引擎返回（融入助理陈富华的人文关怀）
        print(f">> 无法连接本地 Qwen-MoE 接口 ({str(e)})。已自动降级为本地规则转译引擎响应...")
        
        fallback_answer = f"""🌸 您好！我是您的本地行政助手陈富华。
针对您问的“{query}”，行内官方制度规定如下：
👉 {context_info['answer']}

【温馨提示】：本回答由理财部本地大模型微型知识库离线检索输出，您的数据受行内局域网安全保护。若有其他疑问，欢迎直接来 3 楼行政办公室找我，或者拨打我的企业微信内线，祝您工作顺利！"""
        return fallback_answer

def run_assistant(query, host="http://localhost:11434", model="qwen2.5-moe:1.5b"):
    match = retrieve_best_match(query)
    if not match:
        return """🌸 您好！我是理财部行政助理陈富华。
很抱歉，我本地的微型制度库中暂时没有收录与您提问直接相关的制度信息。
你可以试着问我：“打印机怎么连？”、“差旅报销截止日期” 或 “图灵会议室怎么订？”。
如果有紧急诉求，可以直接到 3 楼行政办公室找我，我会第一时间为您解决！"""
        
    return ask_qwen_moe(query, match, host, model)

if __name__ == "__main__":
    q = "打印机卡纸了怎么办？"
    ans = run_assistant(q)
    print("\n提问:", q)
    print("回答:\n", ans)
