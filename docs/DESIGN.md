# 工作方式与维护

中文 | [English](DESIGN.en.md) · [使用说明](../README.md)

## 对话与记录

Skill 分别管理当前活动、反馈节奏、记录开关和解释语言。比如，你可以一边扮演餐厅顾客，一边要求逐句纠正，同时暂停记录。改变其中一项，不会自动改变其他设置。

练习默认等用户说完再反馈。完整示范和独立作答代表不同的学习证据；只有真实作答才能改变复习状态。同一表达的多次尝试保留历史，当前状态取最近相关证据，不能把重复记录计成多个学会的词。

Notion 负责存放记录。保存前确认目标、使用稳定会话标识并查重；保存后回读。返回结果不明确时，先核对已有页面，再决定是否补写。具体规则由 `SKILL.md` 和 `references/` 中的文件维护，不为不同文档语言复制两套运行规则。

## 文件

| 位置 | 内容 |
|---|---|
| `SKILL.md` | 入口、控制语和共同规则 |
| `agents/openai.yaml` | 客户端显示信息 |
| `references/` | 对话、复盘和 Notion 操作流程 |
| `preferences.example.md` | 不含个人数据的设置模板 |
| `README.md`、`README.en.md` | 中英文使用说明 |
| `docs/` | 中英文维护说明和试用场景 |
| `scripts/check_project.py` | 发布清单、链接和常见隐私信息检查 |
| `tests/` | 使用合成数据的检查器测试 |
| `.github/workflows/check.yml` | 每次推送时在 GitHub Actions 中运行同样的检查 |

## 发布检查

在项目根目录运行，Python 3.10+，无需额外依赖：

```bash
python3 scripts/check_project.py
python3 -m unittest discover -s tests -v
python3 scripts/check_project.py --history
```

检查器核对明确的发布清单，并检查 Git 中是否还有清单外的跟踪文件。它检查文件中的常见隐私模式和 `SKILL.md` 的元数据；`--history` 还检查本地分支和标签可达的提交身份及历史文件。首次整理尚未提交的新文件时，默认检查仍会读取工作目录中的这些文件。这三条命令也会通过 GitHub Actions 在每次推送时运行。

提交使用 GitHub 的 `noreply` 隐私邮箱；检查器同样接受 `noreply@…` 形式的机器人地址，例如 GitHub 网页合并或 AI 工具的署名。`preferences.local.md`、`private-records/`、转写和密钥不能加入发布清单。`.gitignore` 对已经被 Git 跟踪的文件不起作用；发现敏感信息时，需要检查旧提交，不能只删当前文件。

自动检测只能提示一部分风险，发布前仍需阅读实际差异。历史检查也不能证明远端缓存、其他引用或别人保存的副本已经删除。

## 验证范围

检查器测试验证文件规则，不验证教学效果。对话规则需要用 [试用场景](BEHAVIOR.md) 检查，尤其是语言切换、暂停记录、角色退出和不确定的保存结果。真实语音和 Notion 联调未完成前，不能写成已验证功能。
