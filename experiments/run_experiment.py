"""
TransLive 实验脚本

实验 1：功能正确性测试（20 条用例）
实验 2：不同文本长度的响应时间测试
实验 3：防抖效果模拟（请求次数对比）

用法:
    python run_experiment.py --api http://localhost:8000
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

import httpx

RESULTS_DIR = Path(__file__).parent / "results"


def load_test_cases() -> dict:
    path = Path(__file__).parent / "test_cases.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def translate(client: httpx.Client, api_base: str, text: str, source: str, target: str) -> dict:
    started = time.perf_counter()
    response = client.post(
        f"{api_base}/api/translate",
        json={"text": text, "source": source, "target": target},
        timeout=60.0,
    )
    elapsed = round((time.perf_counter() - started) * 1000, 2)
    response.raise_for_status()
    data = response.json()
    data["client_latency_ms"] = elapsed
    return data


def run_functional_test(client: httpx.Client, api_base: str, cases: list) -> dict:
    results = []
    success = 0

    for case in cases:
        try:
            data = translate(client, api_base, case["text"], case["source_lang"], case["target_lang"])
            ok = bool(data.get("translated_text", "").strip())
            success += int(ok)
            results.append(
                {
                    "id": case["id"],
                    "category": case["category"],
                    "source": case["text"],
                    "translation": data.get("translated_text"),
                    "latency_ms": data.get("latency_ms"),
                    "success": ok,
                }
            )
        except Exception as exc:
            results.append(
                {
                    "id": case["id"],
                    "category": case["category"],
                    "source": case["text"],
                    "error": str(exc),
                    "success": False,
                }
            )

    return {
        "experiment": "functional_correctness",
        "total": len(cases),
        "success_count": success,
        "success_rate": round(success / len(cases) * 100, 1) if cases else 0,
        "results": results,
    }


def run_performance_test(client: httpx.Client, api_base: str, sample_texts: dict, repeats: int = 10) -> dict:
    summary = []

    for length_key, text in sample_texts.items():
        latencies = []
        for _ in range(repeats):
            data = translate(client, api_base, text, "en", "zh")
            latencies.append(data.get("latency_ms", data.get("client_latency_ms", 0)))

        summary.append(
            {
                "text_length": int(length_key),
                "actual_length": len(text),
                "repeats": repeats,
                "avg_ms": round(statistics.mean(latencies), 2),
                "min_ms": round(min(latencies), 2),
                "max_ms": round(max(latencies), 2),
                "p95_ms": round(sorted(latencies)[int(len(latencies) * 0.95) - 1], 2),
            }
        )

    return {
        "experiment": "performance_latency",
        "repeats_per_length": repeats,
        "summary": summary,
    }


def simulate_debounce(text: str, debounce_ms: int = 500, char_interval_ms: int = 80) -> dict:
    """模拟用户逐字输入时的 API 请求次数。"""

    def count_requests(use_debounce: bool) -> int:
        requests = 0
        last_input_time = 0.0
        pending_timer_fired = False

        for i in range(1, len(text) + 1):
            current_time = i * char_interval_ms
            if use_debounce:
                if current_time - last_input_time >= debounce_ms or i == len(text):
                    requests += 1
                    last_input_time = current_time
            else:
                requests += 1

        return requests

    without_debounce = count_requests(False)
    with_debounce = count_requests(True)
    reduction = round((1 - with_debounce / without_debounce) * 100, 1) if without_debounce else 0

    return {
        "experiment": "debounce_simulation",
        "input_length": len(text),
        "debounce_ms": debounce_ms,
        "char_interval_ms": char_interval_ms,
        "requests_without_debounce": without_debounce,
        "requests_with_debounce": with_debounce,
        "reduction_percent": reduction,
    }


def main():
    parser = argparse.ArgumentParser(description="Run TransLive experiments")
    parser.add_argument("--api", default="http://localhost:8000", help="Backend API base URL")
    parser.add_argument("--repeats", type=int, default=5, help="Performance test repeats per length")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)
    data = load_test_cases()

    print(f"TransLive 实验开始，API: {args.api}")

    with httpx.Client() as client:
        health = client.get(f"{args.api}/health", timeout=10.0)
        health.raise_for_status()
        print("✓ 后端健康检查通过")

        print("\n[实验 1] 功能正确性测试...")
        functional = run_functional_test(client, args.api, data["cases"])
        print(f"  成功率: {functional['success_count']}/{functional['total']} ({functional['success_rate']}%)")

        print("\n[实验 2] 响应时间测试...")
        performance = run_performance_test(client, args.api, data["sample_texts"], repeats=args.repeats)
        for row in performance["summary"]:
            print(f"  长度 {row['actual_length']:>3} 字符: 平均 {row['avg_ms']} ms")

    print("\n[实验 3] 防抖效果模拟...")
    debounce = simulate_debounce(data["sample_texts"]["100"])
    print(
        f"  无防抖: {debounce['requests_without_debounce']} 次请求, "
        f"有防抖: {debounce['requests_with_debounce']} 次, "
        f"减少 {debounce['reduction_percent']}%"
    )

    all_results = {
        "api_base": args.api,
        "functional": functional,
        "performance": performance,
        "debounce": debounce,
    }

    output_path = RESULTS_DIR / "experiment_results.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print(f"\n实验结果已保存: {output_path}")


if __name__ == "__main__":
    main()
