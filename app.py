import streamlit as st
from openai import OpenAI

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

st.markdown("""
<style>
    .main > div { padding-top: 1.2rem; }
    .header-box {
        background: #1558b0;
        color: white;
        padding: 14px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .stTextArea textarea {
        font-size: 14px;
        line-height: 1.7;
        font-family: 'Segoe UI', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-box">
    <strong style="font-size:18px">⚕️ Anamnese Otorrino</strong><br>
    <span style="font-size:13px;opacity:0.85">
        Dr. Glauber Tercio de Almeida · CRM 24537PR | RQE 31190
    </span>
</div>
""", unsafe_allow_html=True)

api_key = st.secrets.get("OPENAI_API_KEY", None)
if not api_key:
    with st.sidebar:
        st.header("🔑 Configuração")
        api_key = st.text_input("Chave de API OpenAI", type="password", placeholder="sk-...")

# ── Componente de voz ────────────────────────────────────────────────────────
# Injeta HTML/JS com SpeechRecognition e devolve o texto via st.query_params
voice_component = """
<style>
    #mic-container {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 8px;
    }
    #mic-btn {
        display: flex;
        align-items: center;
        gap: 7px;
        padding: 8px 18px;
        border: none;
        border-radius: 20px;
        background: #edf4fd;
        color: #1558b0;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        font-family: 'Segoe UI', sans-serif;
        transition: all 0.15s;
    }
    #mic-btn.recording {
        background: #e53e3e;
        color: white;
        box-shadow: 0 0 0 3px rgba(229,62,62,0.25);
    }
    #mic-status {
        font-size: 12px;
        color: #888;
        font-family: 'Segoe UI', sans-serif;
        font-style: italic;
    }
    #mic-status.active { color: #c53030; }
    #dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #e53e3e;
        display: none;
        animation: pulse 1s ease-in-out infinite;
    }
    #dot.visible { display: inline-block; }
    @keyframes pulse {
        0%,100% { opacity:1; transform:scale(1); }
        50%      { opacity:0.4; transform:scale(1.4); }
    }
</style>

<div id="mic-container">
    <button id="mic-btn" onclick="toggleMic()">🎤 Ditar</button>
    <span id="dot"></span>
    <span id="mic-status">Clique para ditar o relato por voz</span>
</div>

<!-- Área que recebe o texto transcrito -->
<textarea id="voice-output" style="
    width:100%; min-height:200px; padding:12px;
    font-size:14px; line-height:1.7;
    font-family:'Segoe UI',sans-serif;
    border:1.5px solid #dde3ec; border-radius:8px;
    outline:none; resize:vertical; box-sizing:border-box;
    color:#1a1a1a; background:#fff;
" placeholder="O texto ditado aparecerá aqui. Você também pode digitar ou colar diretamente."></textarea>

<div style="margin-top:8px; display:flex; gap:8px;">
    <button onclick="sendToStreamlit()" style="
        flex:1; padding:11px; border:none; border-radius:8px;
        background:#1558b0; color:white; font-size:14px;
        font-weight:600; cursor:pointer; font-family:'Segoe UI',sans-serif;
    ">⚙️ Organizar Anamnese</button>
    <button onclick="clearAll()" style="
        padding:11px 16px; border:1px solid #ccd4de; border-radius:8px;
        background:transparent; color:#667788; font-size:13px;
        font-weight:500; cursor:pointer; font-family:'Segoe UI',sans-serif;
    ">Limpar</button>
</div>

<script>
let recognition = null;
let isRecording = false;
let accumulatedText = "";

const btn    = document.getElementById('mic-btn');
const status = document.getElementById('mic-status');
const dot    = document.getElementById('dot');
const output = document.getElementById('voice-output');

// Restaura texto salvo (sobrevive a reruns do Streamlit)
const saved = sessionStorage.getItem('anamnese_relato');
if (saved) output.value = saved;

output.addEventListener('input', () => {
    sessionStorage.setItem('anamnese_relato', output.value);
});

function toggleMic() {
    if (isRecording) stopMic();
    else startMic();
}

function startMic() {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
        status.textContent = '⚠️ Navegador não suporta voz. Use Chrome ou Safari.';
        return;
    }
    accumulatedText = output.value;
    recognition = new SR();
    recognition.lang = 'pt-BR';
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onstart = () => {
        isRecording = true;
        btn.textContent = '⏹ Parar';
        btn.classList.add('recording');
        dot.classList.add('visible');
        status.textContent = 'Gravando... fale o relato';
        status.classList.add('active');
    };

    recognition.onresult = (e) => {
        let interim = '';
        let finalChunk = '';
        for (let i = e.resultIndex; i < e.results.length; i++) {
            const t = e.results[i][0].transcript;
            if (e.results[i].isFinal) finalChunk += t;
            else interim += t;
        }
        if (finalChunk) {
            const sep = accumulatedText && !accumulatedText.endsWith(' ') ? ' ' : '';
            accumulatedText += sep + finalChunk;
        }
        output.value = accumulatedText + (interim ? ' ' + interim : '');
        sessionStorage.setItem('anamnese_relato', output.value);
    };

    recognition.onerror = (e) => {
        if (e.error === 'not-allowed')
            status.textContent = '⚠️ Permissão de microfone negada.';
        else if (e.error !== 'no-speech')
            status.textContent = '⚠️ Erro: ' + e.error;
        stopMic();
    };

    recognition.onend = () => {
        if (isRecording) recognition.start(); // mantém contínuo
    };

    recognition.start();
}

function stopMic() {
    isRecording = false;
    if (recognition) { recognition.onend = null; recognition.stop(); recognition = null; }
    btn.innerHTML = '🎤 Ditar';
    btn.classList.remove('recording');
    dot.classList.remove('visible');
    status.textContent = 'Gravação encerrada.';
    status.classList.remove('active');
    output.value = accumulatedText;
    sessionStorage.setItem('anamnese_relato', output.value);
}

function sendToStreamlit() {
    if (isRecording) stopMic();
    const text = output.value.trim();
    if (!text) { status.textContent = '⚠️ Digite ou dite algum relato primeiro.'; return; }
    // Envia via query param para o Streamlit relê
    const url = new URL(window.parent.location.href);
    url.searchParams.set('relato', encodeURIComponent(text));
    window.parent.history.replaceState({}, '', url);
    // Dispara evento customizado que o Streamlit captura
    window.parent.postMessage({type: 'streamlit:setComponentValue', value: text}, '*');
}

function clearAll() {
    if (isRecording) stopMic();
    accumulatedText = '';
    output.value = '';
    sessionStorage.removeItem('anamnese_relato');
    status.textContent = 'Clique para ditar o relato por voz';
}
</script>
"""

col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown("**📝 Relato da Consulta**")

    # Componente de voz
    from streamlit.components.v1 import html as st_html
    st_html(voice_component, height=340, scrolling=False)

    st.caption("💡 Dica: o texto ditado fica salvo mesmo se a página recarregar.")

    # Campo de texto fallback + botão principal Streamlit
    st.markdown("---")
    st.markdown("**Ou cole/edite o texto aqui e processe:**")
    relato_texto = st.text_area(
        label="relato_fallback",
        label_visibility="collapsed",
        placeholder="Cole ou digite o relato aqui como alternativa...",
        height=150,
        key="relato_fallback",
    )
    processar = st.button(
        "⚙️ Organizar (texto acima)",
        type="primary",
        use_container_width=True,
        disabled=not relato_texto.strip() or not api_key,
    )

with col2:
    st.markdown("**📋 Anamnese Estruturada**")

    if "resultado" not in st.session_state:
        st.session_state.resultado = ""

    if processar and relato_texto.strip() and api_key:
        with st.spinner("Organizando anamnese..."):
            try:
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user",   "content": relato_texto},
                    ],
                    temperature=0.2,
                    max_tokens=1500,
                )
                st.session_state.resultado = response.choices[0].message.content
            except Exception as e:
                st.error(f"Erro: {e}")

    if st.session_state.resultado:
        st.markdown(st.session_state.resultado)
        st.divider()
        st.text_area(
            "📋 Selecione tudo (Ctrl+A) e copie (Ctrl+C):",
            value=st.session_state.resultado,
            height=220,
            key="copy_area",
        )
        if st.button("🗑️ Limpar resultado", use_container_width=True):
            st.session_state.resultado = ""
            st.rerun()
    else:
        st.markdown("""
        <div style="text-align:center;color:#aab4be;padding:60px 20px;">
            <div style="font-size:40px">📋</div>
            <p style="margin-top:10px;font-size:14px">A anamnese organizada aparecerá aqui</p>
            <p style="font-size:12px;color:#c8d0d8">Use "modo direto" para só o texto final</p>
        </div>
        """, unsafe_allow_html=True)

    if not api_key:
        st.warning("⚠️ Insira sua chave de API no painel lateral.")
