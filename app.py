import streamlit as st
import google.generativeai as genai
import tempfile
import os
import time
from pathlib import Path

# --- 頁面設定 ---
st.set_page_config(
    page_title="廣告策略 Gemini 3.0 生成器",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS 優化 ---
st.markdown("""
    <style>
    .stTextArea textarea { font-size: 14px; }
    .stButton button { width: 100%; border-radius: 8px; font-weight: bold; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    div[data-testid="stExpander"] div[role="button"] p { font-size: 1.1rem; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- 核心功能函式 ---

def configure_gemini(api_key):
    """設定 API Key"""
    if not api_key:
        st.error("❌ 請先在側邊欄輸入 Google Gemini API Key")
        return False
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"API Key 設定失敗: {e}")
        return False

def upload_to_gemini(uploaded_file):
    """
    將 Streamlit 上傳的檔案寫入暫存並上傳至 Gemini File API。
    支援多模態：PDF, 圖片, 影片, 音訊, CSV 等。
    """
    if uploaded_file is None:
        return None
    
    try:
        # 1. 寫入暫存檔 (因為 Gemini SDK 需要檔案路徑)
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        # 2. 上傳至 Google GenAI
        with st.spinner(f"正在上傳並處理檔案: {uploaded_file.name} ..."):
            gemini_file = genai.upload_file(path=tmp_path, display_name=uploaded_file.name)
            
            # 3. 檢查處理狀態 (特別是影片或大檔案需要等待)
            while gemini_file.state.name == "PROCESSING":
                time.sleep(2)
                gemini_file = genai.get_file(gemini_file.name)
            
            if gemini_file.state.name == "FAILED":
                st.error(f"檔案 {uploaded_file.name} 處理失敗。")
                return None
                
        # 4. 清理本地暫存
        os.remove(tmp_path)
        return gemini_file

    except Exception as e:
        st.error(f"上傳錯誤 ({uploaded_file.name}): {e}")
        return None

def generate_content_stream(model_name, prompt, files=[]):
    """呼叫 Gemini API 生成內容"""
    try:
        model = genai.GenerativeModel(model_name)
        
        # 組合 Prompt 與 檔案物件
        content_parts = [prompt]
        if files:
            content_parts.extend(files) # 將處理好的 Gemini 檔案物件加入
            
        with st.spinner(f"正在使用 {model_name} 模型進行深度運算中..."):
            response = model.generate_content(
                content_parts,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                )
            )
        return response.text
    except Exception as e:
        st.error(f"生成錯誤: {e}")
        st.error("常見原因：API Key 額度不足、模型名稱錯誤或輸入內容觸發安全過濾。")
        return None

# --- Session State 初始化 (用於跨步驟儲存資料) ---
if 'step1_result' not in st.session_state:
    st.session_state.step1_result = ""
if 'step2_result' not in st.session_state:
    st.session_state.step2_result = ""
if 'step3_result' not in st.session_state:
    st.session_state.step3_result = ""

# --- 側邊欄設定 ---
with st.sidebar:
    st.header("⚙️ 系統設定")
    
    # 1. API Key 輸入
    api_key = st.text_input("輸入 Gemini API Key", type="password", help="請輸入您的 Google AI Studio API Key")
    
    # 2. 模型優先順序選擇 (依照使用者要求)
    st.markdown("### 🧠 模型選擇")
    model_options = [
        "gemini-3-pro",
        "gemini-3-pro-preview",
        "gemini-2.5-pro"
    ]
    selected_model = st.selectbox("使用模型", model_options, index=0)
    
    st.markdown("---")
    st.info(f"當前優先使用: **{selected_model}**")
    
    if st.button("重置所有分析", type="secondary"):
        st.session_state.step1_result = ""
        st.session_state.step2_result = ""
        st.session_state.step3_result = ""
        st.rerun()

# --- 主標題 ---
st.title("🎯 廣告策略 Gemini 3.0 智能工作台")
st.markdown("### 競品分析 → 差異比對 → 格式化素材產出")
st.markdown("---")

# --- 分頁介面 ---
tab1, tab2, tab3 = st.tabs(["Step 1: 競品逆向工程", "Step 2: 我方現況比對", "Step 3: 格式化素材產出"])

# ==========================================
# Step 1: 競品深度分析
# ==========================================
with tab1:
    st.subheader("Step 1: 競品廣告庫分析")
    st.markdown("**目標**：上傳競爭對手廣告庫（PDF/圖片/影片/文案），產出戰略拆解報告。")
    
    # 輸入區
    col1, col2 = st.columns([1, 1])
    with col1:
        competitor_files = st.file_uploader(
            "上傳競品素材 (可多選: 圖/文/影/PDF)", 
            accept_multiple_files=True,
            type=['png', 'jpg', 'jpeg', 'pdf', 'mp4', 'txt', 'csv'],
            key="s1_files"
        )
    with col2:
        competitor_text = st.text_area("直接貼上競品文案/連結 (選填)", height=150, placeholder="若無檔案，可在此貼上文字資料...")

    if st.button("🚀 執行 Step 1 分析", type="primary", key="btn_s1"):
        if configure_gemini(api_key):
            # 準備檔案
            gemini_files_s1 = []
            if competitor_files:
                for f in competitor_files:
                    g_file = upload_to_gemini(f)
                    if g_file: gemini_files_s1.append(g_file)
            
            # 準備 Prompt
            prompt_s1 = f"""# Role: 資深廣告策略顧問
請針對我提供的【競爭對手廣告資料】(包含上傳的檔案與下方文字)進行深度逆向工程分析。

# 補充文字資料：
{competitor_text}

# 任務：產出《競品素材戰略拆解報告》
請嚴格依照以下 Markdown 架構分析：
1. **切角分類 (Hooks & Angles)**：歸納 3 種最強切角，並分析其攻擊邏輯。
2. **受眾推論 (Audience Profiling)**：逆向推導其鎖定的受眾心理狀態。
3. **視覺與素材策略 (Visual Strategy)**：解析畫面風格、配色與元素。
4. **文案語氣 (Tone & Manner)**：分析其溝通語氣與策略意圖。
5. **素材套路庫 (Pattern Library)**：總結可被複製的素材結構模板。
6. **我方戰略機會 (Strategic Gap)**：初步指出對手的盲區。

請給出詳盡、專業的分析報告。
"""
            result = generate_content_stream(selected_model, prompt_s1, gemini_files_s1)
            if result:
                st.session_state.step1_result = result
                st.success("Step 1 分析完成！")

    # 顯示結果與下載
    if st.session_state.step1_result:
        st.markdown("---")
        st.markdown("### 📝 Step 1 分析結果")
        st.markdown(st.session_state.step1_result)
        st.download_button(
            label="📥 下載 Step 1 報告 (.md)",
            data=st.session_state.step1_result,
            file_name="Step1_Competitor_Analysis.md",
            mime="text/markdown"
        )

# ==========================================
# Step 2: 我方現況比對
# ==========================================
with tab2:
    st.subheader("Step 2: 我方現有素材比對")
    
    if not st.session_state.step1_result:
        st.warning("⚠️ 請先完成 Step 1，此步驟需要依賴 Step 1 的分析結果。")
    else:
        st.markdown("**目標**：基於 Step 1 的分析，檢視我方素材的缺口與機會點。")
        
        # 輸入區
        col1, col2 = st.columns([1, 1])
        with col1:
            our_files = st.file_uploader(
                "上傳我方現有素材 (可多選)", 
                accept_multiple_files=True,
                type=['png', 'jpg', 'jpeg', 'pdf', 'mp4', 'txt', 'csv'],
                key="s2_files"
            )
        with col2:
            our_text = st.text_area("補充我方資訊 (產品特點/連結)", height=150)

        if st.button("🚀 執行 Step 2 差異分析", type="primary", key="btn_s2"):
            if configure_gemini(api_key):
                # 準備檔案
                gemini_files_s2 = []
                if our_files:
                    for f in our_files:
                        g_file = upload_to_gemini(f)
                        if g_file: gemini_files_s2.append(g_file)
                
                # 準備 Prompt (串接 Step 1)
                prompt_s2 = f"""# Context: 競品分析背景
這是我們剛剛針對競爭對手做出的分析結果：
{st.session_state.step1_result}

# Task: 差異化分析 (Gap Analysis)
請參考上述分析，並審視我現在上傳的【我方現有素材】(檔案) 以及下方補充資訊：
{our_text}

請進行比對並產出報告：
1. **現況盤點**：我們目前的素材，命中了哪些競品也使用的有效切角？
2. **盲區偵測 (The Gap)**：競品有做，但我們完全沒做到的部分是什麼？
3. **優化建議**：針對我們的現有素材，具體如何修改才能贏過競品？
4. **差異化突圍**：我們有哪些競品沒有的優勢可以放大？

請直接輸出 Markdown 報告。
"""
                result = generate_content_stream(selected_model, prompt_s2, gemini_files_s2)
                if result:
                    st.session_state.step2_result = result
                    st.success("Step 2 比對完成！")

        # 顯示結果與下載
        if st.session_state.step2_result:
            st.markdown("---")
            st.markdown("### 📝 Step 2 分析結果")
            st.markdown(st.session_state.step2_result)
            st.download_button(
                label="📥 下載 Step 2 報告 (.md)",
                data=st.session_state.step2_result,
                file_name="Step2_Gap_Analysis.md",
                mime="text/markdown"
            )

# ==========================================
# Step 3: 格式化素材產出
# ==========================================
with tab3:
    st.subheader("Step 3: 最終素材產出")
    
    if not st.session_state.step2_result:
        st.warning("⚠️ 請先完成 Step 1 與 Step 2。")
    else:
        st.markdown("**目標**：根據分析建議，產出實際可用的文案與素材架構。")
        st.info("💡 如果您有特定的格式要求（如 Excel 表格結構、特定的 Canvas 格式），請上傳範例文件。")
        
        # 範例文件上傳 (非必要)
        example_file = st.file_uploader(
            "上傳範例文件 (選填：僅參考格式)", 
            type=['pdf', 'jpg', 'png', 'txt', 'md', 'csv', 'xlsx'],
            key="s3_example"
        )
        
        additional_req = st.text_input("額外要求 (例如：語氣要更活潑、要產出 5 組)", value="產出 4 組素材建議")

        if st.button("🚀 生成最終素材", type="primary", key="btn_s3"):
            if configure_gemini(api_key):
                # 準備檔案 (範例文件)
                gemini_files_s3 = []
                format_instruction = "請使用標準的 Markdown 表格格式呈現結果。"
                
                if example_file:
                    g_file = upload_to_gemini(example_file)
                    if g_file:
                        gemini_files_s3.append(g_file)
                        format_instruction = """
                        🚨 **格式嚴格要求**：
                        請忽略附件檔案中的「內容」，但必須嚴格模仿附件檔案的「格式排版」與「欄位架構」。
                        如果是表格，請畫出一樣的表格；如果是區塊，請使用一樣的區塊結構。
                        """
                
                # 準備 Prompt (串接前兩步)
                prompt_s3 = f"""# Context
Step 1 競品分析結論：
{st.session_state.step1_result}

Step 2 我方差異分析：
{st.session_state.step2_result}

# Task: 創意素材產出
根據上述策略脈絡，{additional_req}。

# Format Requirement
{format_instruction}

# Content Requirements (每組素材須包含)
1. **廣告主訴求** (Key Message)
2. **廣告素材文字** (Visual Text / Copy on Image)
3. **主文案** (Caption / Body Copy)
4. **廣告標題** (Headline)

請開始生成：
"""
                result = generate_content_stream(selected_model, prompt_s3, gemini_files_s3)
                if result:
                    st.session_state.step3_result = result
                    st.success("Step 3 素材生成完成！")

        # 顯示結果與下載
        if st.session_state.step3_result:
            st.markdown("---")
            st.markdown("### 🎨 Step 3 素材建議")
            st.markdown(st.session_state.step3_result)
            st.download_button(
                label="📥 下載最終素材檔案 (.md)",
                data=st.session_state.step3_result,
                file_name="Step3_Creative_Output.md",
                mime="text/markdown"
            )

# Footer
st.markdown("---")
st.caption(f"Powered by Google {selected_model} | Strategic Ad Toolkit")
