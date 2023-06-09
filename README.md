# Fetching political articles from NHSA in batch

---

![GitHub repo size](https://img.shields.io/github/repo-size/hotakus/nhsa-policy-spider?style=flat-square)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/hotakus/nhsa-policy-spider?style=flat-square)](https://github.com/Hotakus/nhsa-policy-spider/releases)
![GitHub Release Date](https://img.shields.io/github/release-date/hotakus/nhsa-policy-spider)

---

### Description

The project is aim to fetch the political articles of NHSA.  
It implements:
- Fetching articles and pictures, and save them into local.
- Detecting the pictures' content and transform them as text.
- Compose the original text and pictures' content as docx file.

---

### Start

1. **Install [Anaconda](https://www.anaconda.com/download/).**
2. **Download this repository to your computer.**

    ```Bash
    git clone https://github.com/Hotakus/nhsa-policy-spider.git
    ```

3. **Download and uncompress the [Chrome.7z](https://github.com/Hotakus/nhsa-policy-spider/releases/download/nps-v1.1.3/Chrome.7z) as folder named Chrome**

---

### Directly Run

If you want to directly run the code, you can follow the steps below:

```Bash
conda create -n nhsa python=3.8.16
conda activate nhsa
pip install -r requirements.txt
python main.py
```

And then, waiting for the results of fetch.
The all results are in "documents" folder, and some pictures of articles in
"pictures" folder.

**If you have done all procedures above,  you can use pycharm to open this project directly.**

---

### Pack

Use tool -- "Pyinstaller", and turn your conda env to nhsa.
Run:

```Bash
pyinstall --noconfirm ./artice.exe.spec
```

or double click "pack.bat" in Windows system.

and wait a minutes in the dist will generate the exe file
, the "article.exe"

---
