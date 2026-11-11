set -eo pipefail

cd "$(dirname "$0")/.."

if [ "$(id -u)" -eq 0 ]; then SUDO=""; else SUDO="sudo"; fi
export DEBIAN_FRONTEND=noninteractive

TORCH_VERSION="2.1.2"
TORCHVISION_VERSION="0.16.2"
CUDA_TAG="cu118"
HLOC_REF="master" 

echo "[SETUP] Controllo GPU"
if ! command -v nvidia-smi >/dev/null 2>&1; then
    echo "[SETUP] ERRORE: nvidia-smi non trovato, l'istanza non vede la GPU"
    exit 1
fi
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader

if ! command -v nvcc >/dev/null 2>&1; then
    echo "[SETUP] ATTENZIONE: nvcc non trovato. gsplat potrebbe non compilare i kernel CUDA."
    echo "[SETUP] Usa un'immagine '-devel' (es. nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04)."
fi

echo "[SETUP] Pacchetti di sistema"
$SUDO apt-get update
$SUDO apt-get install -y --no-install-recommends \
    software-properties-common build-essential cmake ninja-build git wget curl \
    ffmpeg libusb-1.0-0 libgl1 libglib2.0-0

if ! command -v python3.10 >/dev/null 2>&1; then
    $SUDO add-apt-repository ppa:deadsnakes/ppa -y
    $SUDO apt-get update
fi
$SUDO apt-get install -y python3.10 python3.10-venv python3.10-dev

echo "[SETUP] Virtualenv"
if [ ! -d "venv" ]; then
    python3.10 -m venv venv
fi

source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel

echo "[SETUP] PyTorch ${TORCH_VERSION}+${CUDA_TAG}"
pip install "torch==${TORCH_VERSION}" "torchvision==${TORCHVISION_VERSION}" \
    --index-url "https://download.pytorch.org/whl/${CUDA_TAG}"

echo "[SETUP] Hierarchical-Localization"
if [ ! -d "Hierarchical-Localization" ]; then
    git clone --recursive https://github.com/cvg/Hierarchical-Localization.git
fi
(cd Hierarchical-Localization && git checkout "$HLOC_REF" && git submodule update --init --recursive && pip install -e .)

echo "[SETUP] Requirements"
pip install -r requirements.txt

echo "[SETUP] Verifica finale"
python - <<'EOF'
import torch, pycolmap, hloc, nerfstudio, gsplat, cv2
print("torch", torch.__version__, "| CUDA build", torch.version.cuda)
assert torch.cuda.is_available(), "torch non vede la GPU"
x = torch.zeros(1, device="cuda")  # fallisce se la GPU non e' supportata da questa build
print("GPU:", torch.cuda.get_device_name(0), "| capability", torch.cuda.get_device_capability(0))
print("pycolmap", pycolmap.__version__, "| gsplat", gsplat.__version__, "| opencv", cv2.__version__)
EOF

echo "[SETUP] Completato. Attiva l'ambiente con: source venv/bin/activate"