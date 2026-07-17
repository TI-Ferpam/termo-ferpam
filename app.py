import streamlit as st
import streamlit.components.v1 as components
import uuid
import datetime
import pytz
import os  # <-- Adicionado para evitar erro na deleção do arquivo temporário do PDF
from io import BytesIO
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from fpdf import FPDF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from streamlit_javascript import st_javascript

# 🔥 INTERCEPTAÇÃO E CORREÇÃO DE COMPATIBILIDADE HTTP2 (MATA O BUG DO TYPEERROR & ATTRIBUTEERROR)
import httpx

# Verifica qual o nome correto da classe na versão instalada do httpx
if hasattr(httpx, "Client"):
    TargetClient = httpx.Client
elif hasattr(httpx, "SyncClient"):
    TargetClient = httpx.SyncClient
else:
    TargetClient = None

if TargetClient:
    original_init = TargetClient.__init__

    def patched_init(self, *args, **kwargs):
        if "http2" in kwargs:
            kwargs["http2"] = False  # Desativa o HTTP2 que quebra o Python no Streamlit Cloud
        original_init(self, *args, **kwargs)

    TargetClient.__init__ = patched_init

# 🔥 IMPORTAÇÃO DO BANCO DE DADOS CLIENTE DO SUPABASE
from supabase import create_client, Client

# Configurações de layout
st.set_page_config(page_title="Portal de Assinaturas - Ferpam", page_icon="🏢", layout="centered")

# CSS CUSTOMIZADO
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .termo-doc {
        background-color: white; padding: 30px; border-radius: 8px;
        border: 1px solid #cbd5e1; color: #334155; font-size: 14.5px;
        line-height: 1.6; margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    .termo-doc p {
        margin-top: 0px !important;
        margin-bottom: 12px !important;
        padding: 0px !important;
    }
    iframe[title="streamlit_drawable_canvas.st_canvas"] {
        height: 250px !important;
        min-height: 250px !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 8px !important;
        background-color: #ffffff !important;
        display: block !important;
    }
    .sucesso-box {
        background-color: #f0fdf4; border: 1px solid #bbf7d0; color: #166534;
        padding: 30px; border-radius: 8px; text-align: center; margin-top: 50px;
    }
    .login-box {
        background-color: white; padding: 25px; border-radius: 8px;
        border: 1px solid #cbd5e1; margin-top: 40px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)


# 🔥 INICIALIZAÇÃO DA CONEXÃO DO SUPABASE
@st.cache_resource
def iniciar_banco() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = iniciar_banco()


def renderizar_termo_tela():
    html_conteudo = """<div class="termo-doc">
<h3 style="text-align:center; margin-top:0; margin-bottom:20px; color: #0f172a;">TERMO DE RESPONSABILIDADE E USO DOS RECURSOS DE TI</h3>
<p>Este Termo tem como objetivo estabelecer as diretrizes para o uso adequado dos recursos de Tecnologia da Informação disponibilizados pela Ferpam, garantindo a segurança, a integridade e a confidencialidade das informações da empresa.</p>
<p>Ao receber acesso aos sistemas, equipamentos e recursos tecnológicos da Ferpam, o colaborador declara estar ciente e concorda com as seguintes responsabilidades:</p>
<p><b>1. Confidencialidade das Informações</b><br>Todas as informações acessadas durante as atividades profissionais são de uso exclusive da Ferpam e não devem ser divulgadas, compartilhadas ou utilizadas para fins pessoais ou externos sem autorização.</p>
<p><b>2. Instalação de Programas e Equipamentos</b><br>A instalação de programas, aplicativos, extensões, equipamentos ou qualquer alteração nos computadores e dispositivos da empresa deve ser realizada exclusivamente pelo setor de TI. Não é permitido instalar softwares ou aplicativos por conta própria.</p>
<p><b>3. Uso de E-mails e Dispositivos Pessoais</b><br>O uso de e-mails pessoais, pendrives, cartões de memória, serviços de armazenamento em nuvem e aplicativos de comunicação para manipulação de informações da empresa deve ocorrer apenas quando autorizado pela gestão ou pelo setor de TI.</p>
<p><b>4. Uso da Internet</b><br>O acesso à internet disponibilizado pela empresa deve ser utilizado prioritariamente para atividades relacionadas ao trabalho. O acesso a conteúdos inadequados, ilegais ou que possam comprometer a segurança da empresa é proibido.</p>
<p><b>5. Senhas de Acesso</b><br>Las senhas fornecidas para acesso aos sistemas são pessoais e intransferíveis. Não é permitido compartilhar senhas com outros colaboradores ou terceiros.</p>
<p><b>6. Segurança das Senhas</b><br>O colaborador compromete-se a:<br>
- Não anotar senhas em locais visíveis;<br>
- Não salvar senhas em arquivos desprotegidos;<br>
- Alterar a senha sempre que houver suspeita de comprometimento;<br>
- Utilizar senhas seguras.</p>
<p><b>7. E-mails Suspeitos</b><br>O colaborador não deve abrir links, anexos ou mensagens suspeitas recebidas por e-mail, WhatsApp ou outros meios de comunicação. Em caso de dúvida, o setor de TI deverá ser acionado antes de qualquer interação.</p>
<p><b>8. Proteção dos Equipamentos</b><br>Sempre que se ausentar do local de trabalho, o colaborador deverá bloquear o computador ou encerrar a sessão para evitar acessos não autorizados.</p>
<p><b>9. Uso dos Equipamentos da Empresa</b><br>Os equipamentos disponibilizados pela Ferpam destinam-se às atividades profissionais e devem ser utilizados de forma responsável e cuidadosa.</p>
<p><b>10. Monitoramento</b><br>A Ferpam poderá realizar monitoramento dos recursos tecnológicos disponibilizados, incluindo acessos à internet, utilização dos sistemas corporativos e demais recursos de TI, visando garantir a segurança das informações e a continuidade das operações.</p>
<p><b>11. Comunicação de Incidentes</b><br>Qualquer suspeita de vírus, golpe, tentativa de fraude, perda de equipamento ou incidente relacionado à segurança da informação deverá ser comunicada imediatamente ao setor de TI.</p>
<p><b>12. Responsabilidade do Colaborador</b><br>O descumprimento das diretrizes estabelecidas neste termo poderá resultar em medidas administrativas, conforme as normas internas da empresa e a legislação vigente.</p>
<hr style="border:0; border-top: 1px solid #cbd5e1; margin: 15px 0;">
<p>Declaro estar ciente das orientações acima e comprometo-me a cumprir as normas de utilização dos recursos de Tecnologia da Informação disponibilizados pela Ferpam.</p>
</div>"""
    st.markdown(html_conteudo, unsafe_allow_html=True)


def gerar_pdf_contrato(nome, cargo, setor, data_hora, assinatura_bytes, funcionario_id, ip_cliente="Não capturado", ua_cliente="Não capturado"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "TERMO DE RESPONSABILIDADE E USO DOS RECURSOS DE TI", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 10.5)
    
    intro = (
        "Este Termo tem como objetivo estabelecer las diretrizes para o uso adequado dos recursos de "
        "Tecnologia da Informação disponibilizados pela Ferpam, garantindo a segurança, a integridade "
        "e a confidencialidade das informações da empresa.\n\n"
        "Ao receber acesso aos sistemas, equipamentos e recursos tecnológicos da Ferpam, o colaborador "
        "declara estar ciente e concorda com as seguintes responsabilidades:\n\n"
    )
    pdf.multi_cell(0, 5, intro)

    diretrizes = [
        "1. Confidencialidade das Informações\nTodas as informações acessadas durante as atividades profissionais são de uso exclusivo da Ferpam e não devem ser divulgadas, compartilhadas ou utilizadas para fins pessoais ou externos sem autorização.\n",
        "2. Instalação de Programas e Equipamentos\nA instalação de programas, aplicativos, extensões, equipamentos ou qualquer alteração nos computadores e dispositivos da empresa deve ser realizada exclusivamente pelo setor de TI. Não é permitido instalar softwares ou aplicativos por conta própria.\n",
        "3. Uso de E-mails e Dispositivos Pessoais\nO uso de e-mails pessoais, pendrives, cartões de memória, serviços de armazenamento em nuvem e aplicativos de comunicação para manipulação de informações da empresa deve ocorrer apenas quando autorizado pela gestão ou pelo setor de TI.\n",
        "4. Uso da Internet\nO acesso à internet disponibilizado pela empresa deve ser utilizado prioritariamente para atividades relacionadas ao trabalho. O acesso a conteúdos inadequados, ilegais ou que possam comprometer a segurança da empresa é proibido.\n",
        "5. Senhas de Acesso\nAs senhas fornecidas para acesso aos sistemas são pessoais e intransferíveis. Não é permitido compartilhar senhas com outros colaboradores ou terceiros.\n",
        "6. Segurança das Senhas\nO colaborador compromete-se a:\n- Não anotar senhas em locais visíveis;\n- Não salvar senhas em arquivos desprotegidos;\n- Alterar a senha sempre que houver suspeita de comprometimento;\n- Utilizar senhas seguras.\n",
        "7. E-mails Suspeitos\nO colaborador não deve abrir links, anexos ou mensagens suspeitas recebidas por e-mail, WhatsApp ou outros meios de comunicação. Em caso de dúvida, o setor de TI deverá ser acionado antes de qualquer interação.\n",
        "8. Proteção dos Equipamentos\nSempre que se ausentar do local de trabalho, o colaborador deverá bloquear o computador ou encerrar a sessão para evitar acessos não autorizados.\n",
        "9. Uso dos Equipamentos da Empresa\nOs equipamentos disponibilizados pela Ferpam destinam-se às atividades profissionais e devem ser utilizados de forma responsável e cuidadosa.\n",
        "10. Monitoramento\nA Ferpam poderá realizar monitoramento dos recursos tecnológicos disponibilizados, incluindo acessos à internet, utilização dos sistemas corporativos e demais recursos de TI, visando garantir a segurança das informações e a continuidade das operações.\n",
        "11. Comunicação de Incidentes\nQualquer suspeita de vírus, golpe, tentativa de fraude, perda de equipamento ou incidente relacionado à segurança da informação deverá ser comunicada imediatamente ao setor de TI.\n",
        "12. Responsabilidade do Colaborador\nO descumprimento das diretrizes estabelecidas neste termo poderá resultar em medidas administrativas, conforme as normas internas da empresa e a legislação vigente.\n"
    ]

    for item in diretrizes:
        pdf.multi_cell(0, 5, item)
        pdf.ln(1)

    pdf.ln(2)
    pdf.multi_cell(0, 5, "Declaro estar ciente das orientações acima e comprometo-me a cumpir as normas de utilização dos recursos de Tecnologia da Informação disponibilizados pela Ferpam.\n")
    pdf.ln(4)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_font("Arial", "B", 10.5)
    pdf.cell(0, 6, f"Nome Completo: {nome}", ln=True)
    pdf.cell(0, 6, f"Cargo: {cargo}", ln=True)
    pdf.cell(0, 6, f"Setor: {setor}", ln=True)
    pdf.cell(0, 6, f"Data e Hora do Registro: {data_hora}", ln=True)

    assinatura_temp = f"assinatura_temp_{funcionario_id}.png"
    try:
        with open(assinatura_temp, "wb") as f:
            f.write(assinatura_bytes)
        pdf.ln(3)
        pdf.cell(0, 6, "Assinatura Digitalizada:", ln=True)
        pdf.image(assinatura_temp, x=20, y=pdf.get_y(), w=65)
        pdf.ln(25)
    finally:
        if os.path.exists(assinatura_temp):
            os.remove(assinatura_temp)

    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    pdf.cell(0, 4, f"Metadados de Validação Jurídica (Lei 14.063/2020)", ln=True)
    pdf.cell(0, 4, f"ID de Autenticação do Sistema: {funcionario_id}", ln=True)
    pdf.cell(0, 4, f"Endereço de IP Origem: {ip_cliente}", ln=True)
    pdf.multi_cell(0, 4, f"Assinatura do Dispositivo (User-Agent): {ua_cliente}")

    pdf_bytes = pdf.output(dest="S")
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode("latin1")
    elif isinstance(pdf_bytes, bytearray):
        pdf_bytes = bytes(pdf_bytes)
    return pdf_bytes


def enviar_email(destinatario, nome, link):
    EMAIL = "suporte.ti@ferpam.com.br"
    SENHA = st.secrets["email"]["senha_gmail"] 
    
    mensagem = MIMEMultipart()
    mensagem["From"] = EMAIL
    mensagem["To"] = destinatario
    mensagem["Subject"] = "Assinatura do Termo de Responsabilidade de TI - Ferpam"

    corpo = f"""Olá, {nome}!

Seja bem-vindo(a) à Ferpam.

Para concluir o seu processo de integração, solicitamos a leitura e assinatura digital do Termo de Responsabilidade e Uso dos Recursos de TI.

Clique no link abaixo para acessar o documento e realizar sua assinatura digital:
{link}

Atenciosamente,
Equipe de TI - Ferpam"""
    
    mensagem.attach(MIMEText(corpo, "plain", "utf-8"))

    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(EMAIL, SENHA)
        servidor.sendmail(EMAIL, destinatario, mensagem.as_string())
        servidor.quit()
        return True, "Sucesso"
    except Exception as erro:
        return False, str(erro)


# ---------------- LOGICA DE ROTEAMENTO ----------------
url_id = st.query_params.get("id", None)

if url_id:
    # --- VISÃO DO COLABORADOR ---
    resposta = supabase.table("funcionarios").select("*").eq("id", url_id).execute()
    colaborador = resposta.data[0] if len(resposta.data) > 0 else None
    
    if not colaborador:
        st.error("⚠️ Link de assinatura inválido ou expirado. Entre em contato com o setor de TI.")
    elif colaborador["assinado"]:
        st.markdown(f"""
            <div class="sucesso-box">
                <h1 style="color: #166534; margin-top:0;">✓ Termo Assinado com Sucesso!</h1>
                <p style="font-size: 16px;">Olá <b>{colaborador['nome']}</b>, suas diretrizes de responsabilidade de TI foram registradas.</p>
                <p style="font-size: 14px; color: #65a30d;">Obrigado! Você já pode fechar esta aba.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align: center; color: #0f172a;'>🏢 Assinatura de Termo Digital - Ferpam</h2>", unsafe_allow_html=True)
        st.info(f"Colaborador: {colaborador['nome']} | Cargo: {colaborador['cargo']}")
        
        renderizar_termo_tela()
        
        st.subheader("🖊️ Assine abaixo utilizando o mouse ou o dedo:")

        canvas_result = st_canvas(
            stroke_width=4, stroke_color="#000000", background_color="#FFFFFF",    
            width=680, height=250, drawing_mode="freedraw", key=f"canvas_{url_id}", 
            display_toolbar=False, update_streamlit=True          
        )

        components.html("""
        <script>
            function interceptarEForcarAltura() {
                try {
                    var iframes = window.parent.document.querySelectorAll('iframe[title="streamlit_drawable_canvas.st_canvas"]');
                    iframes.forEach(function(iframe) {
                        if (iframe.getAttribute('height') !== '250') {
                            iframe.setAttribute('height', '250');
                            iframe.style.setProperty('height', '250px', 'important');
                        }
                    });
                } catch (e) {}
            }
            setInterval(interceptarEForcarAltura, 200);
        </script>
        """, height=0, width=0)

        ip_capturado = st_javascript("fetch('https://api.ipify.org?format=json').then(r => r.json()).then(d => d.ip)")
        ua_capturado = st_javascript("window.navigator.userAgent")

        if st.button("💾 Enviar Assinatura Concluída", type="primary", use_container_width=True):
            tem_desenho = False
            if canvas_result.json_data is not None and len(canvas_result.json_data.get("objects", [])) > 0:
                tem_desenho = True

            if not tem_desenho:
                st.error("O quadro de assinatura está vazio. Por favor, faça sua assinatura antes de clicar em enviar.")
            else:
                ip_final = str(ip_capturado) if (ip_capturado and ip_capturado != "False") else "IP Não identificado"
                ua_final = str(ua_capturado) if (ua_capturado and ua_capturado != "False") else "Dispositivo Desconhecido"

                img_array = canvas_result.image_data.astype("uint8")
                img = Image.fromarray(img_array)
                background = Image.new("RGBA", img.size, (255, 255, 255))
                img_final = Image.alpha_composite(background, img).convert("RGB")

                buffered = BytesIO()
                img_final.save(buffered, format="PNG")
                img_bytes = buffered.getvalue()

                fuso_brasilia = pytz.timezone("America/Sao_Paulo")
                data_atual = datetime.datetime.now(fuso_brasilia).strftime("%d/%m/%Y às %H:%M:%S")

                supabase.table("funcionarios").update({
                    "assinado": True,
                    "assinatura_hex": img_bytes.hex(),
                    "data_hora": data_atual,
                    "ip_auditoria": ip_final,
                    "ua_auditoria": ua_final
                }).eq("id", colaborador["id"]).execute()

                st.rerun()
else:
    # --- VISÃO DA TI COM TELA DE LOGIN SEGURA ---
    st.markdown("<h1 style='text-align: center; color: #0f172a;'>🏢 Gestão de Integração Ferpam</h1>", unsafe_allow_html=True)
    
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("### 🔐 Área Restrita - Setor de TI")
        usuario_input = st.text_input("Usuário")
        senha_input = st.text_input("Senha", type="password")
        
        if st.button("Entrar no Painel", use_container_width=True, type="primary"):
            if usuario_input == st.secrets["credentials"]["usuario_ti"] and senha_input == st.secrets["credentials"]["senha_ti"]:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Usuário ou Senha inválidos.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"Logado como: **{st.secrets['credentials']['usuario_ti']}**")
        if st.sidebar.button("🚪 Sair do Painel"):
            st.session_state["autenticado"] = False
            st.rerun()

        st.markdown("---")
        tab_cadastro, tab_arquivo = st.tabs([
            "➕ Cadastrar Integrante", 
            "📂 Arquivo de Contratos"
        ])

        # --- ABA 1: CADASTRO ---
        with tab_cadastro:
            st.markdown("### 📝 Dados do Novo Colaborador")
            col_a, col_b = st.columns(2)
            with col_a:
                nome_cad = st.text_input("Nome Completo", placeholder="Ex: João Neto Silva", key="cad_nome")
                cargo_cad = st.text_input("Cargo", placeholder="Ex: Assistente Administrativo", key="cad_cargo")
            with col_b:
                email_cad = st.text_input("E-mail", placeholder="Ex: joao@ferpam.com.br", key="cad_email")
                setor_cad = st.text_input("Setor", placeholder="Ex: TI", key="cad_setor")

            if st.button("✨ Cadastrar para Assinatura", use_container_width=True):
                if nome_cad and cargo_cad and email_cad:
                    funcionario_id = str(uuid.uuid4())[:8]
                    link_unico = f"https://termo-ferpam.streamlit.app/?id={funcionario_id}"
                    setor_envio = setor_cad if setor_cad else "Geral"
                    
                    novo_funcionario = {
                        "id": funcionario_id, "nome": nome_cad, "cargo": cargo_cad, "setor": setor_envio,
                        "email": email_cad, "assinado": False, "assinatura_hex": None, "data_hora": "",
                        "ip_auditoria": "", "ua_auditoria": ""
                    }
                    
                    enviado, motivo_erro = enviar_email(email_cad, nome_cad, link_unico)
                    
                    if enviado:
                        supabase.table("funcionarios").insert(novo_funcionario).execute()
                        st.success(f"✅ {nome_cad} cadastrado e e-mail enviado com sucesso!")
                    else:
                        st.error(f"❌ Falha crítica ao enviar e-mail: {motivo_erro}")
                else:
                    st.error("Por favor, preencha os campos obrigatórios.")

        # --- ABA 2: ARQUIVO ---
        with tab_arquivo:
            st.markdown("### 📂 Contratos Concluídos")
            
            resposta_todos = supabase.table("funcionarios").select("*").order("nome").execute()
            todos_funcionarios = resposta_todos.data
            
            assinados = [f for f in todos_funcionarios if f["assinado"]]
            pendentes_lista = [f for f in todos_funcionarios if not f["assinado"]]
            
            if not pendentes_lista:
                st.caption("Não há assinaturas pendentes no momento.")
            else:
                st.markdown(f"**Pendentes de Assinatura ({len(pendentes_lista)}):**")
                for p in pendentes_lista:
                    col_pend1, col_pend2 = st.columns([4, 1])
                    with col_pend1:
                        st.caption(f"⏳ {p['nome']} ({p['email']}) - ID: {p['id']}")
                    with col_pend2:
                        if st.button("❌", key=f"del_pend_{p['id']}", help="Cancelar envio/Excluir pendente"):
                            supabase.table("funcionarios").delete().eq("id", p["id"]).execute()
                            st.rerun()

            st.divider()

            if not assinados:
                st.info("Nenhum termo assinado armazenado em banco ainda.")
            else:
                for f in assinados:
                    col_info, col_botoes = st.columns([3, 2])
                    with col_info:
                        st.markdown(f"##### 📄 {f['nome']}")
                        st.caption(f"**Cargo:** {f['cargo']} | **Setor:** {f['setor']} | **Em:** {f['data_hora']}")
                    with col_botoes:
                        sub_col1, sub_col2 = st.columns(2)
                        with sub_col1:
                            if f.get("assinatura_hex"):
                                sig_bytes = bytes.fromhex(f["assinatura_hex"])
                                pdf_sob_demanda = gerar_pdf_contrato(
                                    f["nome"], f["cargo"], f["setor"], f["data_hora"], 
                                    sig_bytes, f["id"], f.get("ip_auditoria", "Não registrado"), f.get("ua_auditoria", "Não registrado")
                                )
                                st.download_button(
                                    "📥 Baixar PDF", 
                                    pdf_sob_demanda, 
                                    file_name=f"Termo_TI_{f['nome'].replace(' ', '_')}.pdf", 
                                    mime="application/pdf", 
                                    key=f"down_{f['id']}"
                                )
                        with sub_col2:
                            if st.button("❌ Deletar", key=f"del_{f['id']}", type="secondary"):
                                supabase.table("funcionarios").delete().eq("id", f["id"]).execute()
                                st.toast(f"Registro de {f['nome']} removido com sucesso!")
                                st.rerun()
                    st.divider()
