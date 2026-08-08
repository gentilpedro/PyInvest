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

## Rodar os testes
```
pip install -r requirements-dev.txt
pytest
```
Os testes (`tests/`) cobrem os filtros, o ranking/score, a formatação da tabela, os presets salvos e a limpeza dos dados do Fundamentus — tudo com dados sintéticos, sem depender de rede ou do Chrome.

## CI/CD
- **PR Checks** (`.github/workflows/pr-checks.yml`): roda em todo push para um PR contra `main` — compila os módulos, roda os testes (`pytest`) e builda o `.exe` como smoke test. Não cria tag nem release.
- **Release** (`.github/workflows/release.yml`): roda a cada push em `main` (ou seja, a cada PR mergeado). Repete as validações, builda o `.exe`, cria automaticamente a próxima tag `vX.Y.Z` (bump de patch) e publica uma GitHub Release com o executável anexado.
