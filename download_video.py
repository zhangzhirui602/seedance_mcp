import os
import sys

import requests
from dotenv import load_dotenv

TASK_ID = "cgt-20260303183702-lgjnx"
GET_TASK_URL_TEMPLATE = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks/{task_id}"


def main() -> None:
    load_dotenv()
    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        print("错误：未在 .env 中读取到 ARK_API_KEY")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {api_key}"}

    print(f"查询任务 {TASK_ID} ...")
    resp = requests.get(
        GET_TASK_URL_TEMPLATE.format(task_id=TASK_ID),
        headers=headers,
        timeout=60,
    )
    data = resp.json()
    print("任务响应：", data)

    status = data.get("status")
    if status != "succeeded":
        print(f"任务状态为 {status}，无法下载")
        sys.exit(1)

    video_url = data.get("content", {}).get("video_url")
    if not video_url:
        print("未找到 video_url")
        sys.exit(1)

    print(f"开始下载视频：{video_url[:80]}...")
    video_resp = requests.get(video_url, stream=True, timeout=120)
    video_resp.raise_for_status()

    output_path = "output_video.mp4"
    with open(output_path, "wb") as f:
        for chunk in video_resp.iter_content(chunk_size=8192):
            f.write(chunk)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"下载完成！文件保存至：{output_path}（{size_kb:.1f} KB）")


if __name__ == "__main__":
    main()
