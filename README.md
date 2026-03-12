# Python 線上題庫評測平台

一個專為大一學生設計的 Python 程式練習平台。

## 功能特色

- 📝 **題目列表** - 依難度分類的練習題目
- 💻 **線上編輯器** - CodeMirror 語法高亮
- ⚡ **即時評測** - 送出程式碼立即顯示結果
- 💡 **解答提示** - 錯誤時顯示引導提示
- 🔒 **安全執行** - 限制危險操作，保護系統

## 技術架構

- **後端**: FastAPI (Python)
- **前端**: Vue 3 + CodeMirror (靜態 HTML)
- **資料儲存**: JSON 檔案

## 快速開始

### 1. 安裝依賴

```bash
cd backend
pip install -r requirements.txt
```

### 2. 啟動後端伺服器

```bash
cd backend
uvicorn main:app --reload --port 8000
```

後端伺服器會在 http://localhost:8000 啟動

### 3. 開啟前端

直接在瀏覽器中打開 `frontend/index.html`

或者使用 Python 啟動簡易伺服器：

```bash
cd frontend
python3 -m http.server 8080
```

然後訪問 http://localhost:8080

## API 文件

啟動後端後訪問：http://localhost:8000/docs

### API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | /api/problems | 取得題目列表 |
| GET | /api/problems/{id} | 取得題目詳情 |
| POST | /api/judge | 評測程式碼 |

### POST /api/judge Request

```json
{
  "problem_id": "001",
  "code": "print('Hello, World!')"
}
```

### Response

```json
{
  "correct": true,
  "problem_id": "001",
  "total_tests": 2,
  "passed_tests": 2,
  "results": [...],
  "hints": []
}
```

## 題目格式

題目存放在 `backend/data/problems/` 目錄，JSON 格式：

```json
{
  "id": "001",
  "title": "題目標題",
  "description": "題目描述",
  "input_example": "輸入範例",
  "output_example": "輸出範例",
  "test_cases": [
    {"input": "輸入\n", "output": "輸出"}
  ],
  "difficulty": "easy",
  "time_limit": 5,
  "hints": ["提示1", "提示2"]
}
```

## 安全性

- 禁止 import 危險模組 (os, sys, subprocess, socket 等)
- 限制執行時間 (預設 5 秒)
- 禁止檔案操作
- 禁止網路存取

## 預設題目

1. Hello World (easy)
2. 兩數相加 (easy)
3. 奇數或偶數 (easy)
4. 三數最大 (medium)
5. FizzBuzz (medium)

## 目錄結構

```
.
├── backend/
│   ├── main.py           # FastAPI 主程式
│   ├── requirements.txt  # Python 依賴
│   ├── api/
│   │   └── routes.py    # API 路由
│   ├── models/
│   │   └── __init__.py  # 資料模型
│   ├── judge/
│   │   ├── engine.py     # 評測引擎
│   │   └── loader.py    # 題目載入器
│   └── data/
│       └── problems/     # 題目 JSON
└── frontend/
    └── index.html       # 前端頁面
```
