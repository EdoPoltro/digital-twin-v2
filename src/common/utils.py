import os
from pathlib import Path
import shutil
import subprocess
from typing import Type

class Logger:
    def log(self, messagge: str) -> None:
        prefix = getattr(self, 'log_name', self.__class__.__name__)
        print(f'[{prefix}] {messagge}')

def data_detection(folder: Path, exception_type: Type[Exception]) -> int:
    if not os.path.isdir(folder):
        raise exception_type(f"La cartella non e' stata trovata: {folder}") 

    content: list[str] = [f for f in os.listdir(folder) if not f.startswith('.')]
    
    if len(content) == 0:
        raise exception_type(f"La cartella e' vuota: {folder}")

    return len(content)

def file_detection(file: Path, exception_type: Type[Exception]) -> None:
    if not file.is_file():
        raise exception_type(f"Il file non è stato trovato o non è valido: {file}")
    
    if file.stat().st_size == 0:
        raise exception_type(f"Il file è vuoto: {file}")


def folder_cleaning(folder: Path, exception_type: Type[Exception]) -> None:
    try:
        os.makedirs(folder, exist_ok=True)
        for item in os.listdir(folder):
            if item.startswith('.'):
                continue
            target = folder / item

            if os.path.isfile(target) or os.path.islink(target):
                os.remove(target)

            elif os.path.isdir(target):
                shutil.rmtree(target)
    except Exception as e:
        raise exception_type(f"Impossibile pulire la cartella di output: {folder}")

def arrange_model(model_out: Path, sparse_out: Path, exception_type: Type[Exception]) -> None:
    
    # fase 1, controlla se i file sono gia nella cartella giusta
    if (model_out / 'cameras.bin').exists() or (model_out / 'cameras.txt').exists():
        return

    # fase 2, controlla se i file sono in sparse o in una sotto cartella
    source_dir = None
    if (sparse_out / 'cameras.bin').exists() or (sparse_out / 'cameras.txt').exists():
        source_dir = sparse_out
    else:
        for subfolder in sparse_out.rglob('*'):
            if subfolder.is_dir() and subfolder != model_out:
                if (subfolder / 'cameras.bin').exists() or (subfolder / 'cameras.txt').exists():
                    source_dir = subfolder
                    break

    # Errore
    if not source_dir:
        raise exception_type(f"File del modello COLMAP (cameras.bin/txt) non trovati in {sparse_out}")

    # 3. Fase 3, creo la cartella 0 se non esiste e sposto i files
    model_out.mkdir(parents=True, exist_ok=True)

    colmap_files = [
        'cameras.bin', 'images.bin', 'points3D.bin', 'frames.bin', 'rigs.bin',
        'cameras.txt', 'images.txt', 'points3D.txt', 'frames.txt', 'rigs.xt',
        'project.ini'
    ]
    
    moved_any = False
    for file_name in colmap_files:
        src_file = source_dir / file_name
        if src_file.exists():
            dst_file = model_out / file_name
            if src_file != dst_file:
                shutil.move(str(src_file), str(dst_file))
            moved_any = True

    if not moved_any:
        raise exception_type(f"Nessun file di modello valido spostato da {source_dir} a {model_out}")

def ask_to_continue() -> bool:
    user_input = input('[SYSTEM] Si vuole continuare con la pipeline ? (y/n): ').strip().lower()
    return user_input == 'y'

def run_command(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(command, check=True)
