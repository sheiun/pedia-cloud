# Pedia Cloud API

A third-party Python API for [Pedia Cloud Dictionary](https://pedia.cloud.edu.tw/)

## Install

```bash
pip install pedia-cloud
```

## Usage

### Get all words and its meaning

```python
>>> from pedia_cloud import PediaDictionary
>>> PediaDictionary.get_all("早")
[早, ㄗㄠˇ, meanings count: 11]
>>> PediaDictionary.get_all("好")
[好, ㄏㄠˇ, meanings count: 14, 好, ㄏㄠˋ, meanings count: 3]
>>> PediaDictionary.get_all("早")[0].meanings
[{'type': '[名]', 'def': '天剛亮的時候...'}, ...]
```

### A word

```python
>>> from pedia_cloud import PediaDictionary
>>> word = PediaDictionary.get_one("好")
>>> word
好, ㄏㄠˇ, meanings count: 14
>>> word.text
'好'
>>> word.zuyin
'ㄏㄠˇ'
>>> word.meanings
[{'type': '[形]', 'def': '美、善，...
```

### Dictionary based idiom segmentation

> I implement it by using pedia-cloud dictionary.  
> This will be slow for long setence due to api call.

```python
>>> from pedia_cloud import PediaDictionary
>>> PediaDictionary.segment("一鳴驚人")
['一', '鳴', '驚人']
>>> PediaDictionary.segment("匯集了世界各地的新聞來源")
['匯集', '了', '世界', '新聞來源']
```
