# Per installare python LINUX
```
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
``` 
```
sudo apt install python3.10 -y
```
```
sudo apt install python3.10-venv -y
```
```
python3.10 -m venv venv
```

# Altri comandi
Per creare la venv ( probabilmente ha senso fare un file config )
```
py -3.10 -m venv venv
```
```
source venv/bin/activate
```

Per usare requirements.txt
```
pip freeze > requirements.txt
```
```
pip install -r requirements.txt
```

Per aggiornare pip win
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
cd ..
```

Per scaricare il progetto e utile ricordare che e necessario scaricare lighglue e hloc separatemante dal file requirements.txt senno vanno in errore

# Avvio rapido

Per iniziare a lavorare c'e' bisogno di eseguire questi comandi 
```
chmod +x setup/setup.sh
```
```
./setup/setup.sh
```
```
source venv/bin/activate
```