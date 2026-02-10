#!/bin/bash
# 临时切换到个人GitHub账号 (jackchen1941) 并推送代码
# 不影响全局Git配置和工作账号

echo "🔄 切换到个人GitHub账号..."
echo "个人账号: jackchen1941"
echo "工作账号: jackchen19411 (不受影响)"
echo ""

# 1. 仅在当前项目设置个人账号的Git配置（不影响全局）
echo "⚙️ 配置当前项目使用个人账号..."
git config --local user.name "jackchen1941"
git config --local user.email "your-personal-email@example.com"  # 替换为你的个人邮箱

# 2. 创建SSH配置，指定使用个人账号的SSH密钥
echo "🔑 配置SSH使用个人账号密钥..."

# 检查是否已有个人账号的SSH密钥
if [ ! -f ~/.ssh/id_ed25519_personal ]; then
    echo "⚠️ 未找到个人账号SSH密钥，需要生成..."
    echo "请按Enter继续生成，或Ctrl+C取消..."
    read
    
    # 生成个人账号专用的SSH密钥
    ssh-keygen -t ed25519 -C "your-personal-email@example.com" -f ~/.ssh/id_ed25519_personal
    
    echo ""
    echo "✅ SSH密钥已生成！"
    echo "📋 请复制以下公钥并添加到GitHub个人账号："
    echo "   访问: https://github.com/settings/keys"
    echo ""
    cat ~/.ssh/id_ed25519_personal.pub
    echo ""
    echo "按Enter继续..."
    read
fi

# 3. 配置SSH使用个人密钥（临时环境变量方式）
echo "🔧 设置SSH使用个人密钥..."

# 创建临时SSH配置
cat > /tmp/ssh_config_personal << EOF
Host github.com-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_personal
    IdentitiesOnly yes
EOF

# 4. 更新Git remote使用个人账号的SSH配置
echo "🔗 更新Git remote URL..."
git remote set-url origin git@github.com-personal:jackchen1941/knowledge_platform.git

# 5. 配置Git使用临时SSH配置
export GIT_SSH_COMMAND="ssh -F /tmp/ssh_config_personal"

# 6. 测试SSH连接
echo "🧪 测试SSH连接..."
ssh -F /tmp/ssh_config_personal -T git@github.com-personal

echo ""
echo "✅ 配置完成！现在可以推送代码了..."
echo ""

# 7. 推送代码
echo "⬆️ 推送到GitHub个人账号..."
git push -u origin main

echo ""
echo "🎉 完成！代码已推送到个人账号仓库"
echo "🌐 访问: https://github.com/jackchen1941/knowledge_platform"
echo ""
echo "📝 注意: 这些配置只对当前项目有效，不影响其他项目"
echo "   - Git用户配置: 仅当前项目"
echo "   - SSH密钥: 使用个人专用密钥"
echo "   - 工作账号: 完全不受影响"
