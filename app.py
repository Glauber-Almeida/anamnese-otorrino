import streamlit as st
from openai import OpenAI

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Anamnese Otorrino",
    page_icon="⚕️",
    layout="wide",
)

SYSTEM_PROMPT = """Você é um assistente especializado em otorrinolaringologia do Dr. Glauber Tercio de Almeida. Organize o relato clínico em anamnese estruturada, seguindo EXATAMENTE este formato:

### História da Moléstia Atual (HMA)
[Descrição da queixa, tempo de evolução, sintomas, fatores agravantes/atenuantes. Sem hipótese diagnóstica aqui.]

### Histórico Pregresso
- **Comorbidades:** [ou "Nega"]
- **Medicações de Uso Contínuo:** [ou "Nega"]
- **Alergias:** [ou "Nega"]
- **Cirurgias Prévias:** [ou "Nega"]
- **Tabagismo / Etilismo:** [ou "Nega"]
- **Histórico Familiar:** [ou "Sem alterações relevantes"]

### Exame Físico
- **Oroscopia:** [achados]
- **Rinoscopia:** [achados] (OMITIR se houver Videonasoendoscopia)
- **Otoscopia:** [achados]
- **Videonasoendoscopia:** [achados] (incluir só se mencionado)
- **Videolaringoscopia:** [achados] (incluir só se mencionado)

### Hipótese Diagnóstica
- [Diagnóstico(s). Se em investigação: "X a esclarecer"]

### Conduta
1. **Prescrição médica:** [medicamentos, doses, duração]
2. **Solicitação de exames:** [só se solicitado]
3. **Encaminhamentos:** [se houver]
4. **Orientações gerais:** [cuidados, retorno]

**Dr. Glauber Tercio de Almeida**
**Otorrinolaringologista**
**CRM 24537PR | RQE 31190**

ABREVIAÇÕES: VNE=Videonasoendoscopia, VFL=Videolaringoscopia, Oro=Oroscopia, Rino=Rinoscopia, Oto=Otoscopia, HD=Hipótese Diagnóstica, CD=Conduta, HCCII=Hipertrofia de cornetos inferiores, IVAS=Infecção de vias aéreas superiores, RSA=Rinossinusite aguda, OMA=Otite média aguda, AG1-4=Amígdalas grau 1-4.

REGRAS:
- Omitir Rinoscopia quando há Videonasoendoscopia
- Omitir Histórico Pregresso e Exame Físico em remoções simples de cerume
- "modo direto" = só a anamnese, sem comentários extras"""

# ── Estilo CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main > div { padding-top: 1.5rem; }
    .stTextArea textarea {
        font-size: 14px;
        line-height: 1.7;
        font-family: 'Segoe UI', sans-serif;
    }
    .resultado {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 20px 24px;
        font-size: 14px;
        line-height: 1.75;
        font-family: 'Segoe UI', sans-serif;
        white-space: pre-wrap;
    }
    .header-box {
        background: #1558b0;
        color: white;
        padding: 14px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-box">
    <strong style="font-size:18px">⚕️ Anamnese Otorrino</strong><br>
    <span style="font-size:13px;opacity:0.85">
        Dr. Glauber Tercio de Almeida · CRM 24537PR | RQE 31190
    </span>
</div>
""", unsafe_allow_html=True)

# ── Chave de API ────────────────────────────────────────────────────────────
# Tenta pegar dos secrets do Streamlit Cloud; se não tiver, pede no sidebar
api_key = st.secrets.get("OPENAI_API_KEY", None)
if not api_key:
    with st.sidebar:
        st.header("🔑 Configuração")
        api_key = st.text_input(
            "Chave de API OpenAI",
            type="password",
            placeholder="sk-...",
            help="Sua chave fica apenas nesta sessão, não é salva."
        )

# ── Layout principal ────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("**📝 Relato da Consulta**")
    relato = st.text_area(
        label="relato",
        label_visibility="collapsed",
        placeholder=(
            "Cole ou digite o relato aqui...\n\n"
            "Ex: Paciente 45 anos, plenitude auricular OD há 5 dias. "
            "Oto: cerume OD. Lavagem sem intercorrências. "
            "Oto pós normal. HD cerume impactado OD. CD remoção e orientações."
        ),
        height=380,
        key="relato_input",
    )

    processar = st.button(
        "⚙️ Organizar Anamnese",
        type="primary",
        use_container_width=True,
        disabled=not relato.strip() or not api_key,
    )

    if not api_key:
        st.caption("⚠️ Insira sua chave de API no painel lateral para continuar.")

with col2:
    st.markdown("**📋 Anamnese Estruturada**")

    if "resultado" not in st.session_state:
        st.session_state.resultado = ""

    if processar and relato.strip() and api_key:
        with st.spinner("Organizando anamnese..."):
            try:
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",   # barato e rápido; troque por gpt-4o se quiser mais qualidade
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": relato},
                    ],
                    temperature=0.2,
                    max_tokens=1500,
                )
                st.session_state.resultado = response.choices[0].message.content
            except Exception as e:
                st.error(f"Erro: {e}")

    if st.session_state.resultado:
        # Exibe formatado
        st.markdown(st.session_state.resultado)

        st.divider()

        # Botão de copiar — abre text_area selecionável
        st.text_area(
            "Texto para copiar (selecione tudo com Ctrl+A):",
            value=st.session_state.resultado,
            height=200,
            key="copy_area",
        )
        st.caption("Selecione todo o texto acima (Ctrl+A) e copie (Ctrl+C) para colar no prontuário.")

    else:
        st.markdown("""
        <div style="text-align:center;color:#aab4be;padding:80px 20px;">
            <div style="font-size:40px">📋</div>
            <p style="margin-top:10px;font-size:14px">
                A anamnese organizada aparecerá aqui
            </p>
            <p style="font-size:12px;color:#c8d0d8">
                Use "modo direto" no relato para receber só o texto
            </p>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.resultado:
        if st.button("🗑️ Limpar", use_container_width=True):
            st.session_state.resultado = ""
            st.rerun()
