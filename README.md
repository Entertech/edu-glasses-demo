# Looktech Glasses Demo

基于独立 Python SDK `looktech-glasses-sdk`，通过 CLI、交互式 Notebook 和可运行示例
体验眼镜能力，并作为二次开发参考。SDK 由 pip 安装，仓库内不复制 `looktech_glasses_sdk` 实现。

首次接入请从[Python SDK 开发者指南](docs/SDK_GUIDE.md)开始：产品介绍、开发者固件准备、
OTA 升级准备、帮助中心、Python 安装，以及拍摄、录音和 WiFi 导出的完整接入示例。
开发前请联系我们，由我们通过 OTA 协助将公版固件升级为开发者固件；App 内没有开发者固件升级入口。

## 安装与运行

> 当前为更名候选版本；新 PyPI 包发布前，请先构建并安装 SDK wheel，再从本仓库安装 Demo。下列 PyPI 命令在新版本发布后使用。

demo 0.4.0 使用更名后的 [SDK 0.6.0](https://pypi.org/project/looktech-glasses-sdk/0.6.0/)，安装时自动拉取对应平台的二进制 wheel。
支持的 Python/平台见[开发者指南](docs/SDK_GUIDE.md#5-准备-python-环境并安装)。

Python 3.9+、Git。先在系统蓝牙设置配对烧录开发者固件的`EDU-Glasses-xxxx`眼镜。

```bash
git clone https://github.com/Entertech/looktech-glasses-demo.git
cd looktech-glasses-demo
python -m venv .venv
# macOS/Linux：source .venv/bin/activate
# Windows PowerShell：.\.venv\Scripts\Activate.ps1
python -m pip install -e .
looktech-glasses --bt auto
```

安装会从 PyPI 拉取固定版本 0.6.0 的二进制 SDK 及 CLI 依赖；macOS自动安装IOBluetooth绑定，
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
按键停止时完成文件。CLI忙碌区间内的开始请求会被忽略，即使命令失败后才投递；接收后超过5秒也不延迟开麦。需要音频通道及解码依赖。
旋钮音量、媒体/通话键沿用固件行为。原始事件仍可自定义观察；AI/翻译完整服务本次未提供。
请先安装新版SDK/demo再更新固件，旧demo可能重复拍摄。实际验收范围见[开发者指南](docs/SDK_GUIDE.md#16-兼容性与已知限制)。
录音、SPP JPEG 小图、LED、提示音、OTA、串口后备与管道调用，见[CLI完整使用说明](docs/CLI_GUIDE.md)。
`help`列出当前命令。自己的应用直接调用SDK，不解析CLI打印文本。

## 交互式 Notebook 与耳机示例

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

`glasses_notebook.py`是示例辅助封装，复用SDK。Notebook按顺序执行，退出时调用`close()`。
耳机示例走系统A2DP/HFP音频设备：

```bash
python -m pip install -e '.[headset]'
python examples/headset_demo.py list
```

## SDK集成与维护

- 外部应用接入：[Python SDK 开发者指南](docs/SDK_GUIDE.md)。
- 接口参数和返回类型：[SDK 接口参考](docs/API_REFERENCE.md)。
- SDK 二进制包从 PyPI 安装，使用者不需要实现仓库权限。
- SDK/demo拆分来源：`Entertech/looktech-glasses-sdk@82f6493fc59703ccffbc0c1d005712aaaac18ade`。
  CLI调用及按键行为保持原样，原有3项CLI检查随代码迁入本仓库。
- 更新SDK时修改`pyproject.toml`中的固定版本，并验证安装、既有CLI检查及所影响能力。

```bash
python -m unittest discover -s tests -v
python demo_cli.py --help
```

不包含当前固件发行包或WiFi凭据。验收记录按版本区分，见开发者指南中的兼容性与已知限制；
示例入口检查不代表完成全部平台、首次固件切换或系统保护矩阵的实测。
