# AGENTS.md — edu-glasses-demo

本仓库维护`demo_cli.py`、教学Notebook、耳机示例及CLI操作技能。
SDK通过`pyproject.toml`固定PyPI版本安装；源码在独立SDK仓库维护，公开接口见`docs/API_REFERENCE.md`。

## 修改与验证

1. 所有眼镜SPP能力调用复用已安装的`edu_host`。SDK源码、协议解析和设备生命周期管理在SDK仓库修改。
2. CLI线程/macOS路径共用`run_session`；命令变化同步`HELP_TEXT`、README与`docs/CLI_GUIDE.md`，保留stdin管道调用。
3. SDK更新时修改固定发行版本，先验证独立环境安装。只复制演示调用，不添加邻接源码树到`sys.path`。
4. macOS的SDK请求在主线程顺序执行，等待使用`wait()/poll()`；按键回调只排队，由主循环执行拍摄。
5. 执行既有检查与入口验证：

```bash
python -m unittest discover -s tests -v
python demo_cli.py --help
python -m compileall -q demo_cli.py examples
```

需要CLI用法、串口后备或成功标志时读取[CLI完整使用说明](docs/CLI_GUIDE.md)。
连接、拍照、录音、传感器、事件、OTA与控制操作，可读取`.claude/skills/`对应技能。

## 设备操作

- 用户给出地址时使用明确设备；自动发现多台时请用户选定，不能猜地址或通道。
- 在系统蓝牙先配对。一个CTRL owner只运行一个demo/Notebook/应用；操作结束关闭连接。
- 管道触发异步操作后使用`wait <seconds>`等待完成；退出码0只表示会话结束，具体操作需核对状态和真实文件。
- 设备保护与错误按SDK原样处理。超时不自动重发拍照；实机验收须记录实际覆盖，离线语法通过不能视为实机通过。
- WiFi凭据仅从本地文件读取，下载媒体保存在忽略目录；提交中不包含凭据、抓取媒体或个人设备地址。
