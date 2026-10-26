# Looktech EDU Python SDK 开发者指南

面向首次接触 Looktech 的外部开发者：先准备眼镜和 EDU 固件，再安装 SDK，把拍摄、录音、传感器和事件接入自己的 Python 项目。

本文对应 Python SDK **0.5.0**、demo **0.3.0**，更新于 2026-10-26。
**发布前待补充：当前 EDU 固件的正式获取方式，以及 App 安装 EDU 固件的具体入口、适用版本和操作步骤。** 其余章节可作为当前 SDK 的接入参考。

## 阅读顺序

1. [认识产品与开发模式](#1-认识产品与开发模式)
2. [获取 EDU 固件](#2-获取-edu-固件)
3. [通过 App 升级为 EDU 固件](#3-通过-app-升级为-edu-固件)
4. [眼镜基础操作与帮助中心](#4-眼镜基础操作与帮助中心)
5. [准备 Python 环境并安装](#5-准备-python-环境并安装)
6. [运行第一个程序](#6-运行第一个程序)
7. [连接与会话管理](#7-连接与会话管理)
8. [设备信息与传感器](#8-设备信息与传感器)
9. [拍照录像与录像配置](#9-拍照录像与录像配置)
10. [通过 WiFi 导出照片和视频](#10-通过-wifi-导出照片和视频)
11. [麦克风录音](#11-麦克风录音)
12. [按键旋钮与状态事件](#12-按键旋钮与状态事件)
13. [LED提示音重启与后续升级](#13-led提示音重启与后续升级)
14. [集成到自己的应用与排障](#14-集成到自己的应用与排障)
15. [API与示例索引](#15-api与示例索引)
16. [兼容性与已知限制](#16-兼容性与已知限制)

## 1. 认识产品与开发模式

Looktech AI Glasses 支持第一视角照片和视频采集、音频采集，以及音乐播放和通话。
公版配合 Looktech App 使用，提供 Memo 等应用服务。首次使用可以先阅读
[产品快速指南](https://help.looktech.ai/en/articles/12542097-looktech-quick-guide)。

EDU 固件为 PC 开发开放设备接口。你可以用 Python 读取传感器、获取图片和音频、控制拍摄，
也可以把这些数据接入自己的视觉、语音或教学应用。SDK 不包含现成的 AI 模型或完整 Memo/翻译服务。

| 组成 | 作用 |
|---|---|
| EDU 固件 | 在眼镜上提供开发接口，执行设备能力和保护检查 |
| Python SDK：`edu-glasses-host` | 安装后通过 `from edu_host import EduSession` 调用设备 |
| 本 demo 仓库 | CLI、可运行示例和教学 Notebook，展示 SDK 的用法 |
| Looktech App | 公版的设备设置与应用服务；本文预留通过 App 安装 EDU 固件的准备流程 |

PC 通过经典蓝牙 SPP 发命令、收事件和音频；教学 JPEG 也可通过 SPP 回传。
保存在眼镜中的照片、视频原件使用 **SPP 控制 + 局域网 WiFi 下载**。
系统音乐和通话使用标准蓝牙音频设备，和 Python 的 SPP 数据接口分别使用。

## 2. 获取 EDU 固件

### 获取

开始开发前，请先取得与你的眼镜硬件匹配的 EDU 固件和配套升级说明。
**官方获取入口（下载页或申请方式）：待补充。**

领取时请核对以下信息：

- 适用眼镜型号和硬件版本。
- 固件版本及支持的 SDK 版本。
- 对应升级方式所需的包和操作说明。
- 文件校验值（如发行方提供）；下载后按发行说明核对。

开发阶段的历史包不作为本指南的正式下载入口；其中可能不包含当前录像配置、WiFi 导出或原生按键能力。

### 使用

**眼镜仍运行公版固件、首次切换为 EDU 时**，App 升级准备和待确认步骤见[第 3 节](#3-通过-app-升级为-edu-固件)。
App 所用升级包和操作方式以配套发行说明为准。

**眼镜已运行 EDU 固件时**，后续更新可使用[第 13 节的 SDK OTA 接口](#13-led提示音重启与后续升级)。
该接口的包格式和前置条件见对应章节。

升级后按下节确认版本与能力；媒体导出还需查询 `media_capabilities()`，不能只根据文件名判断支持范围。

## 3. 通过 App 升级为 EDU 固件

### 升级前准备

1. 从 [Looktech 官方下载页](https://app.looktech.ai/)安装 App，并在眼镜仍运行公版时完成 App 连接。
   首次配对参考[首次使用指南](https://help.looktech.ai/en/articles/11476917-start-your-first-journey-with-looktech)。
2. 按上一节取得适配当前硬件、明确用于 App 切换 EDU 的固件及配套说明。
3. 确认说明中要求的 App 版本及是否需要开通 EDU 升级入口。
   **具体 App 版本和开通条件：待补充。**

### 使用固件完成升级

**App 内 EDU 升级入口及点击步骤：待补充。** 以下列出升级期间的准备与检查事项，尚不能代替完整点选教程。

1. 按配套发行说明进入 App 的 EDU 升级流程，核对当前设备与目标固件。
2. 按 App 提示满足电量等条件。升级期间保持 App 前台、手机解锁、网络稳定；
   [官方升级故障帮助](https://help.looktech.ai/en/articles/12553271-firmware-update-failed)提供通用排障。
3. 按 App 和发行说明完成升级，等待眼镜启动，再按下面的方法确认结果。

### 确认升级结果

1. 按[第 5 节](#5-准备-python-环境并安装)安装 SDK 或 demo。
2. 在 PC 系统蓝牙设置中配对 `EDU-Glasses-xxxx`，按[第 6 节](#6-运行第一个程序)运行信息查询示例。
3. 核对输出的设备版本与发行说明，并检查 `glasses.capabilities`；使用媒体导出前再查询 `media_capabilities()`。

App 断开连接本身不能证明升级成功或失败。当前 EDU 的后续开发连接使用 PC 系统配对和 SPP，
无需完成公版 App 绑定。App 中的普通公版更新也不能直接当作 EDU 切换教程。
本指南尚未实测“公版 → App 安装 EDU”的完整路径。

### 恢复公版

**EDU 切回公版的官方方式：待补充。** 当前 EDU 固件不提供公版 App 的 BLE/绑定业务入口，
不能预设仍可通过原来的 App 连接方式直接切回公版；切换前需向发行方确认恢复方法。

## 4. 眼镜基础操作与帮助中心

先认识三个操作部件：左镜腿上方的 **AI 键**、右镜腿上方的 **拍照键**，以及右镜腿下方的 **媒体旋钮**。
位置和日常操作图示见[按键说明](https://help.looktech.ai/en/articles/11476722-controls-by-button)。

| 目的 | 操作与说明 |
|---|---|
| 开机 | 短按拍照键；无响应时先充电。参考[首次使用指南](https://help.looktech.ai/en/articles/11476917-start-your-first-journey-with-looktech) |
| 关机 | 同时按住 AI 键和拍照键约 3 秒，等待关机反馈。参考[关机说明](https://help.looktech.ai/en/articles/13106497-how-to-turn-the-glasses-off) |
| 充电 | 使用配套充电夹或充电盒，确保触点对齐；橙色表示充电、绿色表示充满。参考[产品快速指南](https://help.looktech.ai/en/articles/12542097-looktech-quick-guide) |
| 拍照 | 当前原生 EDU 固件下，右侧拍照键单击，原片保存在眼镜 |
| 录像 | 长按拍照键开始，录像中再短按停止；正常白灯、提示音由固件管理 |
| PC 录音 | AI 键双击配置为录音时，请求接收程序准备文件；需要运行接收程序，再短按 AI 键停止 |
| 音乐/通话 | 通过系统蓝牙音频使用媒体旋钮，控制含义见[按键说明](https://help.looktech.ai/en/articles/11476722-controls-by-button) |
| 手动进入配对 | 拍照键快速三击，松手后在 10 秒内再长按约 5 秒。操作细节见[配对说明](https://help.looktech.ai/en/articles/12437314-manually-entering-pairing-mode)；EDU 随后在 PC 系统蓝牙中配对 |

帮助中心描述的是产品日常使用；其中 Memo、公版 App 导入等功能不代表 EDU SDK 已提供相同应用服务。
EDU 下载默认保留眼镜原件，删除使用显式接口。原生按键和 PC 的关系见第 12 节。

常用官方入口：

- [帮助中心首页](https://help.looktech.ai/en/)
- [产品快速指南](https://help.looktech.ai/en/articles/12542097-looktech-quick-guide)
- [首次使用与配对](https://help.looktech.ai/en/articles/11476917-start-your-first-journey-with-looktech)
- [固件升级失败排查](https://help.looktech.ai/en/articles/12553271-firmware-update-failed)

## 5. 准备 Python 环境并安装

要求标准 **CPython 3.9–3.14**。SDK 从 PyPI 安装二进制 wheel，不需要实现仓库权限、Git 或本机编译器；只集成 SDK 时不必安装 demo。
[SDK 0.5.0 已发布到 PyPI](https://pypi.org/project/edu-glasses-host/0.5.0/)。自己的项目可在 `requirements.txt` 固定同一发行版本。

| 系统 | wheel 架构 |
|---|---|
| Windows | x64 |
| macOS | Intel x64 / Apple Silicon ARM64，构建最低目标 11.0 |
| Linux | glibc 2.17+ x64 / ARM64 |

Python 发行版和可选依赖可能要求更新的系统。暂不支持 PyPy、free-threaded Python、Windows ARM64、32 位或 Alpine/musl。
缺少匹配 wheel 时，请使用上表的 Python/系统组合；不会回退下载 SDK 源码编译。

```bash
python -m venv .venv
```

macOS/Linux 激活：`source .venv/bin/activate`；Windows PowerShell 激活：`.\.venv\Scripts\Activate.ps1`。

macOS（包含蓝牙绑定与音频 Python 依赖）：

```bash
python -m pip install --only-binary=edu-glasses-host "edu-glasses-host[macos,audio]==0.5.0"
```

Windows/Linux（蓝牙 socket 路径及音频 Python 依赖）：

```bash
python -m pip install --only-binary=edu-glasses-host "edu-glasses-host[audio]==0.5.0"
```

WAV 解码另需系统 **libopus**；macOS 可用 `brew install opus`。缺少解码依赖时 SDK 保留 `.opusraw`，
以实际返回路径为准。只使用传感器、事件或拍摄控制时可不装 `[audio]`。
使用虚拟串口后备时再安装 `[serial]`；macOS 首次运行应允许终端/Python 宿主访问蓝牙。
Windows/Linux 的 Python 若不支持蓝牙 socket，使用第 7 节的虚拟串口后备方式。

需要运行 CLI 和本仓库示例时：

```bash
git clone https://github.com/Entertech/edu-glasses-demo.git
cd edu-glasses-demo
python -m pip install -e .
```

后面的 `examples/...` 命令均在 demo 仓库根目录运行；你的业务项目只需安装 SDK、复制需要的示例调用。

## 6. 运行第一个程序

先在 PC 的系统蓝牙设置配对 `EDU-Glasses-xxxx`。多台设备时指定从系统取得的设备地址。

```bash
python examples/sdk_quickstart.py --bt AA:BB:CC:DD:EE:FF
```

只有一台明确可用的已配对 EDU 设备时也可传 `--bt auto`。成功后会输出协议版本、能力、设备版本、
电量及传感器；程序退出时自动关闭连接。示例不会触发拍摄、录音或升级。

业务项目的最小程序：

```python
from edu_host import EduSession

with EduSession(bt="auto") as glasses:
    print("支持能力：", glasses.capabilities)
    info = glasses.info()
    print("版本：", info.fw_version_str)
    print("电量：", info.battery_level, "充电：", info.charging)
```

## 7. 连接与会话管理

`EduSession()` 构造时不连接，`with` 负责连接和关闭。一个 CTRL 连接由一个程序使用，
运行自己的应用前先退出占用连接的 CLI 或 Notebook。

- 一个会话内顺序调用。macOS 的连接、请求、等待和关闭均在进程主线程执行。
- 持续接收使用 `glasses.poll()` / `glasses.wait()`；不要用长时间的 `time.sleep()` 或阻塞输入代替收包。
- 回调只记录或排队，由主循环执行设备请求；不要在回调中重入 SDK。
- 本地按键录像独立于 PC 连接；SDK 发起的录像随所属连接清理。重连后不能接管旧操作或本地录像。

连接后用 `supports("VIDEO_CONFIG")` 等检查能力，缺少能力/必要通道会抛 `EduUnsupportedError`。
仅凭显示版本字符串不能确定设备具有全部功能。

虚拟串口后备示例：

```python
from edu_host import EduSession

with EduSession(ctrl_port="COM5", audio_port="COM6", img_port="COM7", ota_port="COM8") as glasses:
    print(glasses.info())
```

这些端口是系统为各蓝牙服务创建的虚拟串口，和眼镜的 USB 烧录/日志口用途不同。

## 8. 设备信息与传感器

```python
from edu_host import EduSession

with EduSession(bt="auto") as glasses:
    print(glasses.info())
    if glasses.supports("SENSORS"):
        data = glasses.sensors()
        print(data.als_raw, data.battery_temp_c, data.btcore_temp_c)
```

`battery_level` 单位为百分比；`als_raw` 是光敏原始计数，不能直接当作 lux。
两项温度分别为电池温度和蓝牙芯片结温，单位 ℃，不能直接当作环境温度。

## 9. 拍照录像与录像配置

| 需求 | 接口 | 成功含义 |
|---|---|---|
| 获取教学 JPEG | `photo()` | 完整 JPEG 已写入 PC，返回 `Path` |
| 保存照片原片 | `capture_saved_photo()` | 返回设备拍照控制结果；原片随后从媒体目录导出 |
| 开始/停止录像 | `video_start()` / `video_stop()` | 等待 RECORDING / DONE 控制状态；MP4 随后导出 |
| 观察设备拍摄 | `get_capture_state()` | 只读照片/视频来源与状态，不取得控制权限或文件身份 |

教学小图：`path = glasses.photo("lesson.jpg")`。相对文件名相对 `out_dir`；重复用同一文件名可能覆盖文件。
`record()` 是麦克风录音，视频录像使用 `video_start()`。

保存原片和录像的完整会话示例：

```python
from edu_host import EduSession

with EduSession(bt="auto") as glasses:
    print(glasses.capture_saved_photo())
    operation = glasses.video_start()
    try:
        glasses.wait(5)
    finally:
        print(glasses.video_stop(operation.operation_id))
```

`CaptureResult` 包含 `operation_id/kind/state/error`。操作 ID 用于当前连接的控制状态查询，
和导出时的媒体 ID 分别使用。DONE 不保证文件已出现在目录中；也不精确返回本次唯一媒体 ID。
从真实目录选取媒体，暂未发布时重新查询，不按最大 ID 或最新文件猜测归属。

录像配置需要 `VIDEO_CONFIG` 能力，支持设备级持久部分更新：

```python
from edu_host import EduSession

with EduSession(bt="auto") as glasses:
    print(glasses.get_video_config())
    config = glasses.set_video_config(
        resolution="1080p", orientation="portrait", max_duration_s=60,
    )
    print(config, config.sync_state.name)
```

档位为 `2k/1080p`、`landscape/portrait`、`30/60/180` 秒。省略字段保留原值，下次录像使用；
`video_start(timeout=20)` 的 timeout 是等待启动的时间，最长录像时长由配置决定。
profile 保存值、请求目标和 APPLIED 确认分别表达；只改时长不会凭空确认 ISP profile。
拍摄或 LAN 导入忙碌时拒绝写配置，低电、充电等保护仍由设备检查。

## 10. 通过 WiFi 导出照片和视频

先结束拍摄，再建立媒体导入上下文。PC 和眼镜应位于互通 LAN，PC 可以使用有线网络。
频段和安全类型以 `wifi_capabilities()` / `wifi_scan()` 的实际结果为准。

在本地创建 `wifi.json`，不要提交或打印真实凭据：

```json
{"ssid": "YOUR_WIFI_SSID", "security": "WPA2", "password": "YOUR_WIFI_PASSWORD"}
```

先查看真实媒体列表，再明确指定要下载的媒体 ID：

```bash
python examples/sdk_media_export.py --bt AA:BB:CC:DD:EE:FF --wifi-config wifi.json
python examples/sdk_media_export.py --bt AA:BB:CC:DD:EE:FF --wifi-config wifi.json --media-id 12 --output captures/export-01
```

示例默认只列目录；带 `--media-id` 才下载，允许重复指定多个 ID。示例不会删除眼镜原件。
自己的程序可使用下面的同一组接口：

```python
import json
from pathlib import Path
from edu_host import EduSession, WifiSecurity

credentials = json.loads(Path("wifi.json").read_text(encoding="utf-8"))
security = WifiSecurity[credentials["security"].upper()]
with EduSession(bt="auto") as glasses:
    print(glasses.media_capabilities())
    with glasses.media_import(credentials["ssid"], credentials["password"], security) as media:
        for item in media.list():
            print(item.media_id, item.kind, item.file.name, item.file.size)
        # 用户选择真实目录中的ID后调用：result = media.download(selected_id, "exports")
        # 显式批量导出：results = media.download_all("exports")
```

下载结果检查 `main_success`、`complete`、`files` 和 `errors`：

- 主文件成功且 `complete=True`：本条目的主文件与所需、可确认的伴随文件完整。
- 主文件成功但 `complete=False`：保留可用 JPEG/MP4，单独处理伴随数据缺失或失败。
- 主文件失败：本条目不能算导出完成；批量普通单项失败后仍继续其他项。

只操作有真实 ID 的照片/视频及登记伴随文件。MP4 是设备原片，不包含 App 后处理成片。
下载默认保留原件、不覆盖已有目标文件；整文件最多尝试 3 次，当前不支持 Range 续传。
CTRL 断连、取消或目录会话失效会结束所属导入，已下载成功的文件保留。

只有用户明确选择删除时才调用 `media.delete(selected_id)`。删除沿用设备能力，可能部分失败，
应核对返回结果；不要把自动删除放进普通下载示例。局域网媒体服务沿用当前公版可读、可删范围，
选择允许这一访问范围的网络。

## 11. 麦克风录音

```python
from edu_host import EduSession

with EduSession(bt="auto", out_dir="captures") as glasses:
    path = glasses.record_start("lesson.wav")
    try:
        glasses.wait(5)
    finally:
        stats = glasses.record_stop()
    print(path, stats.output_path, stats.seconds)
    print(stats.decoded_to_wav, stats.frames_written, stats.lost_packages, stats.decode_errors)
```

一次性调用为 `glasses.record("lesson.wav", seconds=5)`，返回实际输出路径。
音频为 16 kHz 单声道，WAV 需要 opuslib 和系统 libopus；缺依赖时保存 `.opusraw`。
没有有效帧时结束录音会报错，不能只根据传入的 `.wav` 后缀判断成功。
`is_recording` 用于本会话麦克风推流状态，不能替代视频录像查询。

## 12. 按键旋钮与状态事件

```bash
python examples/sdk_events.py --bt AA:BB:CC:DD:EE:FF --seconds 30
```

该示例只观察事件，不会收到按键就重复发送拍摄命令。

| 类型 | 开发者如何使用 |
|---|---|
| `ButtonEvent` / `KnobEvent` | 读取动作或旋钮方向，自定义应用逻辑；单击语义选 SINGLE，避免 SHORT/SINGLE 重复执行 |
| `DeviceCaptureState` | 观察存储照片/视频的来源、阶段、错误；教学图传仍使用 `ImgStateEvent` |
| `AudioRecordRequestEvent` | 开始意图在回调中排队，主循环准备文件并调用 `record_start()`；停止意图调用 `record_stop()` 完成文件 |
| `AudioStateEvent` / `ImgStateEvent` | 观察推流来源/错误和教学图片状态；状态事件不能替代完整文件结果 |

当前固件声明 `NATIVE_INPUT` 时，实体拍照/录像由设备直接执行，PC 断连仍可拍摄。
原始事件继续上报，应用不应再把同一个实体动作自动变成第二次 SDK 拍摄。
只读快照没有可控制的 operation，读取后不能据此接管本地录像。

录音需要 PC 接收程序；订阅事件本身不会自动开麦，也不提供离线录音。
处理开始意图应使用唯一文件名，过滤忙碌期间和过期意图（官方 demo 的期限为接收后 5 秒），
参考 [demo 的录音意图处理](../demo_cli.py)，保持回调只排队、主循环调用 SDK。
官方 demo 识别原生能力后关闭旧拍摄映射，旧固件保留原来的 PC 映射；升级固件前先升级 SDK/demo。

## 13. LED提示音重启与后续升级

通过 `set_led()`、`play_tone()` 控制反馈，枚举 `LedId/LedMode/LedColor/LedSpeed/Tone` 可从 `edu_host` 导入。
拍照/录像由固件自动管理反馈，手动 LED 可能被业务覆盖；`LedMode.OFF` 交回自动管理。
`reboot()` 受理后设备会重启并断开，待启动后重新连接。

已运行 EDU 的设备可使用 `glasses.ota(package_path, progress=callback)`；这是 SPP 升级接口，
和第 3 节首次通过 App 切换的流程分别使用。SDK OTA 接收维护者提供、匹配硬件的
**Looktech OTA 外层 `.bin`**；WPK 用于烧录工具，不能直接作为该接口的输入。
升级前结束拍摄、录音和导入；升级后重新核对版本、能力和实际结果。
进度回调参数为 `(stage, done, total)`；详细返回类型见 SDK 参考。

## 14. 集成到自己的应用与排障

将连接、轮询和请求放在同一顺序执行的主循环。界面和事件回调把任务放入队列，
由该主循环调用 SDK；不要在回调或任意工作线程中直接发同步请求。
退出时关闭会话，应用界面分别显示“连接状态”“操作状态”和“文件下载结果”。

| 现象/异常 | 处理方式 |
|---|---|
| 找不到设备/`AmbiguousGlassesError` | 确认 EDU 固件与系统配对；多设备时指定地址；关闭其他占用 CTRL 的程序 |
| No matching distribution found | 先确认该版本已发布；核对 CPython 版本、系统与架构，升级 pip；离线 wheel 也必须匹配平台 |
| `EduUnsupportedError` | 检查能力、匹配固件与必要通道，不重复发送不支持的请求 |
| `EduStatusError` | 读取 `cmd_id/status/data`，用 `edu_host.protocol.Status` 区分 BUSY、INVALID 等 |
| `CaptureTimeoutError` | 保留 `operation_id`，在当前有效连接中查询状态；超时不等于未执行，不能自动重拍 |
| `CaptureError` | 检查 `result.state/error`；UNKNOWN 不等于已经停止 |
| `MediaSessionError` / `MediaCancelled` | 退出当前上下文，明确重建新会话后再操作 |
| 只得到 `.opusraw` | 检查 opuslib 和系统 libopus，读取实际输出路径 |
| `OSError` / `ValueError` | 检查蓝牙、文件路径、输入参数等本地条件 |
| OTA 失败 | OTA 异常单独处理；不能仅捕获 `EduClientError` 代替全部 OTA 错误 |

示例可按具体异常到通用异常顺序捕获 `EduClientError` 子类，记录状态和操作 ID；
`AmbiguousGlassesError` 是独立异常，应单独捕获或明确指定设备地址。
不要记录网络密码或完整配网请求。SDK 超时不会自动重发拍照、录像开始等动作。

## 15. API与示例索引

| 要做的事 | SDK 入口或参考 |
|---|---|
| 建立/关闭连接 | `EduSession`、`connect()`、`close()` |
| 查询能力与设备 | `capabilities`、`supports()`、`info()`、`sensors()` |
| 拍摄/配置 | `photo()`、`capture_saved_photo()`、`video_start()`、`video_stop()`、`video_status()`、`get_video_config()`、`set_video_config()` |
| 收录音频/接收事件 | `record()`、`record_start()`、`record_stop()`、`add_event_listener()`、`poll()`、`wait()`、`events()` |
| 媒体目录与导出 | `media_capabilities()`、`media_import()`、`list/download/download_all/delete()` |
| 详细参数、返回值、异常 | [SDK 接口参考](API_REFERENCE.md) |
| 事件、返回类型与异常 | [SDK 接口参考](API_REFERENCE.md) |
| CLI 命令与管道运行 | [CLI 使用说明](CLI_GUIDE.md) |
| 最小连接示例 | [sdk_quickstart.py](../examples/sdk_quickstart.py) |
| 真实 ID 媒体导出 | [sdk_media_export.py](../examples/sdk_media_export.py) |
| 原始事件与拍摄快照 | [sdk_events.py](../examples/sdk_events.py) |
| 教学 Notebook | [图片、音频、传感器、旋钮和 WiFi 导出](../examples/notebooks/) |

普通应用使用 `edu_host.EduSession`。Notebook 中的 `edu_notebook` 是教学包装，其构造和部分返回值约定不同，
不应直接把包装类当成 SDK 公共类型使用。完整 API 名称以 SDK 参考为准。

## 16. 兼容性与已知限制

- 当前接入基线为 SDK 0.5.0、demo 0.3.0 及配套 EDU 原生输入固件；不同设备按实际能力协商。
- macOS + semi 已实测拍照、录像启停、实体停止 SDK 录像、断连归属及录音到 WAV。
  先前配套固件也验证过录像配置和 WiFi JPEG/MP4 导出；不能把历史结果当作本轮原件重测。
- Windows/Linux 保留连接路径，本轮没有对应实机验收；旋钮、配对、媒体/通话和完整保护矩阵也未全部实测。
- 首次通过 App 切换 EDU 的入口、固件发放和操作仍待补齐，尚未验证该完整升级路径。
- 只读拍摄终态、媒体目录发布、文件下载是不同阶段。原件须按真实媒体 ID 选择，SDK 不保证拍摄调用返回本次文件 ID。
- 快速交替使用存储原片和教学小图有失败历史，未作为稳定支持的连续采集流程验收。

已验证能力和尚未覆盖的组合以上述记录为准；本次二进制发行不新增设备能力，也不代表全部平台实机通过。
帮助中心链接核对于 2026-10-23；日常操作和 EDU SDK 能力分别以官方产品说明和本指南标注为准。
