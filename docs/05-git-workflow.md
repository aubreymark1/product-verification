# Git 工作流

```text
main
└─ dev
   ├─ feature/video-select
   ├─ feature/result-ui
   ├─ feature/backend-retrieval
   └─ feature/ai-integration
```

`main` 只保留稳定演示版本，`dev` 用于联调。每人只在自己的 feature 分支工作，冲突在个人分支解决。禁止直接推送 `main`、提交密钥、未测试合并和让 AI 整体重构。

## 命令模板

```powershell
git fetch origin
git switch dev
git pull --ff-only origin dev
git switch -c feature/your-name
# 修改并测试
git status
git add <明确的文件>
git commit -m "feat: 完成一个小主题"
git fetch origin
git rebase origin/dev
# 解决冲突后重新测试
git push -u origin feature/your-name
```

然后在 GitHub 发起从个人分支到 `dev` 的 Pull Request。合并前检查 API 合同、测试、构建、目录边界和是否误改他人文件。

提交前缀：`feat`、`fix`、`docs`、`test`、`refactor`、`chore`。

