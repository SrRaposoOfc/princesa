import json
import os
import re

HTML_FILE = "amor.html"
PASTA_FOTOS = "fotos"
PASTA_MUSICA = "musica"
EXTENSOES_IMG = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}
EXTENSOES_AUDIO = {".mp3", ".ogg", ".m4a", ".wav", ".flac"}


def ler_html():
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        return f.read()


def salvar_html(conteudo):
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(conteudo)


# ── FOTOS ────────────────────────────────────────────────────────────────────


def escanear_fotos():
    if not os.path.exists(PASTA_FOTOS):
        os.makedirs(PASTA_FOTOS)
    return sorted(
        f
        for f in os.listdir(PASTA_FOTOS)
        if os.path.isfile(os.path.join(PASTA_FOTOS, f))
        and os.path.splitext(f)[1].lower() in EXTENSOES_IMG
    )


def extrair_fotos_do_html(html):
    """Lê a lista atual de fotos que já está embutida no HTML."""
    match = re.search(
        r"/\* FOTOS_INICIO \*/\s*const FOTOS_DATA = (\[.*?\]);\s*/\* FOTOS_FIM \*/",
        html,
        re.DOTALL,
    )
    if not match:
        return []
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return []


def sincronizar_fotos(html, arquivos_pasta):
    fotos_html = extrair_fotos_do_html(html)
    existente = {item["arquivo"]: item for item in fotos_html}

    nova_lista = []
    adicionadas = []
    for arq in arquivos_pasta:
        if arq in existente:
            nova_lista.append(existente[arq])
        else:
            nova_lista.append({"arquivo": arq, "legenda": ""})
            adicionadas.append(arq)

    removidas = [f["arquivo"] for f in fotos_html if f["arquivo"] not in arquivos_pasta]

    # Serializa de forma legível
    if nova_lista:
        linhas = ["[\n"]
        for i, foto in enumerate(nova_lista):
            virgula = "," if i < len(nova_lista) - 1 else ""
            legenda = foto.get("legenda", "").replace('"', '\\"')
            linhas.append(
                f'                {{ "arquivo": "{foto["arquivo"]}", "legenda": "{legenda}" }}{virgula}\n'
            )
        linhas.append("            ]")
        lista_str = "".join(linhas)
    else:
        lista_str = "[]"

    novo_bloco = f"/* FOTOS_INICIO */\n            const FOTOS_DATA = {lista_str};\n            /* FOTOS_FIM */"

    html_novo = re.sub(
        r"/\* FOTOS_INICIO \*/.*?/\* FOTOS_FIM \*/",
        novo_bloco,
        html,
        flags=re.DOTALL,
    )

    return html_novo, adicionadas, removidas


# ── MÚSICA ───────────────────────────────────────────────────────────────────


def escanear_musica():
    if not os.path.exists(PASTA_MUSICA):
        os.makedirs(PASTA_MUSICA)
    arquivos = sorted(
        f
        for f in os.listdir(PASTA_MUSICA)
        if os.path.isfile(os.path.join(PASTA_MUSICA, f))
        and os.path.splitext(f)[1].lower() in EXTENSOES_AUDIO
    )
    return arquivos[0] if arquivos else None


def extrair_musica_do_html(html):
    """Lê o objeto de música atual embutido no HTML."""
    match = re.search(
        r"/\* MUSICA_INICIO \*/\s*const MUSICA_DATA = (null|\{.*?\});\s*/\* MUSICA_FIM \*/",
        html,
        re.DOTALL,
    )
    if not match:
        return None
    raw = match.group(1).strip()
    if raw == "null":
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def sincronizar_musica(html, arquivo_musica):
    musica_html = extrair_musica_do_html(html)

    if arquivo_musica is None:
        novo_valor = "null"
        mudou = musica_html is not None
    else:
        nome_atual = musica_html.get("nome", "") if musica_html else ""
        artista_atual = musica_html.get("artista", "") if musica_html else ""

        # Preserva nome/artista se o arquivo for o mesmo
        if musica_html and musica_html.get("arquivo") == arquivo_musica:
            nome = nome_atual
            artista = artista_atual
        else:
            # Novo arquivo — usa nome do arquivo sem extensão como padrão
            nome = os.path.splitext(arquivo_musica)[0]
            artista = ""

        novo_obj = {"arquivo": arquivo_musica, "nome": nome, "artista": artista}
        novo_valor = json.dumps(novo_obj, ensure_ascii=False)
        mudou = musica_html != novo_obj

    novo_bloco = f"/* MUSICA_INICIO */\n            const MUSICA_DATA = {novo_valor};\n            /* MUSICA_FIM */"

    html_novo = re.sub(
        r"/\* MUSICA_INICIO \*/.*?/\* MUSICA_FIM \*/",
        novo_bloco,
        html,
        flags=re.DOTALL,
    )

    return html_novo, mudou


# ── MAIN ─────────────────────────────────────────────────────────────────────


def main():
    print("=" * 52)
    print("   Sincronizador de Galeria e Musica")
    print("=" * 52)
    print()

    if not os.path.exists(HTML_FILE):
        print(f'ERRO: "{HTML_FILE}" nao encontrado.')
        print("Execute este script na mesma pasta do amor.html.")
        input("\nPressione Enter para fechar...")
        return

    html = ler_html()
    alteracoes = False

    # ── Fotos
    print("Escaneando pasta fotos/ ...")
    arquivos_fotos = escanear_fotos()
    html, adicionadas, removidas = sincronizar_fotos(html, arquivos_fotos)

    if adicionadas:
        for a in adicionadas:
            print(f"  + Foto adicionada: {a}")
        alteracoes = True
    if removidas:
        for r in removidas:
            print(f"  - Foto removida:   {r}")
        alteracoes = True
    if not adicionadas and not removidas:
        print(f"  Sem mudancas. ({len(arquivos_fotos)} foto(s) na galeria)")

    print()

    # ── Música
    print("Escaneando pasta musica/ ...")
    arquivo_musica = escanear_musica()
    html, musica_mudou = sincronizar_musica(html, arquivo_musica)

    if musica_mudou:
        if arquivo_musica:
            print(f"  + Musica atualizada: {arquivo_musica}")
        else:
            print("  - Musica removida (nenhum arquivo de audio encontrado)")
        alteracoes = True
    else:
        status = arquivo_musica if arquivo_musica else "nenhuma"
        print(f"  Sem mudancas. (musica atual: {status})")

    print()

    # ── Salva
    if alteracoes:
        salvar_html(html)
        print("amor.html atualizado com sucesso!")
        print()
        print('Dica: edite o amor.html e procure "legenda" para')
        print("adicionar legendas nas fotos, ou nome/artista na musica.")
    else:
        print("Nada para atualizar.")

    print()
    input("Pressione Enter para fechar...")


if __name__ == "__main__":
    main()
