#!/bin/bash
# 推送代码到GitHub的脚本

echo "🚀 准备推送代码到GitHub..."
echo "仓库地址: git@github.com:jackchen1941/knowledge_platform.git"
echo ""

# 1. 检查git状态
echo "📊 检查Git状态..."
git status

echo ""
echo "按Enter继续提交..."
read

# 2. 配置git用户信息（如果还没配置）
echo "⚙️ 配置Git用户信息..."
git config user.name "jackchen1941"
git config user.email "your-email@example.com"  # 请替换为你的邮箱

# 3. 提交代码（使用简短的commit信息）
echo "📝 提交代码..."
git commit -m "Initial release v1.0.0 - Complete knowledge management platform with 14 core modules, enterprise security, and production-ready deployment"

# 4. 更新remote URL为SSH
echo "🔗 更新remote URL为SSH..."
git remote set-url origin git@github.com:jackchen1941/knowledge_platform.git

# 5. 推送到GitHub
echo "⬆️ 推送到GitHub..."
git push -u origin main

echo ""
echo "✅ 完成！代码已推送到GitHub"
echo "🌐 访问: https://github.com/jackchen1941/knowledge_platform"
