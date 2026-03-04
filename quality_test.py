import json
import os
import time
from typing import Any, Dict, Tuple

import requests
from dotenv import load_dotenv

BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
CREATE_TASK_URL = f"{BASE_URL}/contents/generations/tasks"
QUERY_TASK_URL_TEMPLATE = f"{BASE_URL}/contents/generations/tasks/{{task_id}}"
MODEL = "doubao-seedance-1-5-pro-251215"


def headers() -> Dict[str, str]:
    load_dotenv()
    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        raise RuntimeError("未读取到 ARK_API_KEY，请检查 .env")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def create_text_to_video_task(prompt: str) -> Dict[str, Any]:
    payload = {
        "model": MODEL,
        "content": [{"type": "text", "text": prompt}],
        "resolution": "480p",
        "ratio": "16:9",
        "duration": 5,
        "watermark": False,
        "generate_audio": False,
    }
    response = requests.post(CREATE_TASK_URL, headers=headers(), json=payload, timeout=60)
    print("创建任务完整响应:")
    print(response.text)
    response.raise_for_status()
    return response.json()


def query_task(task_id: str) -> Dict[str, Any]:
    url = QUERY_TASK_URL_TEMPLATE.format(task_id=task_id)
    response = requests.get(url, headers=headers(), timeout=60)
    print("查询任务完整响应:")
    print(response.text)
    response.raise_for_status()
    return response.json()


def poll_until_done(task_id: str, interval_seconds: int = 10, max_attempts: int = 30) -> Dict[str, Any]:
    for attempt in range(1, max_attempts + 1):
        print(f"第 {attempt} 次查询: task_id={task_id}")
        data = query_task(task_id)
        status = data.get("status")
        print(f"当前状态: {status}")

        if status in {"succeeded", "failed", "expired"}:
            return data

        if attempt < max_attempts:
            time.sleep(interval_seconds)

    return {"status": "timeout", "task_id": task_id}


def download_video(video_url: str, output_name: str) -> None:
    response = requests.get(video_url, stream=True, timeout=180)
    response.raise_for_status()

    with open(output_name, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

    size_kb = os.path.getsize(output_name) / 1024
    print(f"下载完成: {output_name} ({size_kb:.1f} KB)")


def run_case(case_name: str, prompt: str, output_name: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    print("=" * 60)
    print(f"开始测试: {case_name}")
    create_data = create_text_to_video_task(prompt)
    task_id = create_data.get("id")
    if not task_id:
        raise RuntimeError(f"{case_name} 创建任务未返回 id")

    final_data = poll_until_done(task_id)
    if final_data.get("status") != "succeeded":
        raise RuntimeError(f"{case_name} 任务未成功: {final_data}")

    video_url = final_data.get("content", {}).get("video_url")
    if not video_url:
        raise RuntimeError(f"{case_name} 未返回 video_url")

    download_video(video_url, output_name)
    return create_data, final_data


def main() -> None:
    baseline_prompt = "一位年轻女性站在窗边看雨。"

    guided_prompt = (
        "主体+运动+环境+运镜+美学："
        "一位短发年轻女性站在老木窗前，注视窗外雨幕，先缓慢抬头再轻轻转身。"
        "环境是黄昏室内，木质桌面上有一杯冒热气的茶，窗外细雨连绵。"
        "镜头1为中景平视，从右向左缓慢侧移；"
        "镜头2切至女性面部近景，轻微推近，捕捉眼神变化；"
        "镜头3切回半身像，镜头缓慢后拉，呈现房间与雨景关系。"
        "整体电影感写实风格，暖色室内与冷色雨景对比，画面细节自然。"
    )

    baseline_create, baseline_final = run_case(
        case_name="A-普通提示词",
        prompt=baseline_prompt,
        output_name="quality_baseline.mp4",
    )

    guided_create, guided_final = run_case(
        case_name="B-指南增强提示词",
        prompt=guided_prompt,
        output_name="quality_guided.mp4",
    )

    result = {
        "model": MODEL,
        "baseline": {
            "prompt": baseline_prompt,
            "create": baseline_create,
            "final": baseline_final,
            "output_file": "quality_baseline.mp4",
        },
        "guided": {
            "prompt": guided_prompt,
            "create": guided_create,
            "final": guided_final,
            "output_file": "quality_guided.mp4",
        },
    }

    with open("quality_test_result.json", "w", encoding="utf-8") as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

    print("=" * 60)
    print("A/B 测试完成")
    print("对比文件:")
    print("- quality_baseline.mp4")
    print("- quality_guided.mp4")
    print("结果记录:")
    print("- quality_test_result.json")


if __name__ == "__main__":
    main()
