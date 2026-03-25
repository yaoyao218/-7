# 測試案例資料庫架構 (TIKTOC)

一個基於 TIKTOC (Test Case-Informed Knowledge Tracing for Open-ended Coding) 研究論文的 AI 驅動測試案例學習平台。

## 系統特色

### 🎯 核心功能
- **答案比對評測**：設定標準答案，學生輸出與答案相同即為正確
- **相似案例偵測**：錯誤時自動找出輸出與哪個測試案例結果相似
- **AI 漸進式提示**：根據不同結果類型提供 3 層級的引導提示
- **學習進度追蹤**：記錄學習狀態，識別薄弱知識點

### 🤖 AI 提示系統
- **結果分析**：分析輸出類型（空輸出、錯誤值、正確、執行錯誤）
- **半對半錯引導**：拓寬學生認知，啟發思考邊界條件
- **根據相似案例**：比對錯誤輸出與測試案例，給予針對性提示
- **3 層漸進提示**：
  - Level 1: 基本檢查點
  - Level 2: 執行流程追蹤 + 優化方向
  - Level 3: 完整解答框架

### 🗄️ 資料庫架構 (7 Tables)
- `problems` - 題目資料（含標準答案）
- `test_cases` - 測試案例
- `tag_categories` - 標籤分類
- `test_case_tags` - 測試案例標籤
- `knowledge_components` - 知識點
- `kc_assignments` - 知識點分配
- `execution_logs` - 執行日誌

## 技術架構

- **後端**: FastAPI + SQLAlchemy + SQLite
- **前端**: Vanilla JS (Dark Theme)
- **評測引擎**: Python 程式碼安全執行

## 目錄結構

```
測試案例資料庫/
├── backend/
│   ├── main.py              # FastAPI 入口
│   ├── database.py          # SQLAlchemy 連接
│   ├── ai_hint.py           # AI 提示生成系統
│   ├── seed.py              # 資料庫初始化
│   ├── api/
│   │   └── routes.py        # API 路由
│   ├── models/
│   │   └── schema.py        # 資料庫模型
│   ├── judge/
│   │   └── engine.py        # 評測引擎
│   └── testcase.db          # SQLite 資料庫
├── frontend/
│   ├── index.html           # 主頁面
│   ├── app.js               # 前端邏輯
│   └── styles.css           # Dark Theme 樣式
├── 啟動平台.bat              # Windows 啟動腳本
└── 停止平台.bat              # Windows 停止腳本
```

## 快速開始

### Windows 啟動
```
雙擊 啟動平台.bat
```

### 手動啟動
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8000
```

訪問 http://localhost:8000

## API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | /api/problems | 題目列表 |
| GET | /api/problems/{id} | 題目詳情 |
| POST | /api/judge | 評測程式碼 |
| POST | /api/ai-hint | AI 提示生成 |
| GET | /api/dashboard | 學習儀表板 |

## 評測流程

1. **提交程式碼** → 執行並取得輸出
2. **答案比對** → 輸出與標準答案相同 → 正確
3. **相似案例偵測** → 輸出與某測試案例結果相同
4. **AI 提示生成** → 根據相似案例給予對應提示

## 資料庫範例 (Two Sum)

```python
# 標準答案
reference_answer: [0, 1]

# 測試案例
test_cases:
  - input: {nums: [2,7,11,15], target: 9}, expected: [0,1]
  - input: {nums: [3,2,4], target: 6}, expected: [1,2]
  - input: {nums: [], target: 5}, expected: []
  - ...
```

## AI 提示範例

### 正確答案
```
🎉 答案正確！
```

### 錯誤輸出（相似案例）
```
您的輸出：[0, 0]
正確答案：[0, 1]

您的輸出出現在這個測試案例：
  輸入：{'nums': [3, 3], 'target': 6}
  該輸入的正確輸出：[0, 1]

思考：
  • 為什麼這個輸入會輸出這個結果？
  • 這個結果和正確答案有什麼不同？
```

## 授權

MIT License
