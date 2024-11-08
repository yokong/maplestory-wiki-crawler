# MapleStory Asset Downloader

一个用于下载冒险岛游戏资源 [https://maplestory.wiki](https://maplestory.wiki) 的 Python 工具，支持物品、NPC 和地图等游戏素材的批量下载。仅供学习交流使用，请勿用于商业用途。

## 功能特点

- 支持多种游戏资源下载：
  - 物品（装备、消耗品等）
  - NPC（开发中）
  - 地图（开发中）
- 多线程并发下载
- 自动重试机制
- 自动处理重名文件

## 系统要求

- Python 3.7+
- pip（Python 包管理器）

## 安装说明

执行以下命令安装所需的 Python 包：

```bash
pip install -r requirements.txt
```

## 使用说明

1. 检查配置文件：

下载时需要配置文件中配置 API、路径、请求、并发等参数，请根据需要修改`config.py`文件。

2. 运行脚本：

```bash
python main.py
```
