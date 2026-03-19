import streamlit as st
from openai import OpenAI
import os


def get_api_key():
    # Streamlit Cloud (secrets) ou .env local
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv("OPENAI_API_KEY")


client = OpenAI(api_key=get_api_key())
MODEL = "gpt-4o"

SYSTEM_PROMPT = """Você é um pesquisador sênior em psicologia analítica com domínio profundo das Obras Completas de C.G. Jung (Collected Works, volumes I–XX).

Seu papel é produzir textos técnicos, densos e rigorosamente fiéis ao pensamento junguiano, que servirão como base para depois serem adaptados em conteúdo de divulgação (posts e reels).

Diretrizes para o texto:
- Escreva com profundidade teórica real. Não simplifique, não generalize, não parafraseie de forma rasa. O texto deve soar como um artigo acadêmico ou capítulo de livro especializado.
- Use a terminologia técnica de Jung com precisão: individuação, Self, Sombra, Anima/Animus, função transcendente, compensação, tipos psicológicos, arquétipo, inconsciente coletivo, complexo, etc. — sempre no sentido exato que Jung empregava.
- Inclua citações diretas de Jung entre aspas, indicando a obra de origem (ex: "Aion", §123; "Tipos Psicológicos", OC vol. VI; "Psicologia e Alquimia", OC vol. XII). Quanto mais citações diretas e referências específicas, melhor.
- Articule os conceitos dentro do sistema teórico de Jung: mostre como se conectam entre si, como evoluíram ao longo da obra, e onde há tensões ou nuances.
- Não misture com outras escolas (Freud, Lacan, etc.) a menos que o usuário peça explicitamente.
- Extensão: seja generoso. Textos de 800–2000 palavras são bem-vindos na primeira versão.

Fluxo de trabalho:
- Na primeira mensagem, produza um rascunho denso e completo sobre o tema pedido.
- Nas mensagens seguintes, refine conforme o feedback do usuário.
- Sempre que apresentar uma nova versão, apresente o texto completo (não parcial).
- Seja direto no feedback — não enrole com explicações desnecessárias."""


def chat(messages: list) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.5,
    )
    return response.choices[0].message.content


def generate_instagram(text: str, num_slides: int) -> str:
    prompt = f"""Você é um criador de conteúdo especializado em psicologia junguiana para Instagram.

Com base no texto final abaixo, crie um roteiro de carrossel para Instagram com {num_slides} slides.

IMPORTANTE: Mantenha o mesmo nível de profundidade, rigor terminológico e tom do texto de entrada. Não simplifique, não dilua, não torne genérico. O carrossel deve preservar a densidade conceitual e as citações diretas de Jung com referências (obra, parágrafo). É um carrossel para um público que quer conteúdo técnico de verdade, não divulgação rasa.

Para cada slide, forneça:
- **Slide N — [Título curto]**
- Texto do slide (máximo 180 palavras): mesmo registro linguístico do texto-fonte — técnico, preciso, denso.
- Citações diretas de Jung entre aspas com referência à obra de origem.

Estrutura sugerida:
- Slide 1: capa com título impactante que reflita o conceito central.
- Slides intermediários: desenvolvimento conceitual com citações e articulação teórica.
- Último slide: reflexão de fechamento ou provocação intelectual (pode incluir CTA discreto).

TEXTO FINAL:
{text}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
    )
    return response.choices[0].message.content


def generate_reels(text: str, duration_secs: int) -> str:
    prompt = f"""Você é um roteirista de conteúdo especializado em psicologia junguiana para Reels/vídeos curtos do Instagram.

Com base no texto final abaixo, crie um roteiro de Reels com duração aproximada de {duration_secs} segundos.

Estrutura do roteiro:
- **[Tempo] — [Descrição da cena/ação]**
- Texto da narração/legenda para aquele momento.
- Indicações visuais (texto na tela, transições, etc.) entre colchetes.

IMPORTANTE: Mantenha o mesmo nível de profundidade, rigor terminológico e tom do texto de entrada. Não simplifique, não dilua. O roteiro deve preservar a densidade conceitual e as citações de Jung com referências. É um Reels para um público que quer conteúdo técnico real.

Diretrizes:
- Gancho forte nos primeiros 3 segundos — pode ser uma citação impactante de Jung ou uma provocação conceitual.
- Citações de Jung entre aspas com referência à obra.
- Encerre com reflexão de fechamento ou provocação intelectual (CTA discreto).
- Linguagem adequada para narração em voz, mas sem perder o rigor — frases podem ser curtas e ritmadas, mas precisas.

TEXTO FINAL:
{text}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
    )
    return response.choices[0].message.content


# ── Interface Streamlit ──────────────────────────────────────────────

st.set_page_config(page_title="Citador de Jung", page_icon="📖", layout="wide")
st.title("📖 Citador de Jung")

# Sidebar
with st.sidebar:
    st.header("Configurações")
    num_slides = st.slider("Slides do carrossel", min_value=5, max_value=15, value=8)
    reels_duration = st.slider("Duração do Reels (segundos)", min_value=15, max_value=90, value=60)
    st.divider()
    if st.button("🔄 Recomeçar", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# Estado
if "stage" not in st.session_state:
    st.session_state.stage = "chat"  # "chat" ou "generate"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "final_text" not in st.session_state:
    st.session_state.final_text = None
if "instagram" not in st.session_state:
    st.session_state.instagram = None
if "reels" not in st.session_state:
    st.session_state.reels = None


def validate_api_key():
    api_key = get_api_key()
    if not api_key or api_key == "sua-chave-aqui":
        st.error("Configure sua chave da OpenAI.")
        return False
    return True


# ── ETAPA 1: Chat ────────────────────────────────────────────────────

if st.session_state.stage == "chat":
    st.caption("Etapa 1 — Converse até chegar no texto ideal. Depois, avance para gerar o conteúdo.")

    # Exibir histórico
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
        elif msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])

    # Botão de avançar (aparece depois da primeira resposta)
    if len(st.session_state.messages) >= 2:
        if st.button("✅ Texto aprovado — avançar para geração", use_container_width=True):
            # Pega a última mensagem do assistente como texto final
            for msg in reversed(st.session_state.messages):
                if msg["role"] == "assistant":
                    st.session_state.final_text = msg["content"]
                    break
            st.session_state.stage = "generate"
            st.rerun()

    # Input do chat
    user_input = st.chat_input("Descreva o tema ou dê feedback sobre o texto...")

    if user_input and validate_api_key():
        st.session_state.messages.append({"role": "user", "content": user_input})

        api_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                reply = chat(api_messages)
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()


# ── ETAPA 2: Geração ─────────────────────────────────────────────────

elif st.session_state.stage == "generate":
    st.caption("Etapa 2 — Escolha o formato de conteúdo para gerar.")

    with st.expander("📄 Texto final aprovado", expanded=False):
        st.markdown(st.session_state.final_text)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📱 Gerar carrossel Instagram", use_container_width=True):
            with st.spinner("Gerando carrossel..."):
                st.session_state.instagram = generate_instagram(
                    st.session_state.final_text, num_slides
                )

    with col2:
        if st.button("🎬 Gerar roteiro de Reels", use_container_width=True):
            with st.spinner("Gerando roteiro de Reels..."):
                st.session_state.reels = generate_reels(
                    st.session_state.final_text, reels_duration
                )

    # Exibir resultados
    if st.session_state.instagram:
        st.header("Roteiro de Carrossel")
        st.markdown(st.session_state.instagram)
        st.download_button(
            "📥 Baixar roteiro carrossel (.txt)",
            st.session_state.instagram,
            file_name="carrossel_jung.txt",
            mime="text/plain",
        )

    if st.session_state.reels:
        st.header("Roteiro de Reels")
        st.markdown(st.session_state.reels)
        st.download_button(
            "📥 Baixar roteiro Reels (.txt)",
            st.session_state.reels,
            file_name="reels_jung.txt",
            mime="text/plain",
        )

    st.divider()
    if st.button("⬅️ Voltar ao chat para ajustar o texto"):
        st.session_state.stage = "chat"
        st.session_state.instagram = None
        st.session_state.reels = None
        st.rerun()
