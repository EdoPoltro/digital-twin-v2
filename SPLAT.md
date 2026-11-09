# Comandi per la preparazione dell'ambiente

Per copiare una cartella da Google Drive su terminale usare
```
cp -r /content/drive/MyDrive/nome_della_tua_cartella /content/destinazione
```

Per Unzippare la cartella da Google Drive
```
unzip /content/drive/MyDrive/data.zip -d /content/splat_generator
```

Per installare Miniconda su linux
```
mkdir -p ~/miniconda3
```
```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
```
```
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
```
```
source ~/miniconda3/bin/activate
```

Per creare la venv con conda su ython 3.10
```
conda create --name venv python=3.10 -y
```
```
conda activate venv
```

Per aggiornare i tool se non uso conda
```
python -m pip install --upgrade pip setuptools wheel
```
```
sudo apt install build-essential cmake python3.10-dev -y
```

Per installare Torch
```
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

Per installare Nerfstudio
```
pip install nerfstudio
```

Per installare colmap
```
sudo apt install colmap -y
```

# Comandi per l'esecuzione dell'ambiente

Per preparare il dataset (struttura standard con colmap/sparse/0)
```
ns-process-data images --data data/images --output-dir data --skip-colmap --skip-image-processing --colmap-model-path colmap/sparse/0
```

Per abbassare il numero di Threads 
```
export MAX_JOBS=2
```

Per il training 
```
ns-train splatfacto --data data --output-dir outputs --viewer.quit-on-train-completion True
```

Per esportare il file vedere se si e' creato un checkpoint (dovrebbe restituire step-000029999.ckpt)
```
ls outputs/data/splatfacto/2026-10-20_124234/nerfstudio_models
```

Per esportare il file splat
```
ls outputs/data/splatfacto
```
```
sed -i 's/torch.load(load_path, map_location="cpu")/torch.load(load_path, map_location="cpu", weights_only=False)/g' /root/miniconda3/envs/venv/lib/python3.10/site-packages/nerfstudio/utils/eval_utils.py
```
```
ns-export gaussian-splat --load-config outputs/data/splatfacto/CARTELLA/config.yml --output-dir exports
```
Per salvare il file splat.ply
```
cp exports/splat.ply /content/drive/MyDrive/gaussian-splatting/
```

Usare SuperSplat Editor per visualizzare il risultato


ns-process-data images --data data/sparse_generator/04_undistorted/images --output-dir data/sparse_generator/04_undistorted --skip-colmap --skip-image-processing --colmap-model-path sparse/0

ns-train splatfacto --data data/sparse_generator/04_undistorted --output-dir data/splat_generator/outputs --viewer.quit-on-train-completion True --vis tensorboard

sed -i 's/torch.load(load_path, map_location="cpu")/torch.load(load_path, map_location="cpu", weights_only=False)/g' /content/digital-twin-v2/venv/lib/python3.10/site-packages/nerfstudio/utils/eval_utils.py

ns-export gaussian-splat --load-config data/splat_generator/outputs/04_undistorted/splatfacto//2026-10-22_212651/config.yml --output-dir exports

