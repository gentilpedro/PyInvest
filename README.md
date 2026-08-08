# AnaliseDeCotasXLS
Programa para verificar melhores bolsas para compra

## Rodar em desenvolvimento
```
pip install -r requirements.txt
python main.py
```

## Gerar o executável (.exe)
```
pip install -r requirements-dev.txt
python build_app.py
```
O executável fica em `dist/PyInvest.exe` (single-file, sem console). Se algo travar antes da janela abrir, um `pyinvest_error.log` é escrito ao lado do .exe com o erro.
