# EPUB 仿生阅读转换器（交互式中英文版）

### EPUB Bionic Reading Converter

这是一个将 EPUB 格式的电子书转换为 **仿生阅读 (Bionic Reading)** 排版的 Python 工具。

本项目 fork 自 `dobrosketchkun/bionic-reading-epub-converter` ，新增了部分功能。

A Python tool to convert EPUB eBooks into Bionic Reading formatting.

Forked from `dobrosketchkun/bionic-reading-epub-converter` with additional features.

#### 免责声明 / Disclaimer

主包是个完全不懂代码的阅读障碍！全靠vibe coding！感谢原作者！

代码拿去随便用！要是不会用直接问AI~

本项目仅在 mac OS 测试过；转换后的epub在苹果图书和微信读书中均可正常阅读。

I know nothing about coding. This whole thing was made through vibe coding. All rights and gratitudes go to the original authur [[dobrosketchkun](https://github.com/dobrosketchkun/bionic-reading-epub-converter/commits?author=dobrosketchkun)].

You may use the script and codes in whatever way you want. If encountered any issue, just ask AI for help :)

Only tested for mac OS. Converted epub works properly in Apple Book and WeChat Reading (WeRead).

---

## 新增功能 / New Features

在原项目的基础上，新增了以下功能：

In addition to the original script, the following features are added:

* **自动安装依赖 / Automatic Dependency Setup**
  
  自动检测并提示安装缺少的依赖库（`regex`, `beautifulsoup4`, `lxml`, `tqdm`）。
  
  Automatically detects missing dependencies (`regex`, `beautifulsoup4`, `lxml`, `tqdm`) and prompts for installation.

* **自定义加粗强度 / Customizable Bolding Intensity**
  
  提供 3 种强度，适配不同需求及阅读习惯。
  
  1. **1-低**：单词长度≤4，仅加粗首字母；单词长度≤7，加粗前2个字母；单词长度＞7，加粗前3个字母
  
  2. **2-中**：单词长度≤3，仅加粗首字母；单词长度≤6，加粗前2个字母；单词长度≤9，加粗前3个字母；单词长度＞9，加粗前4个字母
  
  3. **3-高**：无论单词长度，均加粗前50%的字母（小数点向上取整）
  
  Provides 3 intensity levels to suit different reading habits. 
  
  1. **1-Low**: For word-length ≤ 4, only the first letter is bolded; for word-length ≤ 7, the first two letters are bolded; for word-length ＞ 7, the first three letters are bolded.
  
  2. **2-Mid**: For word-length ≤ 3, only the first letter is bolded; for word-length ≤ 6, the first two letters are bolded; for word-length ≤ 9, the first three letters are bolded; for word-length ＞ 9, the first four letters are bolded.
  
  3. **3-high**: The first 50% letters are bolded, regardless of word-length. 
  
  如需精细客制化加粗规则，可自行修改代码中的 "def process_text(text, intensity, opacity):" 部分。
  
  If you want to make your own bolding rule, just find "def process_text(text, intensity, opacity):" among the codes and edit.  

* **未加粗部分透明度调节 / Opacity Adjust**
  
  支持设置非加粗部分的透明度（0-100）。
  
  Allows adjusting the opacity of unbolded letters (0-100).

* **交互式设置**
  
  脚本将询问加粗强度、透明度和文件路径，根据提示选择即可。
  
  Interactive setting - the script will ask about your preferred bolding level, opacity and the path of your epub. Just follow the instructions.

我个人用着最舒服的是2-中强度，65%不透明度，供参考。

FYI, my personal favourite combination is 2-Mid intensity and 65% opacity.

---

## 完整工作流 / Workflow

    运行脚本
    Run the script
    
    ↓
    
    自动检测依赖库完整性（如有缺失，提示是否安装；如依赖完整，则继续下一步）
    Automatic dependencies detection (if missing, prompts for installation; else continues the workflow )
    
    ↓
    
    选择加粗强度
    Select bolding intensity level
    
    ↓
    
    输入不透明度
    Input opacity
    
    ↓
    
    输入需转换的epub文件的绝对路径 或 直接把文件拖拽入终端窗口
    Input path of epub, OR drag the file into terminal
    
    ↓
    
    转化后的文件将自动生成在同一文件夹内，命名为 bionic_{原文件名}.epub
    Converted epub will appear in the same folder, naming bionic_{original filename}.epub

---

## 使用方法 / Usage

    python bionic_convert.py

主包使用 mac OS ，习惯双击偷懒，因此同时提供.command版本（需先在终端运行一次 `chmod +x bionic_convert.command` 进行授权）；内含完整脚本，保存到任意文件夹下均不影响使用，无需和待转换的epub放在一起。

.command is provided for mac OS users， you can run the script by double clicking it (authorization needed: run `chmod +x bionic_convert.command` for the first time). Full codes included, no need to put .command and your epub in the same file - it works properly on its own.

---

如出现任何使用问题或脚本报错，请直接把代码喂AI，因为主包也不会。

祝大家阅读愉快：）

If encoutered any issue, just feed the codes to your favourite AI, since I don't know 💩 about coding.

Happy reading everyone! :)
