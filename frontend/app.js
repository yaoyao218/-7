const API_BASE = 'http://localhost:8000/api';

let currentPage = 'dashboard';
let userId = localStorage.getItem('userId') || generateUserId();
let currentProblem = null;
let aiHints = [];
let testResults = [];
let hintLevel = 1;
let currentHintResult = null;

function generateUserId() {
    const id = 'user_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('userId', id);
    return id;
}

async function api(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showToast('連線錯誤，請確認伺服器已啟動', 'error');
        throw error;
    }
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast') || createToast();
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    setTimeout(() => toast.classList.remove('show'), 4000);
}

function createToast() {
    const toast = document.createElement('div');
    toast.id = 'toast';
    document.body.appendChild(toast);
    return toast;
}

function getDifficultyText(diff) {
    const map = { easy: '簡單', medium: '中等', hard: '困難' };
    return map[diff] || diff;
}

function getStarterCode(problemName) {
    if (problemName === 'Two Sum') {
        return `def two_sum(nums: list[int], target: int) -> list[int]:
    # 使用 Hash Map 優化時間複雜度
    # 遍歷陣列，檢查 complement 是否存在
    pass
`;
    }
    return `# ${problemName || 'Solution'}\ndef solve():\n    pass\n`;
}

function renderDashboard() {
    return `
        <section class="problem-select container" style="padding-top: 48px;">
            <div class="problem-select-header">
                <h1>📊 儀表板</h1>
            </div>
            <div id="dashboard-content">
                <div class="loading">
                    <div class="spinner"></div>
                    載入中...
                </div>
            </div>
        </section>
    `;
}

function renderProblemList() {
    return `
        <section class="problem-select container" style="padding-top: 48px;">
            <div class="problem-select-header">
                <h1>📝 題目列表</h1>
            </div>
            <div class="problems-grid" id="problems-list">
                <div class="loading">
                    <div class="spinner"></div>
                    載入題目
                </div>
            </div>
        </section>
    `;
}

function renderPractice() {
    if (!currentProblem) {
        return renderProblemList();
    }
    
    return `
        <div class="practice-container">
            <!-- Left Panel: Problem & Hints -->
            <div class="practice-left">
                <button class="back-btn" onclick="backToList()">
                    ← 返回題目列表
                </button>
                
                <div class="problem-panel">
                    <div class="problem-panel-header">
                        <h2>${currentProblem.name}</h2>
                        <span class="difficulty ${currentProblem.difficulty}">${getDifficultyText(currentProblem.difficulty)}</span>
                    </div>
                    <p class="problem-description-text">${currentProblem.description}</p>
                    <div class="function-signature">${currentProblem.function_signature}</div>
                </div>
                
                <!-- AI Hint Panel -->
                <div class="hints-panel" id="ai-hint-panel">
                    <h4>🤖 AI 智能分析</h4>
                    <div id="result-breakdown" style="display: none; margin-bottom: 12px;"></div>
                    <div id="ai-hint-content">
                        <p style="color: var(--text-muted); font-size: 0.85rem;">
                            提交程式碼後，這裡會顯示 AI 分析結果和提示
                        </p>
                    </div>
                    <button class="btn btn-sm btn-secondary" id="more-hints-btn" style="display: none; margin-top: 12px; width: 100%;" onclick="requestMoreHints()">
                        💡 更多提示
                    </button>
                </div>
                
                <!-- Hidden Test Cases (for reference only) -->
                <div style="display: none;" id="hidden-testcases">
                    ${(currentProblem.test_cases || []).map((tc, i) => `
                        <div class="test-case-data" data-index="${i}" data-tags="${(tc.tags || []).join(',')}">
                            ${JSON.stringify(tc)}
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <!-- Right Panel: Editor -->
            <div class="practice-right">
                <div class="editor-panel">
                    <div class="editor-header">
                        <h3>💻 程式碼編輯器</h3>
                        <div class="editor-actions">
                            <button class="btn btn-secondary" onclick="resetCode()">🔄 重置</button>
                            <button class="btn btn-primary" onclick="submitCode()">🚀 提交評測</button>
                        </div>
                    </div>
                    <textarea id="code-editor" placeholder="在此輸入 Python 程式碼..." spellcheck="false">${getStarterCode(currentProblem.name)}</textarea>
                    <div class="results-summary" id="results-summary" style="display: none;">
                        <button class="btn btn-sm btn-success" onclick="nextProblem()" id="next-btn" style="display: none;">
                            下一題 →
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

async function loadDashboard() {
    try {
        const dashboard = await api(`/dashboard?user_id=${userId}`).catch(() => ({
            stats: {},
            weak_kcs: [],
            recommendations: []
        }));
        
        const problems = await api('/problems');
        
        const dashboardHtml = `
            <div style="margin-bottom: 32px;">
                <h2 style="margin-bottom: 20px; color: var(--text-muted);">📈 學習統計</h2>
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;">
                    <div class="problem-card" style="text-align: center;">
                        <div style="font-size: 2rem; color: var(--primary-light);">${dashboard.stats.total_problems || 0}</div>
                        <div style="color: var(--text-muted);">總題目</div>
                    </div>
                    <div class="problem-card" style="text-align: center;">
                        <div style="font-size: 2rem; color: var(--secondary);">${dashboard.stats.passed_problems || 0}</div>
                        <div style="color: var(--text-muted);">已完成</div>
                    </div>
                    <div class="problem-card" style="text-align: center;">
                        <div style="font-size: 2rem; color: var(--warning);">${dashboard.stats.attempted || 0}</div>
                        <div style="color: var(--text-muted);">已嘗試</div>
                    </div>
                    <div class="problem-card" style="text-align: center;">
                        <div style="font-size: 2rem; color: var(--text-light);">${dashboard.stats.success_rate || 0}%</div>
                        <div style="color: var(--text-muted);">通過率</div>
                    </div>
                </div>
            </div>
            
            <div style="margin-bottom: 32px;">
                <h2 style="margin-bottom: 20px; color: var(--text-muted);">⚠️ 薄弱環節</h2>
                ${dashboard.weak_kcs && dashboard.weak_kcs.length > 0 ? 
                    dashboard.weak_kcs.map(kc => `
                        <div class="problem-card" style="margin-bottom: 12px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <strong>${kc.name}</strong>
                                    <div style="color: var(--text-muted); font-size: 0.85rem;">${kc.description || ''}</div>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 1.5rem; color: ${kc.pass_rate > 50 ? 'var(--warning)' : 'var(--danger)'};">${kc.pass_rate}%</div>
                                </div>
                            </div>
                        </div>
                    `).join('') : 
                    '<p style="color: var(--text-muted);">尚無資料，多做題目後會顯示分析結果</p>'
                }
            </div>
            
            <div>
                <h2 style="margin-bottom: 20px; color: var(--text-muted);">📚 推薦題目</h2>
                <div class="problems-grid">
                    ${problems.map(p => `
                        <div class="problem-card" onclick="selectProblem(${p.id})">
                            <div class="problem-card-header">
                                <span class="problem-title">${p.title || p.name}</span>
                                <span class="difficulty ${p.difficulty}">${getDifficultyText(p.difficulty)}</span>
                            </div>
                            <p class="problem-description">${(p.description || '').substring(0, 100)}...</p>
                            <div class="problem-meta">
                                <span>📋 ${p.test_cases?.length || 0} 測試案例</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        document.getElementById('dashboard-content').innerHTML = dashboardHtml;
    } catch (error) {
        console.error('Load dashboard error:', error);
    }
}

async function loadProblemList() {
    try {
        const problems = await api('/problems');
        
        if (problems.length === 0) {
            document.getElementById('problems-list').innerHTML = `
                <div class="empty-state">
                    <div class="icon">📭</div>
                    <p>暫無題目</p>
                </div>
            `;
            return;
        }
        
        document.getElementById('problems-list').innerHTML = problems.map(p => `
            <div class="problem-card" onclick="selectProblem(${p.id})">
                <div class="problem-card-header">
                    <span class="problem-title">${p.title || p.name}</span>
                    <span class="difficulty ${p.difficulty}">${getDifficultyText(p.difficulty)}</span>
                </div>
                <p class="problem-description">
                    ${(p.description || '').substring(0, 120)}${(p.description || '').length > 120 ? '...' : ''}
                </p>
                <div class="problem-meta">
                    <span>📋 ${p.test_cases?.length || 0} 測試案例</span>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Load problems error:', error);
    }
}

async function selectProblem(problemId) {
    try {
        const problem = await api(`/problems/${problemId}`);
        currentProblem = problem;
        testResults = new Array(problem.test_cases?.length || 0).fill(null);
        aiHints = [];
        hintLevel = 1;
        currentHintResult = null;
        navigateTo('practice');
    } catch (error) {
        console.error('Load problem error:', error);
        showToast('載入題目失敗', 'error');
    }
}

async function submitCode() {
    if (!currentProblem) return;
    
    const code = document.getElementById('code-editor').value;
    if (!code.trim()) {
        showToast('請輸入程式碼', 'error');
        return;
    }
    
    hintLevel = 1;
    showToast('評測中...', 'success');
    
    try {
        const result = await api('/judge', {
            method: 'POST',
            body: JSON.stringify({
                problem_id: currentProblem.id,
                code: code
            })
        });
        
        testResults = result.results;
        
        const resultsSummary = document.getElementById('results-summary');
        resultsSummary.style.display = 'block';
        
        const nextBtn = document.getElementById('next-btn');
        
        if (result.correct) {
            showToast('🎉 恭喜！您已完成題目要求！', 'success');
            nextBtn.style.display = 'block';
            
            document.getElementById('ai-hint-content').innerHTML = `
                <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid var(--secondary); border-radius: 8px; padding: 16px; text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 8px;">🎉</div>
                    <div style="font-weight: 600; color: var(--secondary); margin-bottom: 8px;">完成題目要求！</div>
                    <p style="color: var(--text-light); font-size: 0.85rem;">
                        您已通過測試！<br>
                        您可以嘗試用不同的方法來解題，挑戰自己！
                    </p>
                </div>
            `;
            document.getElementById('more-hints-btn').style.display = 'none';
            document.getElementById('result-breakdown').style.display = 'none';
        } else {
            showToast('尚未通過測試，請繼續努力', 'error');
            nextBtn.style.display = 'none';
            
            const aiHintResult = await api('/ai-hint', {
                method: 'POST',
                body: JSON.stringify({
                    code: code,
                    test_results: result.results,
                    problem_name: currentProblem.name,
                    problem_id: currentProblem.id,
                    hint_level: hintLevel,
                    reference_answer: result.reference_answer,
                    similar_test_case: result.similar_test_case,
                    actual_output: result.actual_output
                })
            });
            
            currentHintResult = aiHintResult;
            displayAiHints(aiHintResult, 1);
        }
        
    } catch (error) {
        showToast('評測失敗', 'error');
    }
}

function displayAiHints(hintResult, failCount) {
    const container = document.getElementById('ai-hint-content');
    const breakdownDiv = document.getElementById('result-breakdown');
    const moreHintsBtn = document.getElementById('more-hints-btn');
    
    breakdownDiv.style.display = 'none';
    
    if (!hintResult.hints || hintResult.hints.length === 0) {
        container.innerHTML = `
            <div style="color: var(--text-muted); font-size: 0.85rem;">
                請檢查您的程式碼邏輯
            </div>
        `;
        moreHintsBtn.style.display = 'none';
        return;
    }
    
    let hintsHtml = `
        <div style="margin-bottom: 16px;">
            ${hintResult.your_output !== undefined ? `
                <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 12px; margin-bottom: 12px;">
                    <div style="font-weight: 600; color: var(--danger); margin-bottom: 8px;">您的輸出：${JSON.stringify(hintResult.your_output)}</div>
                    <div style="font-weight: 600; color: var(--secondary);">正確答案：${JSON.stringify(hintResult.correct_answer)}</div>
                </div>
            ` : ''}
            ${hintResult.diagnosis ? `
                <div style="font-size: 0.85rem; font-weight: 600; color: var(--primary-light); margin-bottom: 12px;">
                    ${hintResult.diagnosis}
                </div>
            ` : ''}
    `;
    
    hintResult.hints.forEach((hint, i) => {
        const hintClass = hint.includes('💡') || hint.includes('📋') ? 'ai-hint' : 'ai-hint-simple';
        hintsHtml += `
            <div class="${hintClass}" style="margin-bottom: 8px; font-size: 0.85rem; white-space: pre-line;">
                ${hint}
            </div>
        `;
    });
    
    if (hintResult.suggestion) {
        hintsHtml += `
            <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 8px; padding: 12px; margin-top: 12px;">
                <div style="font-weight: 600; color: var(--primary-light); margin-bottom: 4px;">💪 建議</div>
                <div style="color: var(--text-light); font-size: 0.85rem;">${hintResult.suggestion}</div>
            </div>
        `;
    }
    
    if (hintResult.code_patterns) {
        const patterns = hintResult.code_patterns;
        let patternInfo = '';
        
        if (patterns.uses_brute_force && !patterns.uses_hash_map) {
            patternInfo = '<span style="color: var(--warning);">🔄 檢測到暴力解法</span>';
        } else if (patterns.uses_hash_map) {
            patternInfo = '<span style="color: var(--secondary);">✓ 檢測到 Hash Map 思路</span>';
        }
        
        if (patternInfo) {
            hintsHtml += `
                <div style="margin-top: 12px; font-size: 0.8rem;">
                    ${patternInfo}
                </div>
            `;
        }
    }
    
    hintsHtml += '</div>';
    
    container.innerHTML = hintsHtml;
    
    if (hintResult.hint_level < hintResult.max_hint_level) {
        moreHintsBtn.style.display = 'block';
        moreHintsBtn.textContent = `💡 更多提示 (${hintResult.hint_level}/${hintResult.max_hint_level})`;
    } else {
        moreHintsBtn.style.display = 'none';
    }
}

async function requestMoreHints() {
    if (!currentProblem || !currentHintResult) return;
    
    const code = document.getElementById('code-editor').value;
    hintLevel = Math.min(hintLevel + 1, 3);
    
    try {
        const aiHintResult = await api('/ai-hint', {
            method: 'POST',
            body: JSON.stringify({
                code: code,
                test_results: testResults,
                problem_name: currentProblem.name,
                problem_id: currentProblem.id,
                hint_level: hintLevel,
                reference_answer: currentHintResult.correct_answer,
                similar_test_case: currentHintResult.similar_test_case,
                actual_output: currentHintResult.your_output
            })
        });
        
        currentHintResult = aiHintResult;
        displayAiHints(aiHintResult, 1);
    } catch (error) {
        showToast('取得提示失敗', 'error');
    }
}

function resetCode() {
    if (currentProblem) {
        document.getElementById('code-editor').value = getStarterCode(currentProblem.name);
        document.getElementById('ai-hint-content').innerHTML = `
            <p style="color: var(--text-muted); font-size: 0.85rem;">
                提交程式碼後，這裡會顯示 AI 分析結果和提示
            </p>
        `;
        hintLevel = 1;
        currentHintResult = null;
        document.getElementById('more-hints-btn').style.display = 'none';
        document.getElementById('result-breakdown').style.display = 'none';
    }
}

function backToList() {
    currentProblem = null;
    navigateTo('problems');
}

async function nextProblem() {
    try {
        const problems = await api('/problems');
        const currentIndex = problems.findIndex(p => p.id === currentProblem.id);
        if (currentIndex < problems.length - 1) {
            await selectProblem(problems[currentIndex + 1].id);
        } else {
            showToast('這是最後一題了！', 'success');
        }
    } catch (error) {
        console.error('Load next problem error:', error);
    }
}

async function navigateTo(page) {
    currentPage = page;
    
    document.querySelectorAll('.nav a').forEach(a => {
        a.classList.toggle('active', a.dataset.page === page);
    });
    
    const main = document.getElementById('main-content');
    
    switch (page) {
        case 'dashboard':
            main.innerHTML = renderDashboard();
            loadDashboard();
            break;
        case 'problems':
            main.innerHTML = renderProblemList();
            loadProblemList();
            break;
        case 'practice':
            if (!currentProblem) {
                try {
                    const problems = await api('/problems');
                    if (problems.length > 0) {
                        await selectProblem(problems[0].id);
                    } else {
                        main.innerHTML = renderProblemList();
                        loadProblemList();
                        showToast('尚無題目', 'error');
                    }
                } catch (error) {
                    main.innerHTML = renderProblemList();
                    loadProblemList();
                }
            } else {
                main.innerHTML = renderPractice();
            }
            break;
        default:
            main.innerHTML = renderDashboard();
            loadDashboard();
    }
    
    window.scrollTo(0, 0);
}

document.addEventListener('DOMContentLoaded', () => {
    navigateTo('dashboard');
});
