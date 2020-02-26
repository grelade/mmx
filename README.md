## memsEX
tool for meme popularity analysis. backbone of [this website](https://grelade.pythonanywhere.com).

## based on:
* [clustering alg](https://github.com/zegami/image-similarity-clustering)
* [memescraper](https://github.com/Salil-Jain/memescraper)

## ways to go:

memsEX has two basic ways of work:
- **hoard** is essentially dedicated for *offline* use on your pc:
    * downloading all meme images (~2gb for an extensive scrape)
    * do a step-by-step analysis, store all steps
    * prepare detailed analysis
- **harvest**  is tailored for *online* purposes (like running on a server) and involves:
    * no storage of images, only data/and reddit links
    * doing feature extraction on-the-fly
    * only optimal clustering analysis

In short, hoarding is heavyweight while harvesting tries to keep it as light as possible.

## usage:
- to **hoard** run:
```
python hoard.py
```

- to **harvest** run
```
python harvest.py
```
