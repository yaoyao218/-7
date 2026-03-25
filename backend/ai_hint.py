import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from typing import Dict, Any, List

def analyze_code_patterns(code: str, problem_name: str = "") -> Dict[str, Any]:
    """分析學生代碼中的模式"""
    
    code_lower = code.lower()
    
    patterns = {
        "uses_brute_force": False,
        "uses_hash_map": False,
        "handles_duplicates": False,
        "handles_negatives": False,
        "handles_edge_cases": False,
        "missing_return": False,
        "incorrect_loop_range": False,
        "off_by_one": False,
        "empty_function": False
    }
    
    if "for i in range(len" in code_lower and "for j in range" in code_lower:
        patterns["uses_brute_force"] = True
    
    if "hashmap" in code_lower or "dict" in code_lower or "{}" in code:
        patterns["uses_hash_map"] = True
    
    if "in hashmap" in code_lower or "hashmap.get" in code_lower:
        patterns["handles_duplicates"] = True
    
    if "target - num" in code_lower or "complement" in code_lower:
        patterns["uses_hash_map"] = True
    
    if "if num < 0" in code_lower or "negative" in code_lower:
        patterns["handles_negatives"] = True
    
    if "if len(nums) == 0" in code_lower or "if not nums" in code_lower:
        patterns["handles_edge_cases"] = True
    
    if code.strip().endswith("pass") or (code.count("return") == 0 and "print" not in code_lower):
        patterns["missing_return"] = True
    
    if "range(i+1" in code_lower or "range(i," in code_lower:
        patterns["incorrect_loop_range"] = True
    
    if "range(len(" in code_lower and "i+1" not in code_lower:
        patterns["off_by_one"] = True
    
    if code.count("pass") == 1 and "def " in code:
        patterns["empty_function"] = True
    
    return patterns

def analyze_test_result_type(test_result: Dict[str, Any]) -> Dict[str, Any]:
    """分析單一測試結果的類型"""
    
    actual = str(test_result.get("actual_output", "")).strip()
    expected = test_result.get("expected_output")
    passed = test_result.get("passed", False)
    error = test_result.get("error", "")
    
    result_type = "unknown"
    description = ""
    
    if passed:
        result_type = "correct"
        description = "✅ 輸出正確"
    elif error and "Time Limit" in error:
        result_type = "timeout"
        description = "⏱️ 執行逾時"
    elif error and ("Error" in error or "error" in error.lower()):
        result_type = "runtime_error"
        description = f"❌ 執行錯誤"
    elif actual == "" or actual == "None" or actual == "null":
        result_type = "empty_output"
        description = "⚠️ 沒有輸出"
    elif actual == "[]":
        result_type = "empty_array"
        description = "⚠️ 輸出空陣列"
    else:
        try:
            actual_list = eval(actual) if actual else []
            expected_list = expected if isinstance(expected, list) else []
            if isinstance(expected, list):
                if len(actual_list) != len(expected_list):
                    result_type = "wrong_length"
                    description = f"🔢 長度錯誤 (預期{len(expected_list)}, 實際{len(actual_list)})"
                else:
                    result_type = "wrong_value"
                    description = "🔢 輸出值錯誤"
            else:
                result_type = "wrong_value"
                description = "🔢 輸出值錯誤"
        except:
            result_type = "wrong_format"
            description = "📝 格式錯誤"
    
    return {"type": result_type, "description": description, "actual": actual}

def generate_progressive_hint(
    code: str, 
    test_results: List[Dict], 
    problem_name: str = "",
    hint_level: int = 1
) -> Dict[str, Any]:
    """根據不同的測試結果類型生成漸進式提示"""
    
    patterns = analyze_code_patterns(code, problem_name)
    
    results_analysis = [analyze_test_result_type(r) for r in test_results]
    
    correct_count = sum(1 for r in results_analysis if r["type"] == "correct")
    empty_outputs = [r for r in results_analysis if r["type"] == "empty_output"]
    wrong_values = [r for r in results_analysis if r["type"] in ["wrong_value", "wrong_length", "wrong_format"]]
    empty_arrays = [r for r in results_analysis if r["type"] == "empty_array"]
    errors = [r for r in results_analysis if r["type"] in ["timeout", "runtime_error"]]
    
    total_count = len(test_results)
    failed_count = total_count - correct_count
    
    hints = []
    diagnosis = ""
    suggestion = ""
    
    # 根據不同的結果組合給予不同的引導
    if correct_count == total_count:
        return {
            "status": "success",
            "diagnosis": "🎉 完美通關！",
            "message": "太棒了！您的解答通過了所有測試！",
            "hints": [],
            "passed_count": correct_count,
            "total_count": total_count,
            "all_passed": True
        }
    
    # 情況 1: 完全沒有輸出 (空字串)
    if len(empty_outputs) == failed_count:
        diagnosis = "🔴 嚴重問題：函式完全沒有回傳任何值"
        
        if hint_level == 1:
            hints.append("📋 您的函式沒有回傳任何值")
            hints.append("   請檢查以下問題：")
            hints.append("   1. 函式是否有 return 語句？")
            hints.append("   2. return 語句在對的位置嗎？")
            hints.append("")
            hints.append("💡 提示：")
            hints.append("   - 找到答案時應該 return [i, j]")
            hints.append("   - 沒找到時應該 return []")
            
        elif hint_level == 2:
            hints.append("📋 讓我們追蹤執行流程：")
            hints.append("   以 nums=[2,7,11,15], target=9 為例：")
            hints.append("   - i=0, j=1: 2+7=9 ✓ 找到！")
            hints.append("   - 這時候應該執行 return [0,1]")
            hints.append("")
            hints.append("💡 檢查：")
            hints.append("   if nums[i] + nums[j] == target:")
            hints.append("       return [i, j]  ← 這行有執行到嗎？")
            
        elif hint_level >= 3:
            hints.append("📋 參考程式碼框架：")
            hints.append("   def two_sum(nums, target):")
            hints.append("       for i in range(len(nums)):")
            hints.append("           for j in range(i+1, len(nums)):")
            hints.append("               if nums[i] + nums[j] == target:")
            hints.append("                   return [i, j]  # 找到就回傳")
            hints.append("       return []  # 沒找到回傳空陣列")
    
    # 情況 2: 有輸出空陣列
    elif len(empty_arrays) > 0 and len(wrong_values) > 0:
        diagnosis = "🟡 部分正確：有些情況輸出空陣列，有些輸出錯誤"
        
        if hint_level == 1:
            hints.append(f"📋 結果分析：")
            hints.append(f"   ✅ 正確: {correct_count} 個")
            hints.append(f"   ⚠️ 空陣列: {len(empty_arrays)} 個")
            hints.append(f"   ❌ 錯誤: {len(wrong_values)} 個")
            hints.append("")
            hints.append("💡 請檢查：")
            hints.append("   - 什麼情況會導致輸出空陣列？")
            hints.append("   - 迴圈是否執行到正確的位置？")
            
        elif hint_level == 2:
            hints.append("📋 邏輯檢查：")
            if patterns["uses_brute_force"]:
                hints.append("   暴力解法應該能找到答案")
                hints.append("   請檢查：")
                hints.append("   - 迴圈範圍是否正確？")
                hints.append("   - 判斷條件是否正確？")
            else:
                hints.append("   請確認您的演算法邏輯")
                hints.append("   手工追蹤幾個範例")
                
        elif hint_level >= 3:
            hints.append("📋 請確認：")
            hints.append("   1. 迴圈有正確遍歷所有組合")
            hints.append("   2. 找到時有正確 return")
            hints.append("   3. 迴圈結束後有 return []")
    
    # 情況 3: 半對半錯 - 有部分正確、部分錯誤
    elif correct_count > 0 and correct_count < total_count:
        pass_rate = correct_count / total_count * 100
        
        if pass_rate >= 50:
            diagnosis = f"🌟 不錯！您通過了 {pass_rate:.0f}% 的測試"
        else:
            diagnosis = f"📚 部分正確 - 通過率 {pass_rate:.0f}%"
        
        if hint_level == 1:
            hints.append("📋 結果分析：")
            hints.append(f"   ✅ 通過: {correct_count} 個 ({pass_rate:.0f}%)")
            hints.append(f"   ❌ 失敗: {failed_count} 個")
            hints.append("")
            hints.append("💡 思考方向：")
            hints.append("   1. 通過的測試 vs 失敗的測試有什麼不同？")
            hints.append("   2. 失敗的測試隱藏了什麼边界條件？")
            hints.append("   3. 您的演算法對哪些情況有效？對哪些無效？")
            hints.append("")
            hints.append("🔍 拓寬認知：")
            hints.append("   • 想想「唯一解」vs 「多解」的情況")
            hints.append("   • 想想「有負數」vs 「全正數」的情況")
            hints.append("   • 想想「有重複數字」vs 「無重複」的情況")
            
        elif hint_level == 2:
            hints.append("📋 深入分析：")
            hints.append("   成功案例教會您：")
            hints.append("   → 您的核心邏輯是正確的")
            hints.append("")
            hints.append("   失敗案例告訴您：")
            hints.append("   → 有些邊界情況還沒考慮到")
            hints.append("")
            hints.append("💡 建議：")
            hints.append("   • 列出所有通過的測試輸入")
            hints.append("   • 列出所有失敗的測試輸入")
            hints.append("   • 比較兩者的差異，找出規律")
            
            if patterns["uses_brute_force"]:
                hints.append("")
                hints.append("🔧 暴力解優化方向：")
                hints.append("   • 檢查是否有重複計算？")
                hints.append("   • 能否用空間換取時間？")
            elif patterns["uses_hash_map"]:
                hints.append("")
                hints.append("🔧 Hash Map 檢查清單：")
                hints.append("   • 是否每次都正確檢查 complement？")
                hints.append("   • 存入順序和取出順序正確嗎？")
                
        elif hint_level >= 3:
            hints.append("📋 思維拓展：")
            hints.append("   1. 一題多解：")
            hints.append("      • 暴力解：O(n²) - 兩層迴圈")
            hints.append("      • Hash Map：O(n) - 一次遍歷")
            hints.append("      • 排序+雙指針：O(n log n)")
            hints.append("")
            hints.append("   2. 边界條件思考：")
            hints.append("      • 陣列長度為 0、1 的情況")
            hints.append("      • 有負數或 0 的情況")
            hints.append("      • 有重複數字的情況")
            hints.append("      • 無解的情況")
            hints.append("")
            hints.append("   3. 調試技巧：")
            hints.append("      • 用通過的測試理解邏輯")
            hints.append("      • 用失敗的測試找出漏洞")
    
    # 情況 4: 只有空輸出和空陣列（沒有 wrong_values）
    elif len(empty_outputs) > 0 and len(empty_arrays) > 0 and len(wrong_values) == 0:
        diagnosis = "🟡 問題：函式沒有正確回傳結果"
        
        if hint_level == 1:
            hints.append("📋 結果分析：")
            hints.append(f"   ✅ 正確: {correct_count} 個")
            hints.append(f"   ⚠️ 無輸出: {len(empty_outputs)} 個")
            hints.append(f"   📭 空陣列: {len(empty_arrays)} 個")
            hints.append("")
            hints.append("💡 請檢查：")
            hints.append("   - 函式是否有 return 語句？")
            hints.append("   - 找到答案時是否正確回傳？")
            hints.append("   - 迴圈是否遍歷到正確位置？")
            
        elif hint_level == 2:
            hints.append("📋 追蹤執行流程：")
            hints.append("   以 nums=[2,7,11,15], target=9 為例：")
            hints.append("   - 遍歷每個元素，檢查 complement 是否存在")
            hints.append("   - 找到時：return [索引1, 索引2]")
            hints.append("   - 沒找到：return []")
            hints.append("")
            hints.append("💡 檢查清單：")
            hints.append("   □ 迴圈內有 return [i, j] 語句")
            hints.append("   □ 迴圈外有 return [] 語句")
            
        elif hint_level >= 3:
            hints.append("📋 參考框架：")
            hints.append("   for i in range(len(nums)):")
            hints.append("       for j in range(i+1, len(nums)):")
            hints.append("           if nums[i] + nums[j] == target:")
            hints.append("               return [i, j]")
            hints.append("   return []")
    
    # 情況 5: 有輸出但錯誤（全錯）
    elif len(wrong_values) > 0 and correct_count == 0:
        diagnosis = "🟠 邏輯問題：輸出值不正確"
        
        if hint_level == 1:
            hints.append(f"📋 結果分析：")
            hints.append(f"   ✅ 正確: {correct_count} 個")
            hints.append(f"   ❌ 錯誤: {len(wrong_values)} 個")
            hints.append("")
            
            if patterns["uses_brute_force"]:
                hints.append("💡 您使用暴力解法，邏輯應該正確")
                hints.append("   請檢查：")
                hints.append("   - 迴圈範圍 (i+1, len)")
                hints.append("   - return 的時機")
            elif patterns["uses_hash_map"]:
                hints.append("💡 您使用 Hash Map，需要注意：")
                hints.append("   - 存入和取出順序")
                hints.append("   - 檢查和存入的順序")
            else:
                hints.append("💡 請檢查您的演算法邏輯")
                
        elif hint_level == 2:
            hints.append("📋 以錯誤案例追蹤：")
            hints.append("   假設 nums=[1,2,2,3], target=4")
            hints.append("   暴力解法應該找到 [1,2] 或 [0,3]")
            hints.append("")
            hints.append("💡 檢查：")
            hints.append("   - i=0, j=1: 1+2=3 ≠ 4")
            hints.append("   - i=0, j=2: 1+2=3 ≠ 4")
            hints.append("   - i=0, j=3: 1+3=4 ✓ 應該 return [0,3]")
            
        elif hint_level >= 3:
            hints.append("📋 常見錯誤：")
            hints.append("   1. 迴圈範圍錯誤")
            hints.append("   2. return 在錯誤位置")
            hints.append("   3. 索引計算錯誤")
    
    # 情況 6: 部分正確 + 部分錯誤
    elif len(wrong_values) > 0 and correct_count > 0:
        pass_rate = correct_count / total_count * 100
        
        if pass_rate >= 50:
            diagnosis = f"🌟 不錯！您通過了 {pass_rate:.0f}% 的測試"
        else:
            diagnosis = f"📚 部分正確 - 通過率 {pass_rate:.0f}%"
        
        if hint_level == 1:
            hints.append("📋 結果分析：")
            hints.append(f"   ✅ 通過: {correct_count} 個 ({pass_rate:.0f}%)")
            hints.append(f"   ❌ 失敗: {failed_count} 個")
            hints.append("")
            hints.append("💡 思考方向：")
            hints.append("   1. 通過的測試 vs 失敗的測試有什麼不同？")
            hints.append("   2. 失敗的測試隱藏了什麼边界條件？")
            hints.append("   3. 您的演算法對哪些情況有效？對哪些無效？")
            hints.append("")
            hints.append("🔍 拓寬認知：")
            hints.append("   • 想想「唯一解」vs 「多解」的情況")
            hints.append("   • 想想「有負數」vs 「全正數」的情況")
            hints.append("   • 想想「有重複數字」vs 「無重複」的情況")
            
        elif hint_level == 2:
            hints.append("📋 深入分析：")
            hints.append("   成功案例教會您：")
            hints.append("   → 您的核心邏輯是正確的")
            hints.append("")
            hints.append("   失敗案例告訴您：")
            hints.append("   → 有些邊界情況還沒考慮到")
            hints.append("")
            hints.append("💡 建議：")
            hints.append("   • 列出所有通過的測試輸入")
            hints.append("   • 列出所有失敗的測試輸入")
            hints.append("   • 比較兩者的差異，找出規律")
            
            if patterns["uses_brute_force"]:
                hints.append("")
                hints.append("🔧 暴力解優化方向：")
                hints.append("   • 檢查是否有重複計算？")
                hints.append("   • 能否用空間換取時間？")
            elif patterns["uses_hash_map"]:
                hints.append("")
                hints.append("🔧 Hash Map 檢查清單：")
                hints.append("   • 是否每次都正確檢查 complement？")
                hints.append("   • 存入順序和取出順序正確嗎？")
                
        elif hint_level >= 3:
            hints.append("📋 思維拓展：")
            hints.append("   1. 一題多解：")
            hints.append("      • 暴力解：O(n²) - 兩層迴圈")
            hints.append("      • Hash Map：O(n) - 一次遍歷")
            hints.append("      • 排序+雙指針：O(n log n)")
            hints.append("")
            hints.append("   2. 边界條件思考：")
            hints.append("      • 陣列長度為 0、1 的情況")
            hints.append("      • 有負數或 0 的情況")
            hints.append("      • 有重複數字的情況")
            hints.append("      • 無解的情況")
            hints.append("")
            hints.append("   3. 調試技巧：")
            hints.append("      • 用通過的測試理解邏輯")
            hints.append("      • 用失敗的測試找出漏洞")
    
    # 情況 7: 執行錯誤
    elif len(errors) > 0:
        diagnosis = "🔴 執行錯誤：程式碼有語法或執行問題"
        
        if hint_level >= 1:
            hints.append("📋 您的程式碼有錯誤：")
            hints.append("   請檢查：")
            hints.append("   - 語法是否正確？")
            hints.append("   - 是否有未定義的變數？")
            hints.append("   - 索引是否越界？")
    
    # 額外建議
    if hint_level >= 2:
        if patterns["uses_brute_force"] and not patterns["uses_hash_map"]:
            suggestion = "💡 暴力解可以優化：用 Hash Map 可達 O(n)"
        elif patterns["uses_hash_map"]:
            suggestion = "💡 Hash Map 方向正確，檢查實作細節"
    
    return {
        "status": "needs_help",
        "diagnosis": diagnosis,
        "hints": hints,
        "suggestion": suggestion,
        "passed_count": correct_count,
        "failed_count": failed_count,
        "total_count": total_count,
        "result_breakdown": {
            "correct": correct_count,
            "empty_output": len(empty_outputs),
            "wrong_value": len(wrong_values),
            "empty_array": len(empty_arrays),
            "errors": len(errors)
        },
        "code_patterns": patterns,
        "hint_level": hint_level
    }

def generate_ai_hint(code: str, test_results: list, problem_name: str = "") -> Dict[str, Any]:
    """生成 AI 提示（向後兼容）"""
    return generate_progressive_hint(code, test_results, problem_name, hint_level=1)

def generate_problem_hint(problem_name: str, difficulty: str = "medium") -> Dict[str, Any]:
    """為特定題目生成通用提示"""
    
    hints_by_problem = {
        "Two Sum": [
            "📖 解題思路：",
            "1. 暴力解法：兩層迴圈 O(n²)",
            "2. Hash Map 解法：一次迴圈 O(n)",
            "",
            "💡 Hash Map 技巧：",
            "• 遍歷 nums[i]",
            "• 找 target-nums[i] 是否已存在",
            "• 存在則回傳 [已存索引, i]",
            "• 不存在則存入 {nums[i]: i}"
        ]
    }
    
    default_hints = ["📖 理解問題 → 找出規律 → 設計演算法 → 實現測試"]
    
    return {"problem": problem_name, "hints": hints_by_problem.get(problem_name, default_hints)}

if __name__ == "__main__":
    test_code = "def two_sum(nums, target):\n    pass"
    test_results = [
        {"passed": False, "actual_output": "", "expected_output": [0, 1]},
        {"passed": False, "actual_output": "[]", "expected_output": [1, 2]},
    ]
    
    result = generate_progressive_hint(test_code, test_results, "Two Sum", hint_level=1)
    print("=== Level 1 ===")
    print(result["diagnosis"])
    print(result["hints"])
    
    result2 = generate_progressive_hint(test_code, test_results, "Two Sum", hint_level=2)
    print("\n=== Level 2 ===")
    print(result2["hints"])

def generate_answer_based_hint(
    code: str,
    actual_output: Any,
    correct_answer: Any,
    similar_test_case: Dict = None,
    problem_name: str = "",
    hint_level: int = 1
) -> Dict[str, Any]:
    """根據答案比對結果生成提示"""
    
    patterns = analyze_code_patterns(code, problem_name)
    hints = []
    diagnosis = ""
    
    if actual_output == correct_answer:
        return {
            "status": "success",
            "diagnosis": "🎉 答案正確！",
            "hints": [],
            "suggestion": "太棒了！"
        }
    
    if similar_test_case:
        sim_input = similar_test_case.get("input", {})
        sim_output = similar_test_case.get("expected_output", [])
        diagnosis = "🔍 您的輸出與某個測試案例結果相似"
        
        if hint_level == 1:
            hints.append("📋 分析結果：")
            hints.append(f"   您的輸出：{actual_output}")
            hints.append(f"   正確答案：{correct_answer}")
            hints.append("")
            hints.append("💡 您的輸出出現在這個測試案例：")
            hints.append(f"   輸入：{sim_input}")
            hints.append(f"   該輸入的正確輸出：{sim_output}")
            hints.append("")
            hints.append("🔍 思考：")
            hints.append("   • 為什麼這個輸入會輸出這個結果？")
            hints.append("   • 這個結果和正確答案有什麼不同？")
            hints.append("   • 您的演算法對這個輸入的處理邏輯是什麼？")
            
        elif hint_level == 2:
            hints.append("📋 深入分析：")
            hints.append(f"   您的輸出與測試案例 {sim_input} 的結果相同")
            hints.append(f"   該情況下的正確輸出應該是：{sim_output}")
            hints.append("")
            hints.append("💡 問題所在：")
            hints.append("   • 您的演算法可能只考慮了部分情況")
            hints.append("   • 正確答案考慮了更全面的情况")
            hints.append("")
            hints.append("🔧 建議：")
            hints.append("   • 檢查您的迴圈是否遍歷所有可能性")
            hints.append("   • 確認判斷條件是否完整")
            if patterns["uses_brute_force"]:
                hints.append("   • 暴力解應該能處理，檢查索引計算")
            if patterns["uses_hash_map"]:
                hints.append("   • 檢查 Hash Map 的存取順序")
                
        elif hint_level >= 3:
            hints.append("📋 完整解答框架：")
            hints.append("   1. 遍歷每個元素")
            hints.append("   2. 計算 complement = target - current")
            hints.append("   3. 檢查 complement 是否在已遍歷的元素中")
            hints.append("   4. 是 → 返回 [complement的索引, 當前索引]")
            hints.append("   5. 否 → 將當前元素存入 map")
            hints.append("")
            hints.append("   正確答案思路：")
            hints.append(f"   • 正確答案：{correct_answer}")
            hints.append(f"   • 您的輸出：{actual_output}")
            hints.append("   • 兩者差異點：")
            
            if isinstance(actual_output, list) and isinstance(correct_answer, list):
                if len(actual_output) != len(correct_answer):
                    hints.append(f"     - 長度不同：{len(actual_output)} vs {len(correct_answer)}")
                else:
                    hints.append("     - 元素內容不同")
    
    else:
        diagnosis = "❌ 答案不正確"
        
        if hint_level == 1:
            hints.append("📋 結果分析：")
            hints.append(f"   您的輸出：{actual_output}")
            hints.append(f"   正確答案：{correct_answer}")
            hints.append("")
            hints.append("💡 請檢查：")
            hints.append("   • 您的演算法邏輯是否正確？")
            hints.append("   • 迴圈範圍是否正確？")
            hints.append("   • return 的時機是否正確？")
            
        elif hint_level == 2:
            hints.append("📋 追蹤執行：")
            hints.append("   請用手動追蹤以下範例：")
            hints.append("   輸入: nums = [2, 7, 11, 15], target = 9")
            hints.append("   期望輸出: [0, 1]")
            hints.append("")
            hints.append("   執行步驟：")
            hints.append("   • i=0: num=2, complement=7")
            hints.append("   • 7 在哪里？不在已處理中")
            hints.append("   • 存入 {2: 0}")
            hints.append("   • i=1: num=7, complement=2")
            hints.append("   • 2 在已處理中！找到！")
            hints.append("   • 返回 [0, 1]")
            
        elif hint_level >= 3:
            hints.append("📋 參考解答：")
            hints.append("   def two_sum(nums, target):")
            hints.append("       seen = {}")
            hints.append("       for i, num in enumerate(nums):")
            hints.append("           complement = target - num")
            hints.append("           if complement in seen:")
            hints.append("               return [seen[complement], i]")
            hints.append("           seen[num] = i")
            hints.append("       return []")
    
    suggestion = ""
    if hint_level >= 2:
        if patterns["uses_brute_force"] and not patterns["uses_hash_map"]:
            suggestion = "💡 提示：Hash Map 可將 O(n²) 優化為 O(n)"
        elif patterns["uses_hash_map"]:
            suggestion = "💡 您的 Hash Map 方向正確，檢查實作細節"
    
    return {
        "status": "needs_help",
        "diagnosis": diagnosis,
        "hints": hints,
        "suggestion": suggestion,
        "similar_test_case": similar_test_case
    }
