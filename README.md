# Digital twin

Il progetto consiste in una pipeline software per la fotogrammetria e la creazione di Digital Twin subacquei, ingegnerizzata con un'architettura a moduli separati. Il flusso di lavoro si basa sull'acquisizione di dati tramite una staffa RIG stereo e inizia con un'estrazione intelligente dei frame guidata dal flusso ottico, la quale sfrutta il riconoscimento di flash per la sincronizzazione se sono presenti due video in input. Le coppie di immagini allineate vengono poi processate da COLMAP, che è stato potenziato con un approccio AI basato sul Deep Learning per estrarre le feature e trovare punti di ancoraggio anche sui fondali marini più difficili o privi di contrasto. Infine, le informazioni metriche e spaziali ricavate dal Rig vengono elaborate da un modulo finale di rendering basato sul Gaussian Splatting, una tecnologia che permette di gestire la fisica ottica sottomarina per "cancellare" la torbidezza dell'acqua e restituire un modello 3D fotorealistico, metricamente rigoroso e navigabile in tempo reale.

## Setup iniziale 

Per facilitare la preparazione dell'ambiente e' stato creato un file di setup:
```
chmod +x setup/setup.sh
```
```
./setup/setup.sh
```
```
source venv/bin/activate
```

Successivamente vanno caricati i video nelle relative cartelle in `data/data_extractor/01_raw`, configurare la modalita' di cattura nel file `config/common/config.py` ed in fine avviare il file `main.py` per lanciare la pipeline.
```
python main.py
```

Al termine di ogni modulo verra' chiesto se proseguire con quello successivo.



