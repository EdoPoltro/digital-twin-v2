#!/bin/bash
set -e
cd "$(dirname "$0")/.."

export DEBIAN_FRONTEND=noninteractive
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"

$SUDO apt-get update
$SUDO apt-get install -y build-essential git curl ffmpeg libusb-1.0-0 libgl1 libglib2.0-0 libegl1 libgomp1

# Python 3.10 con uv (Ubuntu 24.04 non lo ha in apt)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
rm -rf venv
uv venv venv --python 3.10 --seed

# Immagine NVIDIA: ignora il loro torch (Python 3.12) e compila gsplat solo per la GPU presente
echo 'unset PYTHONPATH TORCH_CUDA_ARCH_LIST; export LD_LIBRARY_PATH=$(echo "$LD_LIBRARY_PATH" | tr ":" "\n" | grep -v dist-packages | paste -sd:)' >> venv/bin/activate

source venv/bin/activate
pip install --upgrade pip setuptools wheel

if [ ! -d "Hierarchical-Localization" ]; then
    git clone --recursive https://github.com/cvg/Hierarchical-Localization.git
fi
pip install -e ./Hierarchical-Localization -r requirements.txt

# torch >= 2.6: nerfstudio carica i checkpoint con weights_only (la tua patch originale)
python -c "import nerfstudio, pathlib; p = pathlib.Path(nerfstudio.__file__).parent / 'utils' / 'eval_utils.py'; text = p.read_text(); p.write_text(text.replace('torch.load(load_path, map_location=\"cpu\")', 'torch.load(load_path, map_location=\"cpu\", weights_only=False)')); print('Patch applicata a:', p)"