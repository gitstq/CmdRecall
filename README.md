<div align="center">

# 🧠 CmdRecall

**Lightweight Terminal Command History Intelligent Recall Engine**

**轻量级终端命令历史智能召回引擎**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-green.svg)](https://github.com/gitstq/CmdRecall)

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

<a name="english"></a>
## 🇺🇸 English

### 🎉 Introduction

**CmdRecall** is a lightweight, zero-dependency terminal command history intelligent recall engine. Never forget a command again! It uses advanced TF-IDF and BM25 algorithms to help you quickly find commands you've used before.

**Key Highlights:**
- 🔍 **Intelligent Search** - TF-IDF + BM25 + fuzzy matching algorithms
- 📊 **Smart Ranking** - Frequency, recency, and relevance scoring
- 🏷️ **Auto Classification** - Automatically categorize commands (Git, Docker, K8s, etc.)
- ⚠️ **Risk Detection** - Warn about dangerous commands
- 📝 **Templates** - Save and reuse command templates
- 🖥️ **TUI Interface** - Beautiful terminal UI (optional)
- 🐚 **Multi-Shell** - Support for Bash, Zsh, Fish

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🔍 **Smart Search** | TF-IDF + BM25 algorithms with fuzzy matching |
| 📊 **Intelligent Ranking** | Combined scoring by frequency, recency, and relevance |
| 🏷️ **Auto Classification** | 18 command categories (Git, Docker, K8s, NPM, etc.) |
| ⚠️ **Risk Assessment** | 5-level risk detection (safe, low, medium, high, critical) |
| 📝 **Template System** | Save templates with `{{variable}}` placeholders |
| 🖥️ **TUI Dashboard** | Interactive terminal interface with real-time search |
| 🐚 **Shell Integration** | One-click setup for Bash/Zsh/Fish |
| 💾 **SQLite Storage** | Zero-configuration local database |

### 🚀 Quick Start

#### Requirements
- Python 3.8+
- No external dependencies required!

#### Installation

```bash
# Install from PyPI
pip install cmdrecall

# Or install with TUI support
pip install cmdrecall[tui]

# Or install from source
git clone https://github.com/gitstq/CmdRecall.git
cd CmdRecall
pip install -e .
```

#### Basic Usage

```bash
# Sync your shell history
cmdrecall sync

# Search commands
cmdrecall search "git commit"
cmdrecall search "docker run" --limit 10

# Fuzzy search
cmdrecall search "gcm" --fuzzy

# Show most used commands
cmdrecall top

# Show recent commands
cmdrecall recent

# Launch TUI interface
cmdrecall tui

# View statistics
cmdrecall stats
```

### 📖 Detailed Usage

#### Search Commands

```bash
# Basic search
cmdrecall search "npm install"

# Search with limit
cmdrecall search "git" --limit 50

# Fuzzy search (finds "git commit message" with query "gcm")
cmdrecall search "gcm" --fuzzy

# Filter by category
cmdrecall search "push" --category git
```

#### Template Management

```bash
# Add a template
cmdrecall template add deploy "kubectl apply -f {{env}}/{{service}}.yaml"

# List templates
cmdrecall template list

# Use a template
cmdrecall template use deploy env=prod service=api

# Show template details
cmdrecall template show deploy
```

#### Browse by Category

```bash
# List all categories
cmdrecall category

# Browse specific category
cmdrecall category git
cmdrecall category docker
cmdrecall category kubectl
```

#### Shell Integration

```bash
# Initialize shell integration
cmdrecall init --shell bash
cmdrecall init --shell zsh
cmdrecall init --shell fish
```

### 💡 Design Philosophy

**Why CmdRecall?**
- **Ctrl+R is limited** - Only substring matching, no ranking
- **fzf requires installation** - External dependency, complex setup
- **FuzzyShell needs ML models** - Heavy, requires embeddings

**CmdRecall Advantages:**
- ✅ Zero dependencies - Pure Python, works everywhere
- ✅ Intelligent ranking - Not just substring matching
- ✅ Lightweight - Fast startup, low memory usage
- ✅ Privacy-first - All data stored locally

### 📦 Build & Deploy

```bash
# Build package
pip install build
python -m build

# Install locally
pip install dist/cmdrecall-1.0.0-py3-none-any.whl
```

### 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

<a name="简体中文"></a>
## 🇨🇳 简体中文

### 🎉 项目介绍

**CmdRecall** 是一款轻量级、零依赖的终端命令历史智能召回引擎。再也不用担心忘记之前用过的复杂命令！它使用先进的 TF-IDF 和 BM25 算法，帮助你快速找到历史命令。

**核心亮点：**
- 🔍 **智能搜索** - TF-IDF + BM25 + 模糊匹配算法
- 📊 **智能排序** - 频率、时效性、相关性综合评分
- 🏷️ **自动分类** - 自动识别命令类型（Git、Docker、K8s等）
- ⚠️ **风险检测** - 危险命令预警
- 📝 **模板系统** - 保存和复用命令模板
- 🖥️ **TUI界面** - 美观的终端交互界面（可选）
- 🐚 **多Shell支持** - 支持 Bash、Zsh、Fish

### ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🔍 **智能搜索** | TF-IDF + BM25 算法，支持模糊匹配 |
| 📊 **智能排序** | 频率、时效性、相关性综合评分 |
| 🏷️ **自动分类** | 18种命令分类（Git、Docker、K8s、NPM等） |
| ⚠️ **风险评估** | 5级风险检测（安全、低、中、高、危险） |
| 📝 **模板系统** | 支持 `{{变量}}` 占位符的命令模板 |
| 🖥️ **TUI面板** | 实时搜索的交互式终端界面 |
| 🐚 **Shell集成** | Bash/Zsh/Fish 一键配置 |
| 💾 **SQLite存储** | 零配置本地数据库 |

### 🚀 快速开始

#### 环境要求
- Python 3.8+
- 无需任何外部依赖！

#### 安装方式

```bash
# 从 PyPI 安装
pip install cmdrecall

# 安装 TUI 支持
pip install cmdrecall[tui]

# 从源码安装
git clone https://github.com/gitstq/CmdRecall.git
cd CmdRecall
pip install -e .
```

#### 基本使用

```bash
# 同步 Shell 历史
cmdrecall sync

# 搜索命令
cmdrecall search "git commit"
cmdrecall search "docker run" --limit 10

# 模糊搜索
cmdrecall search "gcm" --fuzzy

# 显示最常用命令
cmdrecall top

# 显示最近命令
cmdrecall recent

# 启动 TUI 界面
cmdrecall tui

# 查看统计信息
cmdrecall stats
```

### 📖 详细使用指南

#### 搜索命令

```bash
# 基础搜索
cmdrecall search "npm install"

# 限制结果数量
cmdrecall search "git" --limit 50

# 模糊搜索（输入 "gcm" 可找到 "git commit message"）
cmdrecall search "gcm" --fuzzy

# 按分类筛选
cmdrecall search "push" --category git
```

#### 模板管理

```bash
# 添加模板
cmdrecall template add deploy "kubectl apply -f {{env}}/{{service}}.yaml"

# 列出所有模板
cmdrecall template list

# 使用模板
cmdrecall template use deploy env=prod service=api

# 查看模板详情
cmdrecall template show deploy
```

#### 按分类浏览

```bash
# 列出所有分类
cmdrecall category

# 浏览特定分类
cmdrecall category git
cmdrecall category docker
cmdrecall category kubectl
```

#### Shell 集成

```bash
# 初始化 Shell 集成
cmdrecall init --shell bash
cmdrecall init --shell zsh
cmdrecall init --shell fish
```

### 💡 设计思路

**为什么选择 CmdRecall？**
- **Ctrl+R 功能有限** - 仅支持子串匹配，无智能排序
- **fzf 需要额外安装** - 外部依赖，配置复杂
- **FuzzyShell 需要 ML 模型** - 体积大，需要嵌入模型

**CmdRecall 优势：**
- ✅ 零依赖 - 纯 Python 实现，随处可用
- ✅ 智能排序 - 不仅仅是子串匹配
- ✅ 轻量级 - 快速启动，低内存占用
- ✅ 隐私优先 - 所有数据本地存储

### 📦 打包与部署

```bash
# 构建安装包
pip install build
python -m build

# 本地安装
pip install dist/cmdrecall-1.0.0-py3-none-any.whl
```

### 🤝 贡献指南

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

### 📄 开源协议

本项目采用 MIT 协议开源，详见 [LICENSE](LICENSE)。

---

<a name="繁體中文"></a>
## 🇹🇼 繁體中文

### 🎉 專案介紹

**CmdRecall** 是一款輕量級、零依賴的終端命令歷史智能召回引擎。再也不用擔心忘記之前用過的複雜命令！它使用先進的 TF-IDF 和 BM25 演算法，幫助你快速找到歷史命令。

**核心亮點：**
- 🔍 **智能搜尋** - TF-IDF + BM25 + 模糊匹配演算法
- 📊 **智能排序** - 頻率、時效性、相關性綜合評分
- 🏷️ **自動分類** - 自動識別命令類型（Git、Docker、K8s等）
- ⚠️ **風險檢測** - 危險命令預警
- 📝 **模板系統** - 保存和復用命令模板
- 🖥️ **TUI介面** - 美觀的終端互動介面（可選）
- 🐚 **多Shell支援** - 支援 Bash、Zsh、Fish

### ✨ 核心特性

| 特性 | 說明 |
|------|------|
| 🔍 **智能搜尋** | TF-IDF + BM25 演算法，支援模糊匹配 |
| 📊 **智能排序** | 頻率、時效性、相關性綜合評分 |
| 🏷️ **自動分類** | 18種命令分類（Git、Docker、K8s、NPM等） |
| ⚠️ **風險評估** | 5級風險檢測（安全、低、中、高、危險） |
| 📝 **模板系統** | 支援 `{{變數}}` 佔位符的命令模板 |
| 🖥️ **TUI面板** | 即時搜尋的互動式終端介面 |
| 🐚 **Shell整合** | Bash/Zsh/Fish 一鍵配置 |
| 💾 **SQLite儲存** | 零配置本機資料庫 |

### 🚀 快速開始

#### 環境要求
- Python 3.8+
- 無需任何外部依賴！

#### 安裝方式

```bash
# 從 PyPI 安裝
pip install cmdrecall

# 安裝 TUI 支援
pip install cmdrecall[tui]

# 從原始碼安裝
git clone https://github.com/gitstq/CmdRecall.git
cd CmdRecall
pip install -e .
```

#### 基本使用

```bash
# 同步 Shell 歷史
cmdrecall sync

# 搜尋命令
cmdrecall search "git commit"
cmdrecall search "docker run" --limit 10

# 模糊搜尋
cmdrecall search "gcm" --fuzzy

# 顯示最常用命令
cmdrecall top

# 顯示最近命令
cmdrecall recent

# 啟動 TUI 介面
cmdrecall tui

# 查看統計資訊
cmdrecall stats
```

### 💡 設計思路

**為什麼選擇 CmdRecall？**
- **Ctrl+R 功能有限** - 僅支援子串匹配，無智能排序
- **fzf 需要額外安裝** - 外部依賴，配置複雜
- **FuzzyShell 需要 ML 模型** - 體積大，需要嵌入模型

**CmdRecall 優勢：**
- ✅ 零依賴 - 純 Python 實現，隨處可用
- ✅ 智能排序 - 不僅僅是子串匹配
- ✅ 輕量級 - 快速啟動，低記憶體佔用
- ✅ 隱私優先 - 所有資料本機儲存

### 📄 開源協議

本專案採用 MIT 協議開源，詳見 [LICENSE](LICENSE)。

---

<div align="center">

**Made with ❤️ by [gitstq](https://github.com/gitstq)**

**If you find this project useful, please consider giving it a ⭐!**

</div>
