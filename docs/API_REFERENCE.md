# Python SDK 接口参考

> 本文使用全量更名后的 SDK 0.6.0 / Demo 0.4.0；新 PyPI 项目发布前安装本地 SDK wheel。历史实机记录不等于本次更名已完成实机复验。

对应 SDK 0.6.0。安装与产品准备见[开发者指南](SDK_GUIDE.md)，CLI 见[CLI 使用说明](CLI_GUIDE.md)。
本页维护公共 API、返回类型、事件和错误契约。已安装 wheel 同时提供 `.pyi` 与 `py.typed`，供 IDE 提示。
SDK 实现由独立仓库维护；接入项目直接导入 `looktech_glasses_sdk`，无需实现仓库权限。

## 连接与能力发现

`GlassesSession(...)` 只构造对象，`with` 自动连接并在退出时关闭。需要较长连接等待时，
可显式管理：

```python
from looktech_glasses_sdk import GlassesSession

glasses = GlassesSession(bt="auto", out_dir="captures")
try:
    glasses.connect(timeout=40)
    print(glasses.hello_ack.proto_ver, glasses.capabilities)
finally:
    glasses.close()
```

一副眼镜只允许一个 CTRL host；运行自己的程序前应关闭占用连接的 CLI/Notebook。
`close()` 会清理所属媒体上下文、尝试停止录像/录音并关闭通道；清理可能等待设备确认，
失联时不能据此宣称远端资源已释放。重连后的会话不接管旧操作。

### 能力检查

先建立连接，再用 `supports("能力名")` 或 `capabilities` 判断。HELLO 能力与实际 ISP
能力是两层检查；新固件能力位齐全仍需 `media_capabilities()` 确认后端支持。

| HELLO 能力 | 对应调用 |
|---|---|
| `PHOTO` | `photo()`、`trigger_photo()`、`wait_photo()`，还需 IMG 通道 |
| `AUDIO_STREAM` | `record()`、`record_start()`、`record_stop()`，还需 AUDIO 通道 |
| `SENSORS` | `sensors()` |
| `INPUT_EVENTS` | 按键/旋钮事件 |
| `NATIVE_INPUT` | 设备原生拍照/录像按键及 PC 录音请求，原始事件仅观察 |
| `DEVICE_CAPTURE_STATE` | 只读查询和观察设备最新拍摄状态 |
| `CONTROL` | `set_led()`、`play_tone()`、`reboot()` |
| `WIFI` | `wifi_capabilities()`、`wifi_scan()`、配网和状态查询 |
| `SAVED_PHOTO` + `MEDIA_CATALOG` | `capture_saved_photo()` |
| `VIDEO_CONFIG` | `get_video_config()`、`set_video_config()` |
| `VIDEO` + `MEDIA_CATALOG` | `video_start()`、`video_stop()`、`video_status()` |
| `MEDIA_CATALOG` + `WIFI` | `media_import()`；真实媒体能力由 ISP 查询确认 |

OTA 通过独立服务发现，没有专门的 HELLO OTA 能力位。能力或必要通道缺失时 SDK
抛出 `GlassesUnsupportedError`，不要通过固件版本显示字符串推断所有能力。

### 平台、线程与持续收包

- macOS 的连接、请求、`poll()`、等待和关闭都在**进程主线程**调用；SDK 自行管理
  原生蓝牙通道。Windows/Linux 默认 RFCOMM 通道为 CTRL=6、AUDIO=5、IMG=4、OTA=7；
  macOS 通过 SDP 查询。通常不需要修改通道参数。
- 一个会话内顺序调用 SDK。空闲、录音或等事件时使用 `glasses.wait(seconds)` 或
  `glasses.poll(0.05)`，避免用 `time.sleep()` 或阻塞式 `input()` 长时间停住收包。
- `GlassesSession` 的事件/图片回调在调用者线程分发。回调只做记录或排队，不在回调中
  发设备请求；GUI/其他线程将请求排队，由 SDK 所在线程执行。
- SDK 已处理长 HTTP 下载期间的蓝牙轮询，应用不需要自行将媒体下载移到另一个
  SDK 调用线程。

虚拟串口后备可用
`GlassesSession(ctrl_port="COM5", audio_port="COM6", img_port="COM7", ota_port="COM8")`。
这些应是各 SPP 服务对应的蓝牙虚拟串口，不是整机烧录/日志 USB 串口。

## 信息与传感器

```python
from looktech_glasses_sdk import GlassesSession

with GlassesSession(bt="auto") as glasses:
    info = glasses.info()
    print(info.fw_version_str, info.battery_level, info.charging)
    if glasses.supports("SENSORS"):
        data = glasses.sensors()
        print(data.als_raw, data.battery_temp_c, data.btcore_temp_c)
```

`battery_level` 为百分比；`als_raw` 是光敏原始计数，**不是 lux**。
`battery_temp_c` 和 `btcore_temp_c` 分别是电池温度和蓝牙芯片结温，单位 ℃，
不能当作环境温度。`info()`/`sensors()` 默认请求超时均为 5 秒。

## 照片与录像

### 先选择所需接口

| 目的 | 调用 | 传输/保存位置 | 返回成功的含义 |
|---|---|---|---|
| SPP 图片分析、小图回传 | `photo()` | JPEG 经 IMG SPP 传到 PC | 完整 JPEG 已写入 PC 文件 |
| 保存原片 | `capture_saved_photo()` | 原片保存在眼镜，随后 WiFi 导出 | 公版拍照控制状态 DONE |
| 录制视频 | `video_start()` / `video_stop()` | MP4 保存在眼镜，随后 WiFi 导出 | 公版 RECORDING / DONE 控制状态 |

`photo()` 不等于保存原片；麦克风 `record()` 也不等于录像。拍摄灯效由固件公共
能力管理，不需要额外调用 `set_led()` 模拟。

### SPP JPEG 小图 回传

```python
from looktech_glasses_sdk import GlassesSession

with GlassesSession(bt="auto", out_dir="captures") as glasses:
    path = glasses.photo("photo.jpg", timeout=30)
    print("已落盘：", path)
```

返回 `pathlib.Path`。相对文件名相对会话 `out_dir`，绝对文件名按绝对路径保存。
传入固定文件名可能覆盖该文件，重复采集应使用不同名称或让 SDK 自动命名。
异步拆分调用为 `trigger_photo(filename)` 后 `wait_photo(timeout=30)`；ACK 或
`ImgStateEvent` 的 DONE 不能替代完整 JPEG 落盘判定。

### 保存原片与录像

```python
from looktech_glasses_sdk import GlassesSession, GlassesUnsupportedError

with GlassesSession(bt="auto") as glasses:
    required = ("SAVED_PHOTO", "VIDEO", "MEDIA_CATALOG")
    if not all(glasses.supports(name) for name in required):
        raise GlassesUnsupportedError("当前固件不支持存储拍照/录像")
    print("实际媒体能力：", glasses.media_capabilities())
    photo = glasses.capture_saved_photo(timeout=45)
    print("照片控制结果：", photo.operation_id, photo.state.name)

    video = glasses.video_start(timeout=20)
    try:
        glasses.wait(5)
    finally:
        stopped = glasses.video_stop(video.operation_id, timeout=45)
        print("视频控制结果：", stopped.state.name)
```

返回 `CaptureResult(operation_id, kind, state, error)`，`kind` 为 1 照片、2 视频。
`operation_id` 仅用于当前 CTRL owner 的控制状态查询，**不是媒体 ID**；同种媒体只
保留最近一个操作状态。`media_status(photo.operation_id)` 查询照片或视频，
`video_status(video.operation_id)` 查询视频；省略视频 ID 时使用本会话最近的录像操作。

`CaptureState` 包含 STARTING、RECORDING、STOPPING、DONE、FAILED、UNKNOWN。
公版 DONE/RECORDING 不保证原件已发布、首帧已写入，也不会精确返回本次拍摄的媒体 ID。
导出时从真实媒体列表选择；暂未出现时重新查询，不能按“最新文件”或最大 ID 猜测归属。
UNKNOWN/超时不代表没有拍摄，SDK 不自动重拍；状态处理见[错误处理](#错误处理)。

### 录像配置

需要声明 `VIDEO_CONFIG` 的新开发者固件。分辨率是公版档位 `2k` / `1080p`，方向为
`landscape` / `portrait`，最长时长为公版App的30 / 60 / 180秒，不接受任意宽高或秒数。
配置保存在设备上，重启保留，下次录像使用；它不是某一次调用的临时参数。
档位名称沿用公版，不能据此假设16:9画幅；本轮semi导出的原片尺寸如下：

| 档位 | 横屏 | 竖屏 |
|---|---|---|
| `2k` | 2880×2160 | 2160×2880 |
| `1080p` | 1440×1080 | 1080×1440 |

```python
from looktech_glasses_sdk import GlassesSession

with GlassesSession(bt="auto") as glasses:
    print("原配置：", glasses.get_video_config())
    config = glasses.set_video_config(
        resolution="1080p", orientation="portrait", max_duration_s=60,
        timeout=45,
    )
    print(config.resolution.name, config.orientation.name, config.max_duration_s)
    print("同步状态：", config.sync_state.name)
    # 部分更新：保留分辨率、方向和既有防抖参数
    print(glasses.set_video_config(max_duration_s=30))
```

也可传 `VideoResolution.RES_2K/RES_1080P` 和 `VideoOrientation.LANDSCAPE/PORTRAIT`
枚举，均从 `looktech_glasses_sdk` 导入。`get_video_config()` 返回 `VideoConfig`：

| 字段 | 含义 |
|---|---|
| `resolution` / `orientation` | BT持久配置中的profile；未确认时不能断言ISP已经生效 |
| `max_duration_s` | BT保存的最长秒数，下次开始录像时传给ISP |
| `requested_resolution` / `requested_orientation` | 当前最新请求目标，可能尚在排队/生效中 |
| `sync_state` | `VideoConfigState.UNCONFIRMED` / `PENDING` / `APPLIED` |

保存和生效沿用公版设置及ISP profile同步流程。SDK设置分辨率/方向时默认等待真实回读
确认，返回APPLIED；只设置时长时保存后返回，profile状态可能仍是UNCONFIRMED/PENDING。
查询不会把未确认状态伪装成功；APPLIED仅指profile确认，不是对录像文件尺寸或时长的测量。

拍照、录像启动/录制/停止和LAN导入期间设置返回BUSY；查询仍可用。录像继续遵守公版
充电/低电保护；当前semi充电时会拒绝开始录像，充电状态允许LAN导出，不能将两者混同。
超时后可能仍在处理，
保留同一连接继续`get_video_config()`查询，不自动重发。设备断连不会撤销已经受理的持久
设置；新连接可以查询当前设备配置，但不会接管旧录像operation。

旧`video_start()`无需新增参数；它使用设备配置。`video_start(timeout=20)`的timeout是
等启动状态的超时，`set_video_config(timeout=45)`是等profile生效的超时，两者均不表示
录像最长时长。旧固件缺少bit9时新配置接口抛`GlassesUnsupportedError`，原拍摄接口保持可用。

## 麦克风录音

```python
from looktech_glasses_sdk import GlassesSession

with GlassesSession(bt="auto", out_dir="captures") as glasses:
    actual_path = glasses.record_start("lesson.wav")
    try:
        glasses.wait(5)
    finally:
        stats = glasses.record_stop()
    print(actual_path, stats.output_path, stats.seconds)
    print(stats.decoded_to_wav, stats.frames_written, stats.lost_packages)
```

一次性调用为 `glasses.record("lesson.wav", seconds=5)`，返回实际文件路径。
音频为 16 kHz 单声道；缺少 opuslib/libopus 时保存 `.opusraw`，以实际返回路径为准，
不要只根据传入的 `.wav` 后缀判断格式。没有有效帧时 `record_stop()` 会报错。
`AudioStateEvent.source_name` 表示 MIC/CALL，是否切换或暂停沿用固件行为。
`is_recording` 指麦克风推流状态；录像状态使用 `video_status()`。

## 事件监听与自定义

`GlassesSession` 只分发事件，不自动把按键绑定到拍摄。应用可以自行决定每个事件对应的
业务动作；声明 NATIVE_INPUT 时固件已执行本地拍照/录像，不应重复发命令。
物理按键包含的本地音量/通话/配对行为同样保留。

| 类型 | 主要字段 | 用途 |
|---|---|---|
| `ButtonEvent` | `btn`、`action`、`btn_name`、`action_name` | AI、CAPTURE、MEDIA 键的动作 |
| `KnobEvent` | `direction_name`、`delta_x`、`delta_y` | 旋钮/滑动输入 |
| `AudioStateEvent` | `running`、`source_name`、`err` | 音频运行、来源和错误 |
| `ImgStateEvent` | `capture_evt_name`、`error` | SPP 图传状态，不能替代完整文件结果 |

短按会出现 PRESS、RELEASE、SHORT、SINGLE；需要单击语义时只处理 SINGLE，避免
SHORT/SINGLE 重复触发。长按还会有 REPEAT、LONG_RELEASE。枚举 `ButtonId`、
`KeyAction` 从 `looktech_glasses_sdk.protocol` 导入，完整动作见维护者提供的详细协议。

下面的示例将右侧单击转换为应用请求，由回调外的主循环处理。示例只打印业务请求，
开发者可在标记处接入自己的功能：

```python
from queue import Empty, Queue
from looktech_glasses_sdk import ButtonEvent, GlassesSession, KnobEvent
from looktech_glasses_sdk.protocol import ButtonId, KeyAction

requests = Queue()

def on_event(event):
    if isinstance(event, ButtonEvent):
        if event.btn == ButtonId.CAPTURE and event.action == KeyAction.SINGLE:
            requests.put("right_single")
    elif isinstance(event, KnobEvent):
        requests.put(("knob", event.direction_name, event.delta_x))

try:
    with GlassesSession(bt="auto") as glasses:
        glasses.add_event_listener(on_event)
        while glasses.is_connected:
            glasses.poll(0.05)
            try:
                request = requests.get_nowait()
            except Empty:
                continue
            print("处理应用请求：", request)  # 在此处顺序调用需要的 SDK 方法
except KeyboardInterrupt:
    pass
```

一次性收集可用 `glasses.events(10)`，它等待 10 秒后返回事件列表，不是流式生成器。
图片回调为 `add_image_listener(callback)`，参数 `(path, CompletedImage)`，完整图片已落盘
后触发。以上约束针对 `GlassesSession`；直接使用旧底层 `GlassesClient` 时线程模型不同。

参考 CLI 按能力区分原生与旧固件：有 NATIVE_INPUT 时仅观察实体拍摄事件，避免重复发命令；
旧固件仍将 SINGLE/LONG/PRESS 映射为拍摄请求，并处理去重及配对窗口。复用时参照
[`CaptureButtons`](https://github.com/Entertech/looktech-glasses-demo/blob/main/demo_cli.py)，不要把同步请求直接放进事件回调。
当前原生固件的实体拍照/录像不依赖 PC 在线；SDK 发起的录像仍随所属连接断开清理。

## WiFi 与媒体导出

### 网络与凭据

SPP 负责配网、控制和查询真实媒体身份，JPEG/MP4 原件通过 WiFi LAN HTTP 下载。
PC 与眼镜应处于互通的局域网，PC 可用有线网络，不需要手机 App 或互联网。
实际频段及安全类型以硬件和 `wifi_capabilities()` / `wifi_scan()` 结果为准。

本地创建 `wifi.json`，填写实际网络信息，不提交到版本库：

```json
{
  "ssid": "YOUR_WIFI_SSID",
  "security": "WPA2",
  "password": "YOUR_WIFI_PASSWORD"
}
```

`security` 取 `WifiSecurity` 枚举名称：OPEN、WEP、WEP_SHARED、WPA、WPA2、WPA3，
实际可用值由设备返回；开放网络使用 OPEN 和空密码。SSID 为 1–32 个 UTF-8 字节、
密码最多 64 字节，均不能含 NUL，安全类型和密钥还需后端校验。不要打印完整凭据。

### 列出并下载原件

```python
import json
from pathlib import Path
from looktech_glasses_sdk import GlassesSession, WifiSecurity

credentials = json.loads(Path("wifi.json").read_text(encoding="utf-8"))
security = WifiSecurity[credentials["security"].upper()]

def on_progress(media_id, filename, received, total):
    print(media_id, filename, received, "/", total)

with GlassesSession(bt="auto") as glasses:
    print("实际媒体能力：", glasses.media_capabilities())
    with glasses.media_import(credentials["ssid"], credentials["password"], security) as media:
        items = media.list()
        for item in items:
            print(item.media_id, item.kind, item.file.name, item.file.size)
        # 批量导出本次列表中的全部已索引媒体；不会自动删除设备原件
        results = media.download_all("exports", progress=on_progress)
        for result in results:
            print(result.media.media_id, result.main_success, result.complete)
            print("文件：", result.files, "问题：", result.errors)
```

`media_import()` 创建上下文，进入 `with` 时才执行配网、启动服务并查询目录。
同一会话只允许一个媒体上下文；拍照/录像与导入应顺序执行，先停止录像再导出。
上下文有效时 SDK 在空闲约 30 秒后发 HTTP 活动保活，退出或 CTRL 失效时清理所属
HTTP/STA；停止未确认时设备可能暂时保持 BUSY。不要另外启动重复配网或保活循环。

`media.list()` 返回 `tuple[MediaItem, ...]`，只包含真实 ID 的照片/视频；没有 ID 的
文件不会列出，也不允许路径回退。媒体身份按 `catalog_id + media_id` 区分，
`revision` 用于检查描述变化；不要跨目录或跨会话盲用缓存条目。列表不是原子快照。

单项下载使用 `media.download(item, "exports")`，也支持当前目录中的整数
`media_id`。传入 `MediaItem` 可以检查所选描述是否变化。相对导出目录相对进程当前
工作目录，独立于 `GlassesSession.out_dir`。选择集合应由业务决定，不能从操作 ID 推算媒体 ID。

### 结果、重试和取消

| 结果 | 正确处理 |
|---|---|
| `main_success=True, complete=True` | 主文件和可确认所需伴随文件均成功，使用 `files` 中路径 |
| `main_success=True, complete=False` | 主文件可用；伴随数据缺失、下载失败或无法确认关系，读取 `errors` |
| `main_success=False` | 主文件未成功；本项失败，不能当成导出完成 |

视频导出的是设备 MP4 原件及可确认登记的 gyro 等伴随文件，不包含 App 后处理或
防抖成片。公版 HTTP 列表退为 legacy 时仍可通过 SPP 列出真实媒体 ID，但可能无法
确认视频伴随关系；此时保留可用 MP4 并报告 `complete=False`，不猜同名伴随文件。

SDK 校验 HTTP 状态、Content-Length、实际字节数，并在下载前后重核媒体描述；
通过临时文件提交，默认不覆盖已有文件。每个文件最多尝试 3 次，失败从头下载，
不支持 Range 续传或设备内容哈希校验；不能将本地计算哈希当成端到端身份校验。
已成功导出过同名文件时，换一个导出目录或由应用明确处理已有文件。

`download_all()` 固定调用时的选择集合，普通单项失败后继续并逐项返回结果；
CTRL 失效、取消、目录/所属会话失效会抛出会话级错误并终止，已经提交的文件保留。
进度回调参数为 `(media_id, filename, received, total)`，在调用者线程分发，
重试时 `received` 会重新从头累计，不要在其中重入 SDK。

需要取消时调用 `media.cancel()`，随后下载抛 `MediaCancelled` 并结束所属会话；
也可在进度回调中设置取消。取消后的上下文不能继续使用，应退出 `with` 再重新建立。

### 显式删除

下载默认保留原件。只有应用明确决定删除时才调用 `media.delete(item)` 或
`media.delete(media_id)`。下面仅定义函数，不在导出示例中自动调用：

```python
from looktech_glasses_sdk import MediaImport, MediaItem

def delete_selected(media: MediaImport, item: MediaItem):
    result = media.delete(item)
    print(result.media_id, result.deleted, result.already_absent)
    return result
```

删除沿用公版按 ID 删除及登记伴随文件的范围，不保证事务原子性；失败需重新核实，
不能因列表里消失就断言整组文件已删除。`already_absent=True` 表示实际删除端点返回
不存在。SDK 不提供无 ID、音频或任意路径删除。LAN 服务继承公版可读、可删边界，
没有额外 PC token，部署时应选择允许这一访问范围的网络。

### 单独配网和诊断

仅诊断网络时，可顺序使用 `wifi_capabilities()`、`wifi_scan(timeout=30)`、
`wifi_connect(ssid, password, security, timeout=70)`、`wifi_status()`、
`wifi_disconnect()`。`wifi_connect()` 返回 `WifiStatus`，等待 CONNECTED/SERVING；
单独 CONNECTED 不代表 HTTP 已启动。导出优先使用 `media_import()` 管理完整生命周期。
`wifi_disconnect()` 表示停止请求已受理，实际终态用 `wifi_status()` 确认。

## 设备控制与升级

### LED、提示音、重启

```python
from looktech_glasses_sdk import GlassesSession, LedColor, LedId, LedMode, LedSpeed, Tone

with GlassesSession(bt="auto") as glasses:
    glasses.set_led(LedId.INNER, LedMode.BLINK, LedColor.GREEN, LedSpeed.NORMAL)
    glasses.play_tone(Tone.CLICK)
    glasses.wait(1)
    glasses.set_led(LedId.INNER, LedMode.OFF)
    # 需要重启时单独调用 glasses.reboot()；受理后约 0.5 秒断开
```

外灯不支持颜色选择。手动 LED 是尽力设置，配对/拍摄等业务可覆盖它；OFF 将灯交回
固件自动管理。拍照/录像正常灯效应直接由拍摄能力驱动。提示音用 `Tone` 枚举或
`play_tone("click")`，设备不接受的编号会返回错误。

### OTA

`glasses.ota(package_path, progress=callback)` 使用独立 OTA SPP 服务。升级输入必须是
固件维护者提供、与设备匹配的 **Looktech OTA 外层 `.bin`**，不是 `.wpk` 或 BT 内包。
先停止录像/录音、等待拍照完成并退出媒体导入，再升级；升级期间不调用其他设备能力。

```python
from looktech_glasses_sdk import GlassesSession

def upgrade(glasses: GlassesSession, package_path):
    def progress(stage, done, total):
        print(stage, done, total)
    result = glasses.ota(package_path, progress=progress)
    print(result)
    return result
```

升级包先在本地校验，再开 OTA 通道；返回 `UpdateResultResponse`。升级完成可能重启
并断开连接，待完整启动后重新连接检查能力与版本。`ota()` 没有通用 `timeout` 参数；
通常保留默认分块大小和间隔。不要将历史基础固件包当作当前扩展能力的升级包。

## 错误处理

| 异常 | 可读取的信息 | 应用处理 |
|---|---|---|
| `GlassesUnsupportedError` | 缺少能力或通道 | 提示匹配固件/通道，不重复发送同一请求 |
| `GlassesStatusError` | `cmd_id`、`status`、`data` | 用 `looktech_glasses_sdk.protocol.Status` 区分 BUSY/INVALID/NOT_READY/ERROR；待条件恢复后由业务决定重试 |
| `CaptureTimeoutError` | `operation_id` | 保留操作 ID 查询，不能自动重拍或重复开录像 |
| `CaptureError` | `result`，含 UNKNOWN/FAILED | 根据真实状态处理；UNKNOWN 不等于已经停止 |
| `GlassesTimeoutError` | 请求或图片等待超时 | 可能已执行；先查询或核实，不盲重发 |
| `WifiError` | `code` | 核实网络、安全类型及后端错误，按设备返回的真实错误码处理 |
| `MediaError` | 单项操作问题 | 检查结果/描述；已成功文件保留 |
| `MediaSessionError` / `MediaCancelled` | 所属会话失效或取消 | 结束上下文，明确重新建立后再操作 |
| `AmbiguousGlassesError` | 多设备歧义 | 指定蓝牙地址 |
| `OSError` / `ValueError` | 连接/本地文件问题、无效参数 | 检查系统状态、路径、输入 |
| `OTAError` 及其子类 | 独立 OTA 错误 | 单独处理，不能只捕获 `GlassesClientError` |

异常均可从 `looktech_glasses_sdk` 导入；`CaptureTimeoutError` 继承 `GlassesTimeoutError`，
`MediaCancelled` 继承 `MediaSessionError`，后者继承 `MediaError`，这些异常最终继承
`GlassesClientError`。因此先捕获具体异常，再捕获通用异常。
多设备歧义的 `AmbiguousGlassesError` 则是独立的 `RuntimeError` 子类，需要单独捕获或明确指定设备地址。

保留拍照超时的操作 ID，例如：

```python
from looktech_glasses_sdk import CaptureError, CaptureTimeoutError, GlassesClientError, GlassesSession

with GlassesSession(bt="auto") as glasses:
    try:
        result = glasses.capture_saved_photo()
        print(result)
    except CaptureTimeoutError as exc:
        print("结果未知，保留 operation_id：", exc.operation_id)
        # 后续在同一有效 CTRL 会话查询 glasses.media_status(exc.operation_id)
    except CaptureError as exc:
        print("真实拍摄状态：", exc.result.state.name, exc.result.error)
    except (GlassesClientError, OSError) as exc:
        print("本次请求失败：", exc)
```

实际应用还应在连接这一层处理错误。设备返回 BUSY 时无需绕过共享准入；先完成或
停止当前业务。记录错误可启用标准库 `logging`，不要记录网络密码或完整配网帧。

## API 速查

下表只列公共接入接口；不建议直接依赖 `_request`、`_client` 等私有实现。所有方法
顺序调用；未标明类型的详细字段见上文及对应数据类。

| 入口 | 返回 / 作用 |
|---|---|
| `GlassesSession(bt="auto", *, out_dir="captures", ...)` | 创建会话，构造不连接；串口/通道参数见连接章节 |
| `connect(timeout=6)` / `close()` | 返回当前会话 / 关闭所属资源 |
| `is_connected` / `hello_ack` | 连接状态 / `HelloAck`，关闭后 ack 为 None |
| `capabilities` / `supports(name_or_bits)` | 能力名称元组 / bool，需已连接 |
| `info(timeout=5)` / `sensors(timeout=5)` | `DeviceInfo` / `SensorData` |
| `photo(filename=None, timeout=30)` | `Path`，完整SPP JPEG 小图 已写入 PC |
| `trigger_photo(filename=None, timeout=5)` / `wait_photo(timeout=30)` | 受理 `Response` / 完整图片 `Path` |
| `capture_saved_photo(timeout=45)` | `CaptureResult`，原片保存的公版控制状态 |
| `media_status(operation)` | `CaptureResult`，同 owner 最近操作的当前状态 |
| `get_video_config()` | `VideoConfig`，保存值、请求目标及profile同步状态 |
| `set_video_config(*, resolution=None, orientation=None, max_duration_s=None, timeout=45)` | 部分设置，返回`VideoConfig`；无字段或非法值报错 |
| `video_start(timeout=20)` | `CaptureResult`，等待 RECORDING 或实际终态 |
| `video_stop(operation=None, timeout=45)` / `video_status(operation=None)` | `CaptureResult`；省略 ID 使用最近录像操作 |
| `record(filename, seconds, timeout=5)` | 实际音频文件 `Path` |
| `record_start(filename="record.wav", timeout=5)` / `record_stop(timeout=5)` | 实际路径 / `AudioStats` |
| `is_recording` | 麦克风推流状态，不代表视频录像 |
| `add_event_listener(callback)` / `add_image_listener(callback)` | 注册类型化回调 |
| `poll(seconds=0.05)` / `wait(seconds)` / `events(seconds)` | 本次事件列表 / 持续收包 / 时间窗口事件列表 |
| `wifi_capabilities()` / `wifi_scan(timeout=30)` | `WifiCapabilities` / `tuple[WifiNetwork, ...]` |
| `wifi_connect(ssid, password="", security=WifiSecurity.WPA2, timeout=70)` | `WifiStatus`，已入网 |
| `wifi_status()` / `wifi_disconnect()` | `WifiStatus` / 请求停止，实际终态需查询 |
| `media_capabilities()` | `MediaCapabilities(schema_version, catalog_id, features)`，查询真实 ISP |
| `media_import(ssid, password="", security=WifiSecurity.WPA2)` | `MediaImport`，使用上下文管理 |
| `media.list()` | `tuple[MediaItem, ...]` |
| `media.download(media, directory="captures", progress=None)` | 单项 `DownloadResult`；media 为 ID 或 `MediaItem` |
| `media.download_all(directory="captures", progress=None)` | `tuple[DownloadResult, ...]` |
| `media.delete(media)` | `DeleteResult`，显式设备删除 |
| `media.cancel()` / `media.close()` | 取消在途下载 / 结束导入并请求清理 |
| `set_led(led, mode, color=LedColor.WHITE, speed=LedSpeed.NORMAL, timeout=5)` | 控制 `Response` |
| `play_tone(tone=Tone.CLICK, timeout=5)` / `reboot(timeout=5)` | 控制 `Response` |
| `ota(filename, progress=None, chunk_size=512, packet_interval_ms=10)` | `UpdateResultResponse` |

已有自定义传输实现可用 `GlassesSession.from_transports(ctrl, audio=None, image=None,
ota=None, out_dir="captures")`；普通接入优先使用蓝牙地址或串口参数。


## 原生按键与状态观察（0.4.0）

新版开发者固件默认在设备侧处理拍照键：单击存储拍照，长按录像，录像中再按停止。
PC 断开不影响本地拍摄；SDK 发起的录像仍随所属连接断开而停止。旋钮音量、媒体及通话
按键沿用公版。原始 `ButtonEvent`/`KnobEvent` 仍可订阅，但不要再把同一个拍摄事件自动映射成 SDK 拍摄命令。

```python
from looktech_glasses_sdk import GlassesSession, DeviceCaptureState, AudioRecordRequestEvent

with GlassesSession(bt="auto") as glasses:
    print("原生按键:", glasses.supports("NATIVE_INPUT"))
    if glasses.supports("DEVICE_CAPTURE_STATE"):
        state = glasses.get_capture_state()
        print(state.photo.source.name, state.photo.state.name)
        print(state.video.source.name, state.video.state.name)
    glasses.add_event_listener(print)  # 回调只观察/排队，不能重入 SDK
    glasses.wait(30)
```

`get_capture_state() -> DeviceCaptureState` 和同类型事件包含 `photo`、`video` 两个
`DeviceCaptureEntry(kind, source, state, error)`，枚举为 `CaptureKind`、`CaptureSource`、`CaptureState`。
只读快照观察存储照片和视频，SPP JPEG 小图继续使用 `ImgStateEvent`。每类保留最新终态，重启后为 NONE/IDLE；
没有可控制的 operation，不能据此
调用 `video_stop()` 接管本地录像，也不证明文件已发布。原件仍从真实 ID 媒体目录选择下载。

录音双击按公版双击配置产生 `AudioRecordRequestEvent(start=True)`，固件此时不开麦。
应用若支持此动作，应在回调中排队，在主循环调用 `record_start(唯一文件名)`，该方法先准备
接收端再发送 AUDIO_START；`start=False` 时对正在录制的 SDK 会话调用 `record_stop()` 完成文件。
流属于接收 PC，断连清理；没有接收程序不做离线录音。录音继续沿用 SDK 接收流的充电、重试和静音提示策略。
事件的 `received_at` 是接收帧时的本机单调秒数，应用应拒绝忙碌期间或已过期的开始意图。
官方 demo 已实现该接收流程；
SDK 本身不会因为订阅事件自动录音。AI/翻译完整业务仍需应用自行实现。

配套 demo 在 NATIVE_INPUT 存在时关闭旧拍摄映射，在旧固件上保留原映射。
请先升级 SDK/demo，再更新原生输入固件；旧 demo 可能重复拍摄。

2026-10-23 后续 semi 实测已覆盖实体拍照、录像启停及灯效、实体停止 SDK 录像、本地/SDK
断连归属、录音意图到 PC WAV 收尾；繁忙仅覆盖录像中写配置的 BUSY 分支。旋钮、配对、
充电保护和媒体/通话等剩余项未完成，用户选择暂不继续。本轮新增照片/视频未重验导出原件。
这些是既有固件的实机结果，二进制 SDK 发行不扩大验收范围。
