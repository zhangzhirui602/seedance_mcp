import os
import sys
import time

import requests
from dotenv import load_dotenv

CREATE_TASK_URL = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"
GET_TASK_URL_TEMPLATE = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}"


def main() -> None:
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
        "model": "doubao-seedance-1-5-pro-251215",
        "content": [
            {
                "type": "text",
                "text": "一只橙色的猫在草地上打哈欠",
            }
        ],
        "resolution": "480p",
        "ratio": "16:9",
        "duration": 5,
        "watermark": False,
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
