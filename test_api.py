import os
import sys
import time
import argparse

import requests
from dotenv import load_dotenv

CREATE_TASK_URL = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"
GET_TASK_URL_TEMPLATE = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seedance 文生视频测试")
    parser.add_argument("--prompt", default="一只橙色的猫在草地上打哈欠", help="视频提示词")
    parser.add_argument("--model", default="doubao-seedance-1-5-pro-251215", help="模型名称")
    parser.add_argument("--resolution", default="480p", help="视频分辨率，例如 480p/720p/1080p")
    parser.add_argument("--ratio", default="16:9", help="视频比例，例如 16:9/9:16/1:1")
    parser.add_argument("--duration", type=int, default=5, help="视频时长（秒）")
    parser.add_argument("--watermark", action="store_true", help="开启水印")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    load_dotenv()
    api_key = os.getenv("ARK_API_KEY")

    if not api_key:
        print("错误：未在 .env 中读取到 ARK_API_KEY")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": args.model,
        "content": [
            {
                "type": "text",
                "text": args.prompt,
            }
        ],
        "resolution": args.resolution,
        "ratio": args.ratio,
        "duration": args.duration,
        "watermark": args.watermark,
    }

    print("开始创建任务...")
    try:
        create_resp = requests.post(CREATE_TASK_URL, headers=headers, json=payload, timeout=60)
        print("创建任务接口完整响应：")
        print(create_resp.text)
    except Exception as exc:
        print(f"创建任务请求异常：{exc}")
        sys.exit(1)

    try:
        create_data = create_resp.json()
    except Exception as exc:
        print(f"创建任务响应不是合法 JSON：{exc}")
        sys.exit(1)

    task_id = create_data.get("id")
    if not task_id:
        print("错误：创建任务响应中未获取到 task_id（id 字段）")
        sys.exit(1)

    print(f"成功创建任务，task_id = {task_id}")

    for i in range(1, 31):
        time.sleep(10)
        print(f"第 {i} 次查询任务状态...")
        query_url = GET_TASK_URL_TEMPLATE.format(task_id=task_id)

        try:
            query_resp = requests.get(query_url, headers=headers, timeout=60)
            print("查询任务接口完整响应：")
            print(query_resp.text)
        except Exception as exc:
            print(f"查询任务请求异常：{exc}")
            continue

        try:
            query_data = query_resp.json()
        except Exception as exc:
            print(f"查询任务响应不是合法 JSON：{exc}")
            continue

        status = query_data.get("status")
        print(f"当前状态：{status}")

        if status == "succeeded":
            print("任务成功，完整响应如下：")
            print(query_resp.text)
            break

        if status in {"failed", "expired"}:
            print(f"任务结束，状态为 {status}，完整响应如下：")
            print(query_resp.text)
            break
    else:
        print("超时：查询 30 次（300 秒）后任务仍未完成")


if __name__ == "__main__":
    main()
