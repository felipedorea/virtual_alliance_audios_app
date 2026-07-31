# 🎧 Virtual Alliance Boarding Audios

> Player de áudios de cabine para tripulantes da **Virtual Alliance** — reproduza anúncios de bordo organizados por etapa de voo de forma simples e prática.

---

## 📸 Visão Geral

Aplicativo desktop desenvolvido em **Python + Flet**, com interface escura e moderna, que permite reproduzir áudios de cabine separados por fases do voo: Boas-Vindas, Decolagem, Cruzeiro, Serviço de Bordo, Descida, Pouso, Desembarque e Boas-Vindas à Chegada.

---

## ✨ Funcionalidades

- 🗂️ **8 categorias de voo** organizadas em abas (Boas-Vindas Partida, Decolagem, Cruzeiro, Serv. Bordo, Descida, Pouso, Desembarque, Boas-Vindas Chegada)
- ▶️ **Reprodução de áudios** com barra de progresso em tempo real
- 🔊 **Controle de volume** ajustável via slider
- 🔍 **Busca em tempo real** por nome de faixa
- 🔄 **Atualização da lista** sem reiniciar o app
- 🎵 Suporte a formatos: **MP3, WAV, OGG, M4A, FLAC**
- 📁 Pasta de áudios criada automaticamente em **Documentos**

---

## 🖥️ Requisitos do Sistema

- **Sistema Operacional:** Windows
- **Python:** 3.10 ou superior

---

## 🚀 Instalação e Execução

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/virtual_alliance_audios_app.git
cd virtual_alliance_audios_app
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Execute o aplicativo

```bash
python main.py
```

---

## 📦 Build do Executável (opcional)

Para gerar um `.exe` standalone com PyInstaller:

```bash
pyinstaller --onefile --windowed --name "VirtualAlliancePlayer" --collect-all flet --add-data "logo.png;." main.py
```

O executável gerado estará em `dist/VirtualAlliancePlayer.exe`.

---

## 📁 Estrutura de Pastas dos Áudios

Na **primeira execução**, o app cria automaticamente a seguinte estrutura em **Documentos**:

```
Documentos/
└── Virtual Alliance Boarding Audios/
    └── audios/
        ├── 0. Boas-Vindas Partida/
        ├── 1. Decolagem/
        ├── 2. Cruzeiro/
        ├── 3. Serv. Bordo/
        ├── 4. Descida/
        ├── 5. Pouso/
        ├── 6. Desembarque/
        └── 7. Boas-Vindas Chegada/
```

Basta copiar seus arquivos de áudio para a pasta correspondente a cada fase do voo.

---

## 🎵 Como Adicionar Áudios

1. Abra a pasta:
   ```
   Documentos/Virtual Alliance Boarding Audios/audios
   ```
2. Copie os arquivos de áudio para a **subpasta da fase desejada**.
3. No aplicativo, clique no botão **🔄 Atualizar** para recarregar a lista.

> **Formatos suportados:** `.mp3`, `.wav`, `.ogg`, `.m4a`, `.flac`

---

## ⚠️ Observações Importantes

- Não renomeie a pasta `audios`.
- Caso nenhum áudio apareça, confirme que os arquivos estão dentro da subpasta correta e possuem uma extensão suportada.
- O aplicativo é exclusivo para **Windows** (utiliza API `SHGetFolderPathW` para localizar Documentos).

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Função |
|---|---|
| [Flet](https://flet.dev/) | Framework de UI (Flutter via Python) |
| [pygame-ce](https://pyga.me/) | Engine de reprodução de áudio |
| [mutagen](https://mutagen.readthedocs.io/) | Leitura de metadados de áudio (duração) |
| [PyInstaller](https://pyinstaller.org/) | Geração do executável `.exe` |

---

## 📄 Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
