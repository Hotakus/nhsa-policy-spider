# Fetching political articles from NHSA in batch

---

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
```bash
git clone https://github.com/Hotakus/nhsa-policy-spider.git
```
3. **Uncompress the Chrome.7z as folder named Chrome**  
---
### Directly Run
If you want to directly run the code, you can follow the steps below:

```bash
conda create -n nhsa python=3.8.16
conda activate nhsa
pip install -r requirements.txt
python main.py
```
And then, waiting for the results of fetch.  
The all results are in "documents" folder, and some pictures of articles in 
"pictures" folder.

---
### Pack
Use tool -- "Pyinstaller", and turn your conda env to nhsa.   
Run:
```bash
pyinstall --noconfirm ./artice.exe.spec
```
or double click "pack.bat" in windows system.

and wait a minutes in the dist will generate the exe file
, the "article.exe"
