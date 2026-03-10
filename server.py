import os
import time
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
CREATE_TASK_URL = f"{BASE_URL}/contents/generations/tasks"
QUERY_TASK_URL_TEMPLATE = f"{BASE_URL}/contents/generations/tasks/{{task_id}}"
DEFAULT_MODEL = "doubao-seedance-1-5-pro-251215"

SEEDANCE_PROMPT_GUIDE = """提示词公式：主体+运动+环境（非必须）+运镜/切镜（非必须）+美学描述（非必须）

基础原则1 - 描述必要的信息：
给出主体、运动的限定描述，给出画面应体现的直观信息，善用程度副词。
示例：
- 一个面容沧桑、身穿中世纪海盗服饰的男子站在大海边黑色的礁石上。男子的表情富有激情，他向天空有力地举起双手，动作透露出对自由的渴望。
- 狂风暴雨中，海面上卷起巨大的海浪。海水冲进城市，撞毁岸边的房屋。数以百计的市民惊恐地逃跑。最终海啸淹没一切。
- 玩偶先是缓慢旋转，随后她停止转动，面对镜头展现自己的可爱。

基础原则2 - 描述清晰的信息：
prompt与画面形成正确对应；用特征指定主体，指定方式全程一致。
示例：
- 模特展示身上的旗袍，气质优雅，旗袍魅力十足。
- 多人场景需精准定位：画面最左边赛车服形象的人是赛车手、中间中国青年形象的人是导演、最右边黑人手上抱着摄影机形象的人是摄影师。

基础原则3 - 精准的切镜描述：
明确区分每个镜头，告诉模型确切的切镜信息；精准撰写切镜的时机；切镜之间有明确的景别/内容区分。
示例：
- 第一镜头为侧面中景，男生看向窗外。随后切镜至第二镜头，第二镜头为男生面部特写。
- 镜头从三人同框的中景开始→切镜至左侧女子近景→切镜至白人男子近景→切回三人同框中景，气氛明显变得紧张。
- 镜头1 正面中景，男子皱眉看向双手，空气中出现能量粒子。镜头2 切镜到手部特写，蓝白色能量包裹双手。镜头3 切镜面部特写，能量沿颈部攀升，眼睛亮起冷白色光。镜头4 切镜正面中远景，超级英雄战衣在身体表面快速成型。

切镜撰写进阶：
支持切镜前后风格一致（迪士尼风格动漫/皮克斯风格/写实），在提示词开头声明风格即可。
支持正反打镜头分镜（双人/三人对话场景）。
支持响应切镜时机（特效变身/影视/动漫）。

进阶技巧1 - 指定参考风格提升美感：
通过指定美学参考对象生成风格鲜明的视频。
示例：
- 模仿日剧《小森林》的风格，生成一个女孩在果园中采摘苹果视频。
- 模仿宫崎骏动漫的风格，生成一个女孩在果园中采摘苹果视频。
- 参考迪士尼2D动漫电影的风格，生成一个女孩在果园中采摘苹果视频。

进阶技巧2 - 用摄影术语提升镜头效果：

视角：
- 摄影机角度：高机位/低机位/俯视/仰视/平视/正扣/正仰
- 叙事视角：过肩视角/主观视角/监控视角/望远镜视角/蝼蚁视角/偷窥视角
- 主体角度：正面/正侧/四分之三侧/背面/顶面/底面
示例：
- 高机位俯视静谧的森林空镜，秋风卷着银杏叶掠过青石板，镜头缓推聚焦落叶堆中半露的青铜钥匙。
- 低机位从流浪汉的膝盖间仰拍表情，随着一声惊雷流浪汉吓得抬起头看向天空，镜头随动作上摇至漆黑落雨的天空。
- 固定鱼眼监控镜头，画面中心是一个人在封闭房间内焦虑徘徊，房间四面墙壁在鱼眼效应下向中心挤压弯曲。

景别（语法：主体+景别，如"左边的男人的近景"、"红衣女子的半身像"）：
- 摄影专业景别词：远景/全景/中景/近景/特写
- 美术专业景别词：头像/胸像/半身像/全身像
示例：
- 全景：荒漠黄沙中，一名旅者独自行走，镜头以全景视角捕捉广阔地平线，从左向右平稳侧移。
- 中景：一位短发少女在街角写生，镜头保持中景，从正前方缓慢绕至右前。
- 特写：镜头聚焦在一位女性的嘴唇区域，她涂着玫瑰豆沙色唇妆，镜头保持特写构图慢速推近。

运镜（公式：起幅构图描述+运镜+运镜幅度+落幅构图描述）：
- 基础运镜：推/拉/摇/移/跟/升/降/甩/环绕/旋转/变焦
- 组合运镜：希区柯克镜头=推拉+变焦；子弹时间=升格镜头+快速环绕
示例：
- 上摇：精灵族少年指了指上方然后抬起头看向树冠，镜头上升，大树枝杈间有一颗散发神秘光芒的恐龙蛋。
- 希区柯克变焦：保持女孩主体构图不变，拉镜头+镜头焦距变长。
- 推近dolly-in：镜头以中景（胸部以上）开始，以稳定的滑轨速度缓慢推近，最终到达极近距离特写（只剩眼睛与鼻梁区域）。

进阶技巧3 - 特效运用：
精准描述触发时机、变身过程、变身后细节。
示例：
- 玩法特效：她无意间用手指轻轻碰触了那颗旧圣诞球，球体内部瞬间亮起柔和的金色光芒。光芒首先缠绕女孩全身，她的衣服重塑为圣诞装扮；同时，圣诞树从地面生长，彩灯依次点亮。
- 影视特效：她的瞳孔颜色由蓝变红。以她的眼角为起点，原本细腻的皮肤开始硬化、隆起。深黑色的龙鳞仿佛从皮肤底下刺破而出，沿颧骨向脖颈快速蔓延。暗黑奇幻风格，极度逼真的8K材质细节。
- 太阳朋克特效：一束温暖的阳光刺破乌云，照射在混凝土墙面中心点。以光斑为圆心，灰色混凝土表面瞬间褪色变软，鲜嫩的绿色苔藓和藤蔓以快进摄影的速度向四周蔓延。原本死寂的墙面在几秒内变成一面随风摆动的垂直花海。吉卜力画风，色彩从单调灰瞬间转为高饱和的绚烂。

图生视频特别说明：
图片已决定画面内容，prompt 的唯一任务是描述"画面怎么动"和"镜头怎么运动"，不要重复描述图片中已有的内容，不要与图片内容矛盾。
示例：
- 上传人像时：女性缓缓抬起头，温暖地微笑，固定机位，柔和灯光。
- 上传风景时：云层缓缓流动，树枝轻轻摇曳，远处有鸟飞过，缓慢推进镜头。"""

mcp = FastMCP("seedance-mcp")


def _get_api_key() -> str:
    api_key = os.getenv("ARK_API_KEY")
    if not api_key:
        raise ValueError("ARK_API_KEY 未配置，请在 .env 中设置 ARK_API_KEY")
    return api_key


def _headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {_get_api_key()}",
        "Content-Type": "application/json",
    }


def _create_task(payload: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(CREATE_TASK_URL, headers=_headers(), json=payload, timeout=60)
    data = response.json()
    return {
        "status_code": response.status_code,
        "response": data,
    }


def _query_task(task_id: str) -> Dict[str, Any]:
    url = QUERY_TASK_URL_TEMPLATE.format(task_id=task_id)
    response = requests.get(url, headers=_headers(), timeout=60)
    data = response.json()
    return {
        "status_code": response.status_code,
        "response": data,
    }


def poll_task(task_id: str, interval_seconds: int = 10, max_wait_seconds: int = 300) -> Dict[str, Any]:
    max_attempts = max_wait_seconds // interval_seconds
    history: List[Dict[str, Any]] = []

    for attempt in range(1, max_attempts + 1):
        task_result = _query_task(task_id)
        response_body = task_result.get("response", {})
        status = response_body.get("status")
        history.append(
            {
                "attempt": attempt,
                "status": status,
                "status_code": task_result.get("status_code"),
                "response": response_body,
            }
        )

        if status in {"succeeded", "failed", "expired"}:
            return {
                "task_id": task_id,
                "final_status": status,
                "poll_history": history,
                "final_response": response_body,
            }

        if attempt < max_attempts:
            time.sleep(interval_seconds)

    return {
        "task_id": task_id,
        "final_status": "timeout",
        "poll_history": history,
        "message": f"超过 {max_wait_seconds} 秒任务仍未结束",
    }


@mcp.tool(description="根据文本提示词生成视频。将 prompt 发送给 Seedance API 创建视频生成任务并轮询至完成。严禁未经用户确认 prompt 就直接调用此工具，必须先向用户展示完整 prompt 并获得明确确认后才可调用。")
def text_to_video(
    prompt: str,
    model: str = DEFAULT_MODEL,
    resolution: str = "480p",
    ratio: str = "16:9",
    duration: int = 5,
    watermark: bool = False,
    generate_audio: bool = False,
) -> Dict[str, Any]:
    payload = {
        "model": model,
        "content": [
            {
                "type": "text",
                "text": prompt,
            }
        ],
        "resolution": resolution,
        "ratio": ratio,
        "duration": duration,
        "watermark": watermark,
        "generate_audio": generate_audio,
    }

    create_result = _create_task(payload)
    create_response = create_result.get("response", {})
    task_id = create_response.get("id")

    result: Dict[str, Any] = {
        "create_task": create_result,
        "task_id": task_id,
    }

    if not task_id:
        result["error"] = "创建任务成功返回中未找到 id"
        return result

    result["poll_result"] = poll_task(task_id)
    return result


@mcp.tool(description="根据图片和运动描述生成视频。将图片 URL 和 motion prompt 发送给 Seedance API 创建视频生成任务并轮询至完成。严禁未经用户确认 prompt 就直接调用此工具，必须先向用户展示完整 prompt 并获得明确确认后才可调用。")
def image_to_video(
    image_url: str,
    motion_prompt: str,
    model: str = DEFAULT_MODEL,
    resolution: str = "480p",
    ratio: str = "16:9",
    duration: int = 5,
    watermark: bool = False,
    generate_audio: bool = False,
) -> Dict[str, Any]:
    content: List[Dict[str, Any]] = [
        {
            "type": "image_url",
            "image_url": image_url,
        }
    ]

    if motion_prompt:
        content.append(
            {
                "type": "text",
                "text": motion_prompt,
            }
        )

    payload = {
        "model": model,
        "content": content,
        "resolution": resolution,
        "ratio": ratio,
        "duration": duration,
        "watermark": watermark,
        "generate_audio": generate_audio,
    }

    create_result = _create_task(payload)
    create_response = create_result.get("response", {})
    task_id = create_response.get("id")

    result: Dict[str, Any] = {
        "create_task": create_result,
        "task_id": task_id,
    }

    if not task_id:
        result["error"] = "创建任务成功返回中未找到 id"
        return result

    result["poll_result"] = poll_task(task_id)
    return result


@mcp.tool()
def query_task(task_id: str) -> Dict[str, Any]:
    return _query_task(task_id)


if __name__ == "__main__":
    mcp.run()
