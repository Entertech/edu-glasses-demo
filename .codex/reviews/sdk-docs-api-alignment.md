# SDK 使用文档与实现对账

- 审查目标：SDK 主教程混入 Demo 使用方式，以及方法表、调用示例与实现参数是否一致。
- 范围：两个仓库当前 main；SDK `187d839ca83e1a4751a5adf90aebc6795870e942`，Demo `2581d182b1450560d058d940d0551a0b83919c2d`。
- 审查轮次：2026-10-28 首次核对及修复闭环；下表位置保留首次审查时的基线行号，修复位置见后文。
- 验证：CodeGraph 查询，GlassesSession / MediaImport 方法 AST 签名清单，API 速查覆盖及参数名比对，已安装 SDK 的 inspect.signature / bind；未连接设备。

## 结论

首次审查发现 4 项文档对齐问题，现已全部修复。Demo README 直接承载完整 SDK 使用指南，原 SDK_GUIDE 只维护导航。
主线示例只依赖 SDK，Demo 脚本、CLI 与 Notebook 的安装和运行集中在 CLI_GUIDE，并由 README 链接。
概览表、API 速查和 Python 示例已对齐真实参数；CLI 的 video start/stop/status 只接受两个命令词，内部使用 SDK 默认 operation 和 timeout，文档已明确区分。

| ID | 严重级别 | 状态 | 代码位置 | 问题描述 | 影响 | 修复建议 | 验证方式 | 备注 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R001 | Minor | Fixed | SDK_GUIDE.md:154、169、288、348、365 | SDK 安装教程后，首个运行入口及媒体、事件章节优先给出 Demo 仓库脚本和脚本参数 | 只安装 SDK 的读者没有 examples 目录；容易混淆脚本的 --bt / --seconds / --media-id 与 SDK 方法参数，录音意图的 5 秒期限也属于 Demo 策略 | 主线先给完整 SDK Python 调用；Demo 命令、Notebook 辅助封装及策略移到单独的可选示例章节，保留必要的设备与回调约束 | SDK-only 环境下主教程不依赖 demo_cli、examples 或 glasses_notebook；Demo 章节标明克隆和安装前提 | 现文已提示 Demo 安装可选，但主线顺序仍混杂 |
| R002 | Minor | Fixed | SDK_GUIDE.md:232、249；API_REFERENCE.md:93、130、487；SDK session.py:269；demo_cli.py:449 | 概览表写 video_stop()，同章节示例却传 operation_id；概览未标明省略可选参数，也未突出与 CLI video stop 的区别 | 读者无法从表中了解 operation、timeout、默认值和省略 operation 的语义；可能把 Python 参数带入 CLI 而得到无效命令 | 表中给出 video_stop(operation=None, timeout=45.0)，说明 operation 来自 video_start 的 operation_id、默认用本会话最近录像；CLI 文档明确 video stop 不开放这两个参数 | 对照 AST / inspect 签名及 CLI len(args)==2 分支，无需修改运行接口 | API_REFERENCE.md:487 已正确写出参数，并非整个 SDK 都缺少参数说明 |
| R003 | Minor | Fixed | API_REFERENCE.md:478；SDK session.py:176 | 表中写 supports(name_or_bits)，实际公开参数名为 capability | 按表将 name_or_bits 作为关键字传入会产生 TypeError；位置参数调用不受影响 | 改为 supports(capability)，另用文字说明接受能力名称或位值 | inspect.signature(GlassesSession.supports).bind(None, name_or_bits="VIDEO") 失败，而 capability="VIDEO" 成功 | 这是实际参数名不一致，区别于 R002 的签名简写 |
| R004 | Minor | Fixed | API_REFERENCE.md:468–505、523；SDK session.py:242 | API 速查遗漏 get_capture_state()，正文示例和 SDK 实现均已存在 | 按速查表集成的开发者可能遗漏设备本地拍摄状态查询能力 | 增加 get_capture_state() -> DeviceCaptureState 行，标明只读、不取得录像控制权 | 将 GlassesSession 公共方法清单与速查区逐项比对；该方法是唯一未进入速查区的公共方法 | from_transports 已在表后说明，不计作遗漏 |

## 已确认的参数边界

- SDK：`video_start(timeout=20.0)`、`video_stop(operation=None, timeout=45.0)`、`video_status(operation=None)`。
- CLI：`video start`、`video stop`、`video status`，不直接接收 operation 或 timeout 参数。
- operation 是当前会话的录像控制操作 ID，不是媒体目录的媒体 ID；省略时使用当前会话最近的录像操作。
- SDK 的停止录像接口不能借设备本地状态快照接管实体按键发起的本地录像。

本轮未新增单元测试，未执行拍照、录像、停止录像或任何设备收发。

## 修复位置与闭环验证

- R001：[README 的 SDK 首个程序](../../README.md#6-运行第一个程序)直接保存为 app.py，媒体和事件示例直接调用 SDK；[Demo 使用说明](../../docs/CLI_GUIDE.md#安装并运行-demo)包含克隆、安装、CLI、三个脚本和五个 Notebook 的入口。README 不依赖 Demo 文件，也不把示例脚本参数当作 SDK 参数。
- R002：[README 的拍摄章节](../../README.md#9-拍照录像与录像配置)与 [API 拍摄章节](../../docs/API_REFERENCE.md#保存原片与录像)列出 operation/timeout、默认值、等待语义和控制归属；[CLI 参数说明](../../docs/CLI_GUIDE.md#存储照片录像与-wifi-原件导出)明确不接收这些 Python 参数。
- R003 / R004：[API 速查](../../docs/API_REFERENCE.md#api-速查)已使用 supports(capability)，并补入只读 get_capture_state()；与安装的 SDK 签名及公共方法清单核对通过。
- SDK 仓库 README 和 SDK_GUIDE 的公开指南链接已同步指向 Demo README；SDK README 中误称“从本仓库安装 Demo”的说明也已修正。

2026-10-28 验证结果：

- SDK 现有 55 项检查、Demo 现有 3 项检查均通过；两个仓库 compileall 通过。
- 6 份用户文档中 85 处本地及跨仓库链接、50 个标题锚点、24 段 Python 示例语法、95 处 SDK 调用参数绑定均通过；速查覆盖全部 36 个公开会话方法（含表后的 from_transports）。
- CLI 与 4 个示例的 --help、pip check、两个仓库 git diff --check 通过。
- PyPI 项目查询仍返回 404，指南明确发布前安装本地匹配 wheel，未把候选版本写成已发布。
- 未新增单元测试、未改运行接口、未重新构建 Cython wheel，未连接设备或执行拍摄/录音/OTA。本次验证不扩大历史实机结论。
