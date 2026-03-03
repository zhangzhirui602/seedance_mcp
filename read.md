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

脚本会：
- 创建视频生成任务
- 每 10 秒轮询任务状态（最多 30 次）
- 成功后打印完整响应（包含 `video_url`）

## 4. 下载视频到本地（可选）
```bash
python download_video.py
```

默认输出文件：`output_video.mp4`
