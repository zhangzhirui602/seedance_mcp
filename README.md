# Seedance API 测试说明

## 1. 安装依赖
```bash
pip install -r requirements.txt
```

## 2. 配置 API Key
在项目根目录创建 `.env`：

```env
ARK_API_KEY=你的火山方舟API_KEY
```

## 3. 运行文生视频测试
```bash
python test_api.py
```

也可以在运行时选择分辨率、比例和时长：

```bash
python test_api.py --resolution 720p --ratio 9:16 --duration 8
```

其他常用参数示例：

```bash
python test_api.py --prompt "赛博朋克城市夜景" --model doubao-seedance-1-5-pro-251215 --watermark
```

### 常用参数可选值示例

- 常见比例（`--ratio`）：`16:9`（横屏）、`9:16`（竖屏）、`1:1`（方形）
- 常见时长（`--duration`）：`5`、`8`、`10`

可直接复制的命令：

```bash
# 横屏短视频
python test_api.py --resolution 720p --ratio 16:9 --duration 5

# 竖屏短视频（适合短视频平台）
python test_api.py --resolution 720p --ratio 9:16 --duration 8

# 方形视频
python test_api.py --resolution 720p --ratio 1:1 --duration 10
```

脚本会：
- 创建视频生成任务
- 每 10 秒轮询任务状态（最多 30 次）
- 成功后打印完整响应（包含 `video_url`）

## 4. 下载视频到本地（可选）
```bash
python download_video.py
```

默认输出文件：`output_video.mp4`
