import os
from pathlib import Path
import shutil
from typing import Type

class Logger:
    def log(self, messagge: str) -> None:
        prefix = getattr(self, 'log_name', self.__class__.__name__)
        print(f'[{prefix}] {messagge}')

def data_detection(folder: Path, exception_type: Type[Exception]) -> int:
    if not os.path.isdir(folder):
        raise exception_type(f"La cartella non e' stata trovata: {folder}") 

    content: list[str] = os.listdir(folder)
    
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
            target = folder / item

            if os.path.isfile(target) or os.path.islink(target):
                os.remove(target)

            elif os.path.isdir(target):
                shutil.rmtree(target)
    except Exception as e:
        raise exception_type(f"Impossibile pulire la cartella di output: {folder}") from e

def arrange_model(model_out: Path, sparse_out: Path, exception_type: Type[Exception]) -> None:
    if (model_out / 'cameras.bin').exists():
            return
    
    if not (sparse_out / 'cameras.bin').exists():
        raise exception_type(f'File bin non trovati in {sparse_out}')

    model_out.mkdir(parents=True, exist_ok=True)
    for item in list(sparse_out.iterdir()):
        if item.is_file():
            shutil.move(str(item), str(model_out / item.name))

def ask_to_continue() -> bool:
    user_input = input('[SYSTEM] Si vuole continuare con la pipeline ? (y/n): ').strip().lower()
    return user_input == 'y'

