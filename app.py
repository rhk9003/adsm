import streamlit as st

# 設定頁面配置
st.set_page_config(
    page_title="廣告策略 Prompt 生成器",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義 CSS 優化介面
st.markdown("""
    <style>
    .stTextArea textarea {
        font-size: 14px;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# 標題區
st.title("🎯 廣告策略 Prompt 生成器")
st.markdown("針對競爭對手進行深度逆向工程，三步驟生成：**競品分析 → 差異比對 → 素材產出**")
st.markdown("---")

# 側邊欄：資料輸入區
with st.sidebar:
    st.header("1. 資料輸入 (Input Data)")
    st.info("在此貼上廣告檔案庫內容（文字、字幕、文案等）。系統會自動將其填入 Step 1 的 Prompt 中。")
    
    competitor_data = st.text_area(
        "競爭對手資料",
        height=400,
        placeholder="例如：\n競品A文案：「限時三天，買一送一...」\n競品B影片字幕：「想要肌膚透亮...」",
        help="貼上越詳細的資料，分析越精準"
    )
    
    st.caption(f"目前字數: {len(competitor_data)}")

# 主畫面：分頁切換
tab1, tab2, tab3 = st.tabs(["Step 1: 競品深度分析", "Step 2: 我方現況比對", "Step 3: 素材創意產出"])

# --- Step 1: 競品深度分析 ---
with tab1:
    st.subheader("Step 1: 競品素材戰略拆解")
    st.markdown("此指令用於**逆向工程**對手的切角、受眾與視覺策略。")
    
    # 處理資料填入
    input_content = competitor_data if competitor_data.strip() else "[在此貼上資料]"
    
    prompt1 = f"""# Role: 資深廣告策略顧問 (Strategic Ad Consultant)

# Goal
請針對我提供的【競爭對手廣告資料】進行深度逆向工程分析，產出一份《競品素材戰略拆解報告》，用以指導我方客戶（品牌主）未來的廣告素材製作方向。

# Input Data
以下貼的是廣告檔案庫的內容（可能包含文字、截圖、PDF、影片字幕等）：
{input_content}

# Analysis Framework (Must Follow)
請嚴格依照以下 markdown 結構輸出報告，並確保分析具有洞察力（Insightful），避免表面描述。務必引用原文句子佐證。

---

## 1. 切角分類 (Hooks & Angles)
請歸納對手最常使用的 3 種溝通切角，每個切角需包含：
- **切角類型**：
- **對應文案/句子**（引用原文）：
- **攻擊邏輯**（為什麼有效？打中了什麼心理？）：

---

## 2. 受眾推論 (Audience Profiling)
請逆向推導對手主要鎖定的人群，包含：
- **主要受眾**：
- **心理狀態**：
- **被打中的原因**：

---

## 3. 視覺與素材策略 (Visual Strategy)
請解析對手的畫面呈現方式：
- **視覺風格**：
- **關鍵視覺元素**：
- **設計意圖**：

---

## 4. 廣告結構解析 (Structure Breakdown)
請拆解有效廣告的敘事節奏：
- **開場 (The Hook)**：
- **中段 (The Body)**：
- **結尾 (The CTA)**：

---

## 5. 文案語氣風格分析 (Tone Analysis)
請拆解對手文案的語氣模型（3～4 行）：
- **語氣風格特徵**：
- **語氣背後策略意圖**：
- **為什麼這語氣適合其受眾？**：

---

## 6. 競品素材 Pattern Library（素材套路庫）
請統整 2～3 個對手經常使用的素材模板（Pattern），每個需包含：
- **Pattern 名稱**：
- **素材結構（如：案例 → 補助 → 限量 → CTA）**：
- **視覺配置重點**：
- **常見搭配語氣**：
- **適用情境（打誰？適合什麼狀態？）**：

---

## 7. 我方戰略指引 (Strategic Action Plan)

### 7-1. 推薦素材角度 (To Model)
請列出 2～3 個我方應借鑑的競品策略：
1）
2）
3）

---

### 7-2. 競品盲區與卡位機會 (The Gap)
指出對手沒做到、沒說好、或我們能做得更好的差異化突破：
- 

# Output Format
請以完整 markdown 報告輸出，不需重複我的指令，直接開始分析。"""

    st.code(prompt1, language="markdown")
    st.success("☝️ 點擊代碼區塊右上角的按鈕即可一鍵複製")

# --- Step 2: 我方現況比對 ---
with tab2:
    st.subheader("Step 2: 我方現況比對 (Gap Analysis)")
    st.warning("⚠️ 注意：發送此指令時，請記得附上您客戶的網頁連結或文案內容。")
    
    prompt2 = """請比對我的客戶的網頁連結與文案素材

按照前面的分析，我的客戶哪些有做到？哪些沒做到？哪裡可以做更好？"""

    st.code(prompt2, language="markdown")

# --- Step 3: 素材創意產出 ---
with tab3:
    st.subheader("Step 3: 創意素材產出")
    st.markdown("根據前兩步的分析，產出具體的 Canvas 格式素材建議。")
    
    prompt3 = """根據你的建議輸出給我四則廣告素材建議，格式呈現比照我給的附件，canvas呈現給我

包含

-廣告主訴求

-廣告素材文字

-主文案

-廣告標題"""

    st.code(prompt3, language="markdown")

# Footer
st.markdown("---")
st.markdown("© Strategic Ad Consultant Toolkit | Built with Streamlit")
