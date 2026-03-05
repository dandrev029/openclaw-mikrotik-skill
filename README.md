# MikroTik RouterOS Skill for OpenClaw

通过 API 连接和管理 MikroTik RouterOS 设备的 OpenClaw Skill。

## 功能

- ✅ 查看设备状态（系统信息、CPU、内存、存储）
- ✅ 查看防火墙规则（filter、NAT、mangle）
- ✅ 查看网络配置（接口、IP 地址、路由、DNS）
- ✅ 执行自定义 RouterOS 命令
- ✅ 支持多设备连接

## 安装

### 方法 1: 通过 ClawHub（推荐）

```bash
npx clawhub install mikrotik
```

### 方法 2: 手动安装

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/openclaw-mikrotik-skill.git
cd openclaw-mikrotik-skill

# 复制到 OpenClaw skills 目录
cp -r mikrotik /usr/lib/node_modules/openclaw/skills/

# 重启 OpenClaw Gateway
openclaw gateway restart
```

## 配置

在 `TOOLS.md` 中添加 MikroTik 设备信息：

```markdown
### MikroTik 设备

- **office**: 192.168.1.1, admin, 空密码
- **home**: 192.168.88.1, admin, yourpassword
```

## 用法

### 自然语言命令

```
查看 mikrotik 设备状态
mikrotik 防火墙配置
检查路由器运行情况
查看网络接口
在 mikrotik 上执行 /system/resource/print
```

### 命令行工具

```bash
cd mikrotik-api
python3 cli.py 10.0.5.4 status      # 查看设备状态
python3 cli.py 10.0.5.4 firewall    # 查看防火墙
python3 cli.py 10.0.5.4 interfaces  # 查看接口
python3 cli.py 10.0.5.4 routes      # 查看路由
```

### Python API

```python
from mikrotik_api import MikroTikAPI, QuickCommands

with MikroTikAPI('10.0.5.4') as api:
    api.login()
    quick = QuickCommands(api)
    quick.print_status()
```

## 示例输出

```
📡 MikroTik RouterOS 设备状态
============================================================
  设备名：OFFICE
  版本：7.21.2 (stable)
  运行时间：1w2d9h9m39s
  CPU: MIPS 1004Kc V2.15 @ 880MHz
  CPU 负载：1%
  内存：61.6MB / 256.0MB
  存储：3.6MB / 16.0MB
============================================================
```

## 依赖

- Python 3.6+
- OpenClaw 2026.3.2+
- MikroTik RouterOS API 已启用（默认端口 8728）

## 注意事项

1. 确保 RouterOS 的 API 服务已启用（`/ip/service/print` 查看）
2. 默认端口 8728，SSL 端口 8729
3. 空密码设备注意安全风险
4. 部分命令需要管理员权限

## 文件结构

```
mikrotik/
├── SKILL.md           # Skill 说明和配置
├── handler.py         # 命令处理器
├── README.md          # 本文件
└── mikrotik-api/      # Python API 客户端
    ├── __init__.py
    ├── client.py      # 核心 API 客户端
    ├── commands.py    # 常用命令封装
    ├── cli.py         # 命令行工具
    └── README.md      # API 文档
```

## 开发

### 测试

```bash
cd mikrotik-api
python3 cli.py 10.0.5.4 status
```

### 添加新功能

1. 在 `commands.py` 中添加新方法
2. 在 `handler.py` 中添加命令处理
3. 更新 `SKILL.md` 文档

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 作者

虾哥 🤖

## 相关链接

- [OpenClaw 文档](https://docs.openclaw.ai)
- [MikroTik API 文档](https://help.mikrotik.com/docs/display/ROS/API)
- [ClawHub](https://clawhub.com)
