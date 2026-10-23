# Looktech EDU 眼镜 Demo

基于独立[Python SDK](https://github.com/Entertech/edu-glasses-host/tree/feat/edu-sdk-integration)
调用眼镜能力。包含CLI、五本教学Notebook与耳机示例；通过pip安装SDK依赖，仓库内不复制`edu_host`实现。

## 安装与运行

Python 3.9+、Git。先在系统蓝牙设置配对烧录EDU固件的`EDU-Glasses-xxxx`眼镜。

```bash
git clone https://github.com/Entertech/edu-glasses-demo.git
cd edu-glasses-demo
python -m venv .venv
# macOS/Linux：source .venv/bin/activate
# Windows PowerShell：.\.venv\Scripts\Activate.ps1
python -m pip install -e .
edu-glasses --bt auto
```

安装会拉取已固定commit的SDK及CLI原有依赖；macOS自动安装IOBluetooth绑定，
Windows/Linux蓝牙使用标准库socket。WAV解码另需系统libopus，否则保留`.opusraw`。
首次运行macOS需要授予终端或Python宿主蓝牙权限。
源码方式也可运行`python demo_cli.py --bt auto`，多台眼镜时用明确地址替换`auto`。

安装后在CLI中输入：

```text
info
sensors
video config
video config --resolution 1080p --orientation portrait --max-duration 60
photo-save
video start
wait 5
video stop
media open /absolute/path/wifi.json
media list
media download all /absolute/path/captures
media close
quit
```

`wifi.json`自行创建本地文件，字段为`ssid`、`security`（如`WPA2`）及`password`。
PC与眼镜需要处于互通局域网。SPP负责控制和媒体身份查询，原件通过WiFi下载。
`media delete <id>`是显式删除；下载默认保留原件。充电/低电规则由公版能力检查处理。

## 按键、灯效与其他能力

固件声明`NATIVE_INPUT`时，右侧单击拍照、长按录像、再按停止由固件直接执行，PC断开仍可使用。
CLI保留原始事件显示，并关闭旧拍摄映射以免重复触发；旧固件继续使用PC映射。灯效复用公版生命周期。
`capture status`只读查询设备照片/视频的来源和控制状态，不接管本地录像。
录音双击依公版配置请求PC准备文件，CLI在主循环先打开`captures/record-<时间>.wav`再启动录音；
按键停止时完成文件。CLI忙碌时忽略开始请求，排队超过5秒不延迟开麦。需要音频通道及解码依赖。
旋钮音量、媒体/通话键沿用固件行为。原始事件仍可自定义观察；AI/翻译完整服务本次未提供。
请先安装新版SDK/demo再更新固件，旧demo可能重复拍摄。本轮未烧录实测。
录音、教学小图、LED、提示音、OTA、串口后备与管道调用，见[CLI完整使用说明](docs/CLI_GUIDE.md)。
`help`列出当前命令。自己的应用直接调用SDK，不解析CLI打印文本。

## 教学Notebook与耳机示例

```bash
python -m pip install -e '.[notebooks]'
cd examples/notebooks
jupyter lab
```

| 示例 | 内容 |
|---|---|
| [01_photo_analysis.ipynb](examples/notebooks/01_photo_analysis.ipynb) | 拍照与图像分析 |
| [02_audio_analysis.ipynb](examples/notebooks/02_audio_analysis.ipynb) | 录音与波形分析 |
| [03_live_sensors.ipynb](examples/notebooks/03_live_sensors.ipynb) | 传感器实时展示 |
| [04_knob_events.ipynb](examples/notebooks/04_knob_events.ipynb) | 旋钮事件交互 |
| [05_wifi_media_export.ipynb](examples/notebooks/05_wifi_media_export.ipynb) | 存储拍摄与WiFi原件导出 |

`edu_notebook.py`是教学薄包装，复用SDK。Notebook按顺序执行，退出时调用`close()`。
耳机示例走系统A2DP/HFP音频设备：

```bash
python -m pip install -e '.[headset]'
python examples/headset_demo.py list
```

## SDK集成与维护

- 只开发应用：[SDK安装和使用说明](https://github.com/Entertech/edu-glasses-host/blob/feat/edu-sdk-integration/docs/SDK_GUIDE.md)。
- 完整线协议：[PROTOCOL.md](https://github.com/Entertech/edu-glasses-host/blob/feat/edu-sdk-integration/docs/PROTOCOL.md)。
- SDK/demo拆分来源：`Entertech/edu-glasses-host@82f6493fc59703ccffbc0c1d005712aaaac18ade`。
  CLI调用及按键行为保持原样，原有3项CLI检查随代码迁入本仓库。
- 更新SDK时修改`pyproject.toml`中的固定commit，并验证安装、既有CLI检查及所影响能力。

```bash
python -m unittest discover -s tests -v
python demo_cli.py --help
```

不包含固件或WiFi凭据。实机功能结论沿用SDK文档中的2026-10-21验收记录；
本轮仓库拆分验证安装及调用入口，不代表重跑了实机或系统保护矩阵。
