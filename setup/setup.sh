sudo apt update
sudo apt install software-properties-common build-essential cmake colmap libusb-1.0-0 ffmpeg -y

sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev

python3.10 -m venv venv
source venv/bin/activate

python -m pip install --upgrade pip setuptools wheel

if [ ! -d "Hierarchical-Localization" ]; then
    git clone --recursive https://github.com/cvg/Hierarchical-Localization.git
fi
cd Hierarchical-Localization
pip install -e .
cd ..

if [ -f "requirements.txt" ]; then
    pip install --ignore-installed -r requirements.txt
else
    echo "Avviso: requirements.txt non trovato nella cartella corrente, salto il passaggio."
fi

python -c "import nerfstudio, pathlib; p = pathlib.Path(nerfstudio.__file__).parent / 'utils' / 'eval_utils.py'; text = p.read_text(); p.write_text(text.replace('torch.load(load_path, map_location=\"cpu\")', 'torch.load(load_path, map_location=\"cpu\", weights_only=False)')); print('Patch applicata con successo a:', p)"