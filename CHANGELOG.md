# Changelog

所有重要的项目变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/)，项目遵循 [语义化版本](https://semver.org/)。

## [Unreleased]

### ✨ 新功能
- 添加版本管理系统（version-bump.sh, version-check.sh, generate-changelog.sh）
- 创建版本管理策略文档 (VERSION-MANAGEMENT-STRATEGY.md)
- 实现 Version Manager Skill
- 添加 GitHub Release 模板

### 📚 文档
- 创建完整的版本管理策略文档
- 添加版本管理技能文档
- 创建 Release 模板

### 🔧 其他
- 整理开发项目到 my-dev/ 子目录
- 清理依赖和构建文件
- 优化 Git 仓库结构

---

## [2.1.0] - 2026-03-05

### ✨ 新功能
- 模型健康监控系统 v2.0
  - 自动错误检测（billing, auth, rate limit, timeout）
  - 备用模型自动切换
  - 集成 heartbeat 检查
- MindForge AI 项目
  - 6 个核心模块（memory, planning, thought, learning, monitor, evaluation）
  - 文字冒险游戏娱乐系统
  - 积分管理系统（5 类评分）
- SSH 远程控制面板
  - 现代化 UI 设计
  - 实时终端连接
  - 模型健康监控集成

### 🐛 Bug 修复
- 修复模型额度耗尽时系统崩溃问题
- 修复记忆系统内存泄漏
- 修复 JSON 解析错误

### ⚡ 性能优化
- 优化模型 fallback 链
- 减少不必要的 API 调用
- 优化数据库查询

### 📚 文档
- 添加模型监控使用文档
- 创建外部探索计划文档
- 更新系统架构文档

### ♻️ 重构
- 重构监控系统架构
- 模块化设计（参考 LangChain）
- 统一错误处理机制

---

## [2.0.1] - 2026-03-01

### 🐛 Bug 修复
- 修复初始化脚本错误
- 修复配置文件解析问题

### 🔧 其他
- 更新依赖版本
- 优化构建流程

---

## [2.0.0] - 2026-02-28

### ✨ 新功能
- OpenClaw 核心系统上线
- 支持多模型提供商（Bailian, ZAI）
- 基础记忆系统
- 基础规划系统

### 📚 文档
- 创建初始文档
- 添加使用指南

---

*此 CHANGELOG 持续更新中...*
