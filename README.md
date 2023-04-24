# Fetching political articles from NHSA in batch

---

---

# Start
- **First: Install anaconda.**
- **Second: Download this repository to your computer.**
- **Three: Uncompress the Chrome.7z as folder named Chrome**
---
### Directly Run
If you want to directly run the code, you can follow the steps below:

```bash
conda activate a_new_environment
pip install -r requirements.txt
python main.py
```
---
### Pack
Use pack named "Pyinstaller"
```bash
pyinstall --noconfirm ./artice.exe.spec
```

and wait minutes in the dist will generate the exe file
, the "article.exe"

### TODO:
- [ ] 实现正则表达提取文章
- [x] 实现指定内容提取
- [x] 完成批量保存文章(文件名)
- [x] 完成polling主体

- [x] 实现html图片检测
- [x] 实现图片文字识别
- [x] 实现多线程图片识别
- [x] 重构文章抓取算法
- [ ] 优化图像识别准确率