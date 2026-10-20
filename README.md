Per creare la venv ( probabilmente ha senso fare un file config )
```
py -3.10 -m venv venv
```

Per usare requirements.txt
```
pip freeze > requirements.txt
```
```
pip install -r requirements.txt
```

Per aggiornare pip
```
python.exe -m pip install --upgrade pip
```

Per scaricare hloc da git 
```
git clone --recursive https://github.com/cvg/Hierarchical-Localization.git
```
```
cd Hierarchical-Localization
pip install -e .
```

Per scaricare il progetto e utile ricordare che e necessario scaricare lighglue e hloc separatemante dal file requirements.txt senno vanno in errore
