# 发票自动归档 Skill

自动识别增值税发票图片/PDF，智能分类汇总，生成Excel报销报表。

## 安装方法

**只需两步：**

### 第一步：复制文件夹

把整个 `invoice` 文件夹复制到：

```
~/.claude/skills/
```

完成后目录结构应该是：
```
~/.claude/skills/invoice/
├── SKILL.md
├── invoice_ocr.py
└── config-template.json
```

**快捷命令：**
```bash
cp -r invoice ~/.claude/skills/
```

### 第二步：配置 API 密钥

创建配置文件 `~/.invoice-ocr-config.json`：

```bash
cp ~/.claude/skills/invoice/config-template.json ~/.invoice-ocr-config.json
```

然后编辑，填入你的百度 OCR API 密钥：

```json
{
  "api_key": "你的API Key",
  "secret_key": "你的Secret Key"
}
```

**搞定！**

---

## 获取百度 OCR API 密钥

1. 访问 [百度智能云控制台](https://console.bce.baidu.com/ai/#/ai/ocr/overview/index)
2. 注册/登录百度账号，完成实名认证
3. 开通「增值税发票识别」服务（免费额度：个人1000次/月，企业2000次/月）
4. 创建应用，获取 `API Key` 和 `Secret Key`

---

## 使用方法

在 Claude Code 中输入：

```bash
/发票                              # 处理当前目录
/发票 ~/Desktop/报销发票           # 处理指定目录
/发票 ~/Desktop/报销发票 Q1.xlsx   # 指定输出文件名
```

---

## 依赖安装（首次使用前）

```bash
pip install requests openpyxl Pillow pdf2image
```

处理 PDF 还需要：
```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt-get install poppler-utils
```

---

## 支持的文件格式

- ✅ jpg / jpeg / png / bmp
- ✅ pdf（需安装 poppler）
- ✅ webp（自动转换）

---

## 输出报表

Excel 报表包含 4 个 Sheet：
1. **发票明细** - 每张发票详情
2. **按类别汇总** - 餐饮、交通、办公等
3. **按月份汇总** - 按开票月份统计
4. **报销清单** - 总金额汇总
