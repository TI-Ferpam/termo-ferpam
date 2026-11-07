import streamlit as st
import streamlit.components.v1 as components
import uuid
import datetime
import pytz
import os
import re
from io import BytesIO
from PIL import Image, ImageDraw
from streamlit_drawable_canvas import st_canvas
from fpdf import FPDF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from streamlit_javascript import st_javascript

# 🔥 INTERCEPTAÇÃO E CORREÇÃO DE COMPATIBILIDADE HTTP2
import httpx

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
            kwargs["http2"] = False  # Desativa HTTP2 para evitar erros no Streamlit Cloud
        original_init(self, *args, **kwargs)

    TargetClient.__init__ = patched_init

# 🔥 IMPORTAÇÃO DO BANCO DE DADOS SUPABASE
from supabase import create_client, Client

# Configurações do Layout
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
        border: 2px solid #94a3b8 !important;
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


# 🔥 INICIALIZAÇÃO DA CONEXÃO COM O SUPABASE
@st.cache_resource
def iniciar_banco() -> Client:
    url = st.secrets["supabase"]["url"].strip().rstrip('/')
    key = st.secrets["supabase"]["key"].strip()
    return create_client(url, key)

supabase = iniciar_banco()


def renderizar_termo_tela():
    html_conteudo = """<div class="termo-doc">
<h3 style="text-align:center; margin-top:0; margin-bottom:20px; color: #0f172a;">TERMO DE RESPONSABILIDADE E USO DOS RECURSOS DE TI</h3>
<p>Este Termo tem como objetivo estabelecer as diretrizes para o uso adequado dos recursos de Tecnologia da Informação disponibilizados pela Ferpam, garantindo a segurança, a integridade e a confidencialidade das informações da empresa.</p>
<p>Ao receber acesso aos sistemas, equipamentos e recursos tecnológicos da Ferpam, o colaborador declara estar ciente e concorda com as seguintes responsabilidades:</p>
<p><b>1. Confidencialidade das Informações</b><br>Todas as informações acessadas durante as atividades profissionais são de uso exclusivo da Ferpam e não devem ser divulgadas, compartilhadas ou utilizadas para fins pessoais ou externos sem autorização.</p>
<p><b>2. Instalação de Programas e Equipamentos</b><br>A instalação de programas, aplicativos, extensões, equipamentos ou qualquer alteração nos computadores e dispositivos da empresa deve ser realizada exclusivamente pelo setor de TI. Não é permitido instalar softwares ou aplicativos por conta própria.</p>
<p><b>3. Uso de E-mails e Dispositivos Pessoais</b><br>O uso de e-mails pessoais, pendrives, cartões de memória, serviços de armazenamento em nuvem e aplicativos de comunicação para manipulação de informações da empresa deve ocorrer apenas quando autorizado pela gestão ou pelo setor de TI.</p>
<p><b>4. Uso da Internet</b><br>O acesso à internet disponibilizado pela empresa deve ser utilizado prioritariamente para atividades relacionadas ao trabalho. É proibido acessar conteúdos inadequados, ilegais ou que possam comprometer a segurança da empresa, ainda que existam mecanismos de bloqueio ou restrição de acesso.</p>
<p><b>5. Senhas de Acesso</b><br>As senhas fornecidas para acesso aos sistemas são pessoais e intransferíveis. Não é permitido compartilhar senhas com outros colaboradores ou terceiros.</p>
<p><b>6. Segurança das Senhas</b><br>O colaborador compromete-se a:<br>
- Não anotar senhas em locais visíveis;<br>
- Não salvar senhas em arquivos desprotegidos;<br>
- Alterar a senha sempre que houver suspeita de comprometimento;<br>
- Utilizar senhas seguras.</p>
<p><b>7. E-mails Suspeitos</b><br>O colaborador não deve abrir links, anexos ou mensagens suspeitas recebidas por e-mail, WhatsApp ou outros meios de comunicação. Em caso de dúvida, o setor de TI deverá ser acionado antes de qualquer interação.</p>
<p><b>8. Proteção dos Equipamentos</b><br>Sempre que se ausentar do local de trabalho, o colaborador deverá bloquear o computador ou encerrar a sessão para evitar acessos não autorizados.</p>
<p><b>9. Uso dos Equipamentos da Empresa</b><br>Os equipamentos disponibilizados pela Ferpam destinam-se às atividades profissionais e devem ser utilizados de forma responsável, cuidadosa e de acordo com as orientações da empresa.</p>
<p><b>10. Monitoramento</b><br>A Ferpam poderá realizar o monitoramento dos recursos tecnológicos disponibilizados, incluindo acessos à internet, utilização dos sistemas corporativos e demais recursos de TI, visando garantir a segurança das informações e a continuidade das operações.</p>
<p><b>11. Comunicação de Incidentes</b><br>Qualquer suspeita de vírus, golpe, tentativa de fraude, perda de equipamento ou incidente relacionado à segurança da informação deverá ser comunicada imediatamente ao setor de TI.</p>
<p><b>12. Responsabilidade do Colaborador</b><br>O descumprimento das diretrizes estabelecidas neste Termo poderá resultar em medidas administrativas, conforme as normas internas da empresa e a legislação vigente.</p>
<hr style="border:0; border-top: 1px solid #cbd5e1; margin: 15px 0;">
<p>Declaro estar ciente das orientações acima e comprometo-me a cumprir as normas de utilização dos recursos de Tecnologia da Informação disponibilizados pela Ferpam.</p>
</div>"""
    st.markdown(html_conteudo, unsafe_allow_html=True)


def converter_texto_latin1(texto):
    """Auxiliar para evitar exceção de encode de caracteres no FPDF"""
    return str(texto).encode('latin-1', 'replace').decode('latin-1')


def parse_svg_path(path_data):
    """Converte qualquer formato (string SVG ou lista bruta) numa lista limpa de comandos"""
    if isinstance(path_data, list):
        clean = []
        for cmd in path_data:
            if isinstance(cmd, list):
                clean.append([str(cmd[0])] + [float(x) for x in cmd[1:]])
            elif isinstance(cmd, str):
                tokens = re.findall(r'([a-zA-Z])|([-+]?(?:\d*\.\d+|\d+))', cmd)
                flat = [t[0] or float(t[1]) for t in tokens]
                if flat:
                    clean.append(flat)
        return clean
    elif isinstance(path_data, str):
        tokens = re.findall(r'([a-zA-Z])|([-+]?(?:\d*\.\d+|\d+))', path_data)
        clean = []
        curr_cmd = None
        for t0, t1 in tokens:
            if t0:
                if curr_cmd:
                    clean.append(curr_cmd)
                curr_cmd = [t0]
            elif t1 and curr_cmd is not None:
                curr_cmd.append(float(t1))
        if curr_cmd:
            clean.append(curr_cmd)
        return clean
    return []


def renderizar_vetores_assinatura(json_data, width=680, height=220):
    """Reconstrói a assinatura vetorial com correção de escala e posicionamento"""
    if not json_data or not isinstance(json_data, dict):
        return None
    objects = json_data.get("objects", [])
    if not objects:
        return None

    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    elementos_desenhados = 0

    for obj in objects:
        raw_path = obj.get("path")
        if not raw_path:
            continue

        commands = parse_svg_path(raw_path)
        if not commands:
            continue

        xs, ys = [], []
        for cmd in commands:
            c = str(cmd[0]).upper()
            if c in ("M", "L") and len(cmd) >= 3:
                xs.append(cmd[1])
                ys.append(cmd[2])
            elif c == "Q" and len(cmd) >= 5:
                xs.extend([cmd[1], cmd[3]])
                ys.extend([cmd[2], cmd[4]])
            elif c == "C" and len(cmd) >= 7:
                xs.extend([cmd[1], cmd[3], cmd[5]])
                ys.extend([cmd[2], cmd[4], cmd[6]])

        if not xs or not ys:
            continue

        min_x, min_y = min(xs), min(ys)
        shift_x, shift_y = 0.0, 0.0

        path_offset = obj.get("pathOffset", {})
        po_x = float(path_offset.get("x", 0.0)) if isinstance(path_offset, dict) else 0.0
        po_y = float(path_offset.get("y", 0.0)) if isinstance(path_offset, dict) else 0.0

        # Aplica deslocamento apenas se as coordenadas forem centralizadas em torno do zero
        if min_x < -0.1 or min_y < -0.1:
            shift_x = po_x
            shift_y = po_y

        stroke_color = obj.get("stroke") or "#000000"
        stroke_width = max(3, int(obj.get("strokeWidth") or 4))

        curr = (shift_x, shift_y)
        for cmd in commands:
            c = str(cmd[0]).upper()
            if c == "M" and len(cmd) >= 3:
                curr = (cmd[1] + shift_x, cmd[2] + shift_y)
                draw.ellipse([curr[0]-stroke_width/2, curr[1]-stroke_width/2,
                              curr[0]+stroke_width/2, curr[1]+stroke_width/2], fill=stroke_color)
                elementos_desenhados += 1
            elif c == "L" and len(cmd) >= 3:
                nxt = (cmd[1] + shift_x, cmd[2] + shift_y)
                draw.line([curr, nxt], fill=stroke_color, width=stroke_width)
                draw.ellipse([nxt[0]-stroke_width/2, nxt[1]-stroke_width/2,
                              nxt[0]+stroke_width/2, nxt[1]+stroke_width/2], fill=stroke_color)
                curr = nxt
                elementos_desenhados += 1
            elif c == "Q" and len(cmd) >= 5:
                x0, y0 = curr
                cx, cy = cmd[1] + shift_x, cmd[2] + shift_y
                x1, y1 = cmd[3] + shift_x, cmd[4] + shift_y
                steps = 10
                for s in range(1, steps + 1):
                    t = s / steps
                    xt = (1-t)**2 * x0 + 2*(1-t)*t * cx + t**2 * x1
                    yt = (1-t)**2 * y0 + 2*(1-t)*t * cy + t**2 * y1
                    draw.line([curr, (xt, yt)], fill=stroke_color, width=stroke_width)
                    draw.ellipse([xt-stroke_width/2, yt-stroke_width/2,
                                  xt+stroke_width/2, yt+stroke_width/2], fill=stroke_color)
                    curr = (xt, yt)
                curr = (x1, y1)
                elementos_desenhados += 1
            elif c == "C" and len(cmd) >= 7:
                x0, y0 = curr
                cx1, cy1 = cmd[1] + shift_x, cmd[2] + shift_y
                cx2, cy2 = cmd[3] + shift_x, cmd[4] + shift_y
                x1, y1 = cmd[5] + shift_x, cmd[6] + shift_y
                steps = 10
                for s in range(1, steps + 1):
                    t = s / steps
                    xt = (1-t)**3 * x0 + 3*(1-t)**2 * t * cx1 + 3*(1-t)*t**2 * cx2 + t**3 * x1
                    yt = (1-t)**3 * y0 + 3*(1-t)**2 * t * cy1 + 3*(1-t)*t**2 * cy2 + t**3 * y1
                    draw.line([curr, (xt, yt)], fill=stroke_color, width=stroke_width)
                    draw.ellipse([xt-stroke_width/2, yt-stroke_width/2,
                                  xt+stroke_width/2, yt+stroke_width/2], fill=stroke_color)
                    curr = (xt, yt)
                curr = (x1, y1)
                elementos_desenhados += 1

    if elementos_desenhados > 0:
        return img
    return None


def obter_imagem_final(canvas_res, width=680, height=220):
    """Garante a extração da imagem testando tanto o buffer nativo como os vetores"""
    if canvas_res is None:
        return None

    # 1. Tenta o buffer de imagem nativo
    try:
        if hasattr(canvas_res, "image_data") and canvas_res.image_data is not None:
            raw_arr = canvas_res.image_data.astype("uint8")
            raw_img = Image.fromarray(raw_arr)
            bg = Image.new("RGBA", raw_img.size, (255, 255, 255))
            composed = Image.alpha_composite(bg, raw_img).convert("RGB")
            if composed.getextrema() != ((255, 255), (255, 255), (255, 255)):
                return composed
    except Exception:
        pass

    # 2. Reconstrói a partir do JSON de vetores
    if hasattr(canvas_res, "json_data") and canvas_res.json_data:
        img_vetorial = renderizar_vetores_assinatura(canvas_res.json_data, width=width, height=height)
        if img_vetorial is not None and img_vetorial.getextrema() != ((255, 255), (255, 255), (255, 255)):
            return img_vetorial

    return None


def gerar_pdf_contrato(nome, cargo, setor, data_hora, assinatura_bytes, funcionario_id, ip_cliente="Não capturado", ua_cliente="Não capturado"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, converter_texto_latin1("TERMO DE RESPONSABILIDADE E USO DOS RECURSOS DE TI"), ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "", 10.5)

    intro = (
        "Este Termo tem como objetivo estabelecer as diretrizes para o uso adequado dos recursos de "
        "Tecnologia da Informação disponibilizados pela Ferpam, garantindo a segurança, a integridade "
        "e a confidencialidade das informações da empresa.\n\n"
        "Ao receber acesso aos sistemas, equipamentos e recursos tecnológicos da Ferpam, o colaborador "
        "declara estar ciente e concorda com as seguintes responsabilidades:\n\n"
    )
    pdf.multi_cell(0, 5, converter_texto_latin1(intro))

    diretrizes = [
        "1. Confidencialidade das Informações\nTodas as informações acessadas durante as atividades profissionais são de uso exclusivo da Ferpam e não devem ser divulgadas, compartilhadas ou utilizadas para fins pessoais ou externos sem autorização.\n",
        "2. Instalação de Programas e Equipamentos\nA instalação de programas, aplicativos, extensões, equipamentos ou qualquer alteração nos computadores e dispositivos da empresa deve ser realizada exclusivamente pelo setor de TI. Não é permitido instalar softwares ou aplicativos por conta própria.\n",
        "3. Uso de E-mails e Dispositivos Pessoais\nO uso de e-mails pessoais, pendrives, cartões de memória, serviços de armazenamento em nuvem e aplicativos de comunicação para manipulação de informações da empresa deve ocorrer apenas quando autorizado pela gestão ou pelo setor de TI.\n",
        "4. Uso da Internet\nO acesso à internet disponibilizado pela empresa deve ser utilizado prioritariamente para atividades relacionadas ao trabalho. É proibido acessar conteúdos inadequados, ilegais ou que possam comprometer a segurança da empresa, ainda que existam mecanismos de bloqueio ou restrição de acesso.\n",
        "5. Senhas de Acesso\nAs senhas fornecidas para acesso aos sistemas são pessoais e intransferíveis. Não é permitido compartilhar senhas com outros colaboradores ou terceiros.\n",
        "6. Segurança das Senhas\nO colaborador compromete-se a:\n- Não anotar senhas em locais visíveis;\n- Não salvar senhas em arquivos desprotegidos;\n- Alterar a senha sempre que houver suspeita de comprometimento;\n- Utilizar senhas seguras.\n",
        "7. E-mails Suspeitos\nO colaborador não deve abrir links, anexos ou mensagens suspeitas recebidas por e-mail, WhatsApp ou outros meios de comunicação. Em caso de dúvida, o setor de TI deverá ser acionado antes de qualquer interação.\n",
        "8. Proteção dos Equipamentos\nSempre que se ausentar do local de trabalho, o colaborador deverá bloquear o computador ou encerrar a sessão para evitar acessos não autorizados.\n",
        "9. Uso dos Equipamentos da Empresa\nOs equipamentos disponibilizados pela Ferpam destinam-se às atividades profissionais e devem ser utilizados de forma responsável, cuidadosa e de acordo com as orientações da empresa.\n",
        "10. Monitoramento\nA Ferpam poderá realizar o monitoramento dos recursos tecnológicos disponibilizados, incluindo acessos à internet, utilização dos sistemas corporativos e demais recursos de TI, visando garantir a segurança das informações e a continuidade das operações.\n",
        "11. Comunicação de Incidentes\nQualquer suspeita de vírus, golpe, tentativa de fraude, perda de equipamento ou incidente relacionado à segurança da informação deverá ser comunicada imediatamente ao setor de TI.\n",
        "12. Responsabilidade do Colaborador\nO descumprimento das diretrizes estabelecidas neste Termo poderá resultar em medidas administrativas, conforme as normas internas da empresa e a legislação vigente.\n"
    ]

    for item in diretrizes:
        pdf.multi_cell(0, 5, converter_texto_latin1(item))
        pdf.ln(1)

    pdf.ln(2)
    pdf.multi_cell(0, 5, converter_texto_latin1("Declaro estar ciente das orientações acima e comprometo-me a cumprir as normas de utilização dos recursos de Tecnologia da Informação disponibilizados pela Ferpam.\n"))
    pdf.ln(4)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    pdf.set_font("Arial", "B", 10.5)
    pdf.cell(0, 6, converter_texto_latin1(f"Nome Completo: {nome}"), ln=True)
    pdf.cell(0, 6, converter_texto_latin1(f"Cargo: {cargo}"), ln=True)
    pdf.cell(0, 6, converter_texto_latin1(f"Setor: {setor}"), ln=True)
    pdf.cell(0, 6, converter_texto_latin1(f"Data e Hora do Registro: {data_hora}"), ln=True)

    assinatura_temp = f"temp_sig_{funcionario_id}.png"
    try:
        with open(assinatura_temp, "wb") as f:
            f.write(assinatura_bytes)
        pdf.ln(3)
        pdf.cell(0, 6, converter_texto_latin1("Assinatura Digitalizada:"), ln=True)
        pdf.image(assinatura_temp, x=20, y=pdf.get_y(), w=70)
        pdf.ln(30)
    finally:
        if os.path.exists(assinatura_temp):
            os.remove(assinatura_temp)

    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    pdf.cell(0, 4, converter_texto_latin1("Metadados de Validação Jurídica (Lei 14.063/2020)"), ln=True)
    pdf.cell(0, 4, converter_texto_latin1(f"ID de Autenticação do Sistema: {funcionario_id}"), ln=True)
    pdf.cell(0, 4, converter_texto_latin1(f"Endereço de IP Origem: {ip_cliente}"), ln=True)
    pdf.multi_cell(0, 4, converter_texto_latin1(f"Assinatura do Dispositivo (User-Agent): {ua_cliente}"))

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
        servidor.sendmail(EMAIL, destinatario, msg=mensagem.as_string())
        servidor.quit()
        return True, "Sucesso"
    except Exception as erro:
        return False, str(erro)


# ---------------- LOGICA DE ROTEAMENTO E PERSISTÊNCIA ----------------
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
                <p style="font-size: 16px;">Olá <b>{colaborador['nome']}</b>, as suas diretrizes de TI foram registadas com sucesso.</p>
                <p style="font-size: 14px; color: #65a30d;">Obrigado! Pode fechar esta página.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align: center; color: #0f172a;'>🏢 Assinatura de Termo Digital - Ferpam</h2>", unsafe_allow_html=True)
        st.info(f"Colaborador: {colaborador['nome']} | Cargo: {colaborador['cargo']}")

        renderizar_termo_tela()

        st.subheader("🖊️ Assine no quadro abaixo:")

        canvas_result = st_canvas(
            stroke_width=4,
            stroke_color="#000000",
            background_color="#FFFFFF",
            width=680,
            height=220,
            drawing_mode="freedraw",
            key=f"canvas_{url_id}",
            update_streamlit=True
        )

        # Atualiza a assinatura na sessão sem risco de eliminação acidental
        img_capturada = obter_imagem_final(canvas_result, width=680, height=220)
        if img_capturada is not None:
            st.session_state[f"assinatura_valida_{url_id}"] = img_capturada

        # Captura estável de IP e User-Agent
        if "ip_cliente" not in st.session_state:
            st.session_state["ip_cliente"] = st_javascript("fetch('https://api.ipify.org?format=json').then(r => r.json()).then(d => d.ip)", key="ip_tracker")
        if "ua_cliente" not in st.session_state:
            st.session_state["ua_cliente"] = st_javascript("window.navigator.userAgent", key="ua_tracker")

        col_b1, col_b2 = st.columns([4, 1])
        with col_b1:
            btn_enviar = st.button("💾 Enviar Assinatura Concluída", type="primary", use_container_width=True)
        with col_b2:
            if st.button("🗑️ Limpar"):
                st.session_state.pop(f"assinatura_valida_{url_id}", None)
                st.rerun()

        if btn_enviar:
            img_final = st.session_state.get(f"assinatura_valida_{url_id}")
            if img_final is None:
                img_final = obter_imagem_final(canvas_result, width=680, height=220)

            if img_final is None:
                st.error("O quadro de assinatura está vazio. Por favor, assine claramente antes de enviar.")
            else:
                ip_val = st.session_state.get("ip_cliente")
                ua_val = st.session_state.get("ua_cliente")
                ip_final = str(ip_val) if (ip_val and ip_val != "False" and ip_val != 0) else "IP Não identificado"
                ua_final = str(ua_val) if (ua_val and ua_val != "False" and ua_val != 0) else "Dispositivo Desconhecido"

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
    # --- VISÃO DA TI COM PERSISTÊNCIA DE SESSÃO NO F5 ---
    st.markdown("<h1 style='text-align: center; color: #0f172a;'>🏢 Gestão de Integração Ferpam</h1>", unsafe_allow_html=True)

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = (st.query_params.get("session") == "ti_logged_in")

    if not st.session_state["autenticado"]:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown("### 🔐 Área Restrita - Setor de TI")
        usuario_input = st.text_input("Usuário")
        senha_input = st.text_input("Senha", type="password")

        if st.button("Entrar no Painel", use_container_width=True, type="primary"):
            if usuario_input == st.secrets["credentials"]["usuario_ti"] and senha_input == st.secrets["credentials"]["senha_ti"]:
                st.session_state["autenticado"] = True
                st.query_params["session"] = "ti_logged_in"
                st.rerun()
            else:
                st.error("Usuário ou Senha inválidos.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"Logado como: **{st.secrets['credentials']['usuario_ti']}**")

        col_side1, col_side2 = st.sidebar.columns(2)
        with col_side1:
            if st.button("🔄 Atualizar", help="Sincronizar dados do banco"):
                st.rerun()
        with col_side2:
            if st.button("🚪 Sair"):
                st.session_state["autenticado"] = False
                if "session" in st.query_params:
                    del st.query_params["session"]
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

            if st.button("✨ Salvar e Gerar Link de Assinatura", use_container_width=True, type="primary"):
                if nome_cad and cargo_cad and email_cad:
                    funcionario_id = str(uuid.uuid4())[:8]
                    setor_envio = setor_cad if setor_cad else "Geral"

                    novo_funcionario = {
                        "id": funcionario_id, "nome": nome_cad, "cargo": cargo_cad, "setor": setor_envio,
                        "email": email_cad, "assinado": False, "assinatura_hex": None, "data_hora": "",
                        "ip_auditoria": "", "ua_auditoria": ""
                    }

                    try:
                        supabase.table("funcionarios").insert(novo_funcionario).execute()
                        st.success(f"✅ {nome_cad} cadastrado com sucesso!")
                        st.rerun()
                    except Exception as erro_banco:
                        st.error(f"❌ Erro ao gravar no Supabase: {erro_banco}")
                else:
                    st.error("Por favor, preencha os campos obrigatórios.")

            st.divider()

            st.markdown("### ✉️ Disparo Manual de Links")
            resposta_pendentes = supabase.table("funcionarios").select("*").eq("assinado", False).order("nome").execute()
            pendentes_email = resposta_pendentes.data

            if not pendentes_email:
                st.caption("Nenhum colaborador aguardando envio de link no momento.")
            else:
                for p in pendentes_email:
                    c1, c2 = st.columns([3, 1])
                    link_unico = f"https://termo-ferpam.streamlit.app/?id={p['id']}"

                    with c1:
                        st.markdown(f"**{p['nome']}** ({p['email']})")
                        st.caption(f"Cargo: {p['cargo']} | Link: `{link_unico}`")
                    with c2:
                        if st.button("🚀 Enviar E-mail", key=f"env_mail_{p['id']}", use_container_width=True):
                            enviado, motivo_erro = enviar_email(p["email"], p["nome"], link_unico)
                            if enviado:
                                st.toast(f"E-mail enviado para {p['nome']}!")
                            else:
                                st.error(f"Erro ao enviar: {motivo_erro}")

        # --- ABA 2: ARQUIVO ---
        with tab_arquivo:
            st.markdown("### 📂 Contratos Concluídos e Pendentes")

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
                st.info("Nenhum termo assinado armazenado no banco ainda.")
            else:
                st.markdown(f"**Termos Assinados ({len(assinados)}):**")
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
