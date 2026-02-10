# 快速推送到GitHub

## 方法1: 使用脚本（推荐）

```bash
chmod +x PUSH_TO_GITHUB.sh
./PUSH_TO_GITHUB.sh
```

## 方法2: 手动执行命令

如果脚本卡住，请在终端手动执行以下命令：

### 1. 配置Git用户信息（首次需要）
```bash
git config user.name "jackchen1941"
git config user.email "your-email@example.com"  # 替换为你的邮箱
```

### 2. 检查状态
```bash
git status
```

### 3. 提交代码（简短版本）
```bash
git commit -m "Initial release v1.0.0"
```

### 4. 更新remote为SSH
```bash
git remote set-url origin git@github.com:jackchen1941/knowledge_platform.git
```

### 5. 推送到GitHub
```bash
git push -u origin main
```

## 如果遇到问题

### 问题1: SSH密钥未配置
```bash
# 生成SSH密钥
ssh-keygen -t ed25519 -C "your-email@example.com"

# 复制公钥
cat ~/.ssh/id_ed25519.pub

# 然后到GitHub Settings > SSH and GPG keys > New SSH key 添加
```

### 问题2: 推送被拒绝
```bash
# 如果远程仓库有内容，先拉取
git pull origin main --allow-unrelated-histories

# 然后再推送
git push -u origin main
```

### 问题3: commit卡住
- 使用更短的commit信息
- 或者直接按 Ctrl+C 取消，然后用简短版本重试

## 验证推送成功

推送成功后，访问：
https://github.com/jackchen1941/knowledge_platform

你应该能看到所有文件已经上传！

## 后续步骤

1. 在GitHub上创建第一个Release (v1.0.0)
2. 设置分支保护规则
3. 启用安全扫描功能
4. 添加仓库描述和标签