# anamnese-otorrino

Aplicativo Streamlit para geração de anamnese estruturada em otorrinolaringologia, com suporte a ditado por voz, entrada livre de texto e organização assistida por IA (OpenAI API).

## Funcionalidades

- **Ditado por voz**: reconhecimento de fala em português via Web Speech API, com transcrição contínua e acumulativa
- **Entrada de texto livre**: cole ou digite o relato clínico diretamente no campo de texto
- **Organização por IA**: estrutura automaticamente o relato em anamnese padronizada usando GPT-4o-mini (OpenAI API)
- **Formato padronizado**: gera HMA, Histórico Pregresso, Exame Físico, Hipótese Diagnóstica e Conduta
- **Suporte a abreviações clínicas**: interpreta siglas como VNE, VFL, HMA, OMA, RSA, HCCII e outras
- **Modo direto**: opção para retornar só o texto final, sem comentários adicionais
- **Interface responsiva**: layout em duas colunas com visualização simultânea do relato e do resultado
- **Cópia facilitada**: área de texto com seleção rápida para copiar a anamnese gerada

## Tecnologias

- [Streamlit](https://streamlit.io/)
- [OpenAI API](https://platform.openai.com/) — modelo `gpt-4o-mini`
- Web Speech API (reconhecimento de voz nativo do navegador)

## Como usar

### Executar localmente

1. Clone o repositório:
```bash
git clone https://github.com/Glauber-Almeida/anamnese-otorrino.git
cd anamnese-otorrino
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure sua chave de API em `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "sk-..."
```

4. Execute o aplicativo:
```bash
streamlit run app.py
```

### Deploy no Streamlit Cloud

Publique gratuitamente no [Streamlit Community Cloud](https://streamlit.io/cloud).
Conecte o repositório e adicione `OPENAI_API_KEY` nas configurações de secrets.

---

**Dr. Glauber Tercio de Almeida**
Otorrinolaringologista · CRM 24537PR | RQE 31190
