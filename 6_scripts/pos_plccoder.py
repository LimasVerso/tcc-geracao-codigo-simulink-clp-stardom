#!/usr/bin/env python3
"""
pos_plccoder.py - Pós-processamento do código ST gerado pelo Simulink PLC Coder
(Target IDE "Generic", arquivo .st) para importação no Logic Designer (Yokogawa).

Aplica automaticamente as adequações identificadas no TCC "Geração Automática de
Código para CLP com ferramentas do MATLAB/Simulink" (Rota B, Tabela 4):

  Modo "estrutural" (adequações para a importação):
    R1  troca da seção VAR_TEMP por VAR;
    R2  marcação de abertura da worksheet, antes do corpo de cada POU;
    R3  marcação de fechamento da worksheet, depois do corpo de cada POU.

  Modo "completo" (estrutural + adequações de tipo):
    R4  prefixo de tipo LREAL# nos literais decimais (fora dos comentários);
    R5  seletor do CASE convertido com SINT_TO_INT quando a variável é SINT.

Não são tratados, por não estarem no arquivo gerado: os conversores REAL/LREAL e a
constante SINT#1 do bloco MOVE, que pertencem ao programa montado pelo usuário no
Logic Designer, e a renomeação das portas, que tem apenas intuito didático.

Uso:
    python pos_plccoder.py ENTRADA.st [-o SAIDA.ST] [--modo estrutural|completo]
                           [--relatorio RELATORIO.txt]

Requer apenas a biblioteca padrão do Python (3.8 ou superior).
"""

import argparse
import re
import sys

POU_INICIO = re.compile(r'^\s*(FUNCTION_BLOCK|FUNCTION|PROGRAM)\s+([A-Za-z_]\w*)', re.I)
POU_FIM = re.compile(r'^\s*END_(FUNCTION_BLOCK|FUNCTION|PROGRAM)\b', re.I)
SECAO_VAR = re.compile(r'^\s*VAR(_INPUT|_OUTPUT|_IN_OUT|_TEMP|_EXTERNAL|_GLOBAL)?\b', re.I)
FIM_VAR = re.compile(r'^\s*END_VAR\b', re.I)
# literal decimal sem prefixo de tipo: 0.0, 1.83, 1.0E-3, 2.5e+10
LITERAL = re.compile(r'(?<![\w#.])(\d+\.\d+(?:[eE][+-]?\d+)?)(?![\w.])')
DECLARACAO = re.compile(r'^\s*([A-Za-z_]\w*)\s*:\s*([A-Za-z_]\w*)', re.I)


# ----------------------------------------------------------------------------
# Leitura e escrita preservando codificação e quebra de linha
# ----------------------------------------------------------------------------
def ler(caminho):
    with open(caminho, 'rb') as f:
        dados = f.read()
    try:
        texto, cod = dados.decode('utf-8'), 'utf-8'
    except UnicodeDecodeError:
        texto, cod = dados.decode('latin-1'), 'latin-1'
    nl = '\r\n' if '\r\n' in texto else '\n'
    linhas = texto.replace('\r\n', '\n').split('\n')
    final_nl = texto.endswith('\n') or texto.endswith('\r\n')
    if final_nl:
        linhas = linhas[:-1]
    return linhas, {'cod': cod, 'nl': nl, 'final_nl': final_nl}


def escrever(caminho, linhas, fmt):
    texto = fmt['nl'].join(linhas) + (fmt['nl'] if fmt['final_nl'] else '')
    with open(caminho, 'wb') as f:
        f.write(texto.encode(fmt['cod']))


# ----------------------------------------------------------------------------
# Comentários (* ... *): máscara por caractere, para não alterar o texto deles
# ----------------------------------------------------------------------------
def mascara_comentarios(linhas):
    """Para cada linha, devolve uma lista de booleanos (True = dentro de comentário)."""
    dentro = False
    mascaras = []
    for linha in linhas:
        m = [False] * len(linha)
        i = 0
        while i < len(linha):
            if not dentro and linha.startswith('(*', i):
                dentro = True
                m[i] = m[i + 1] = True
                i += 2
                continue
            if dentro and linha.startswith('*)', i):
                m[i] = m[i + 1] = True
                dentro = False
                i += 2
                continue
            if not dentro and linha.startswith('//', i):
                for k in range(i, len(linha)):
                    m[k] = True
                break
            m[i] = dentro
            i += 1
        mascaras.append(m)
    return mascaras


def eh_codigo(linha, mascara):
    """Linha com algum caractere de código fora de comentário."""
    return any(not c.isspace() and not mk for c, mk in zip(linha, mascara))


# ----------------------------------------------------------------------------
# Estrutura das POU
# ----------------------------------------------------------------------------
def localizar_pous(linhas, mascaras):
    pous, atual, em_var = [], None, False
    for n, linha in enumerate(linhas):
        if not eh_codigo(linha, mascaras[n]):
            continue
        if atual is None:
            m = POU_INICIO.match(linha)
            if m:
                atual = {'tipo': m.group(1).upper(), 'nome': m.group(2),
                         'inicio': n, 'ultimo_end_var': None, 'fim': None, 'vars': {}}
            continue
        if POU_FIM.match(linha):
            atual['fim'] = n
            pous.append(atual)
            atual, em_var = None, False
            continue
        m_var = SECAO_VAR.match(linha)
        if m_var:
            resto = linha[m_var.end():]
            d = DECLARACAO.match(resto)
            if d:
                atual['vars'][d.group(1)] = d.group(2).upper()
            if re.search(r'\bEND_VAR\b', resto, re.I):
                atual['ultimo_end_var'] = n
            else:
                em_var = True
            continue
        if FIM_VAR.match(linha):
            em_var = False
            atual['ultimo_end_var'] = n
            continue
        if em_var:
            d = DECLARACAO.match(linha)
            if d:
                atual['vars'][d.group(1)] = d.group(2).upper()
    return pous


# ----------------------------------------------------------------------------
# Regras
# ----------------------------------------------------------------------------
def r1_var_temp(linhas, mascaras, pous, log):
    for n, linha in enumerate(linhas):
        if eh_codigo(linha, mascaras[n]) and re.match(r'^\s*VAR_TEMP\b', linha, re.I):
            novo = re.sub(r'VAR_TEMP', 'VAR', linha, count=1, flags=re.I)
            log.append(('R1', n, linha, novo, 'troca de VAR_TEMP por VAR'))
            linhas[n] = novo
            mascaras[n] = mascara_comentarios([novo])[0]


def r4_lreal(linhas, mascaras, pous, log):
    for p in pous:
        tipos = set(p['vars'].values())
        if 'REAL' in tipos:
            log.append(('AVISO', p['inicio'], '', '',
                        'POU %s declara variáveis REAL: prefixo LREAL# não aplicado; '
                        'conferir os literais manualmente' % p['nome']))
            continue
        for n in range(p['inicio'] + 1, p['fim']):
            linha, mk = linhas[n], mascaras[n]
            partes, ult = [], 0
            for m in LITERAL.finditer(linha):
                if mk[m.start()]:
                    continue
                partes.append(linha[ult:m.start()] + 'LREAL#' + m.group(1))
                ult = m.end()
            if partes:
                novo = ''.join(partes) + linha[ult:]
                log.append(('R4', n, linha, novo, 'prefixo de tipo LREAL# nos literais decimais'))
                linhas[n] = novo
                mascaras[n] = mascara_comentarios([novo])[0]


def r5_case(linhas, mascaras, pous, log):
    for p in pous:
        for n in range(p['inicio'] + 1, p['fim']):
            linha = linhas[n]
            m = re.match(r'^(\s*CASE\s+)([A-Za-z_]\w*)(\s+OF\b.*)$', linha, re.I)
            if m and eh_codigo(linha, mascaras[n]) and p['vars'].get(m.group(2)) == 'SINT':
                novo = '%sSINT_TO_INT(%s)%s' % (m.group(1), m.group(2), m.group(3))
                log.append(('R5', n, linha, novo, 'seletor do CASE convertido com SINT_TO_INT'))
                linhas[n] = novo


def r2_r3_worksheet(linhas, pous, log):
    """Insere as marcações de baixo para cima, para não deslocar os índices."""
    for p in reversed(pous):
        if p['ultimo_end_var'] is None:
            log.append(('AVISO', p['inicio'], '', '',
                        'POU %s sem seção de variáveis: marcação de abertura inserida '
                        'após a declaração da POU' % p['nome']))
            pos_abre = p['inicio'] + 1
        else:
            pos_abre = p['ultimo_end_var'] + 1
        fecha = ['(*@KEY@: END_WORKSHEET *)']
        abre = ['(*@KEY@: WORKSHEET', 'NAME: %s' % p['nome'].upper(), 'IEC_LANGUAGE: ST', '*)']
        linhas[p['fim']:p['fim']] = fecha
        log.append(('R3', p['fim'], '', fecha[0], 'marcação de fechamento da worksheet'))
        linhas[pos_abre:pos_abre] = abre
        log.append(('R2', pos_abre, '', ' / '.join(abre), 'marcação de abertura da worksheet'))


# ----------------------------------------------------------------------------
# Processamento e relatório
# ----------------------------------------------------------------------------
def processar(linhas, modo='completo'):
    linhas = list(linhas)
    mascaras = mascara_comentarios(linhas)
    pous = localizar_pous(linhas, mascaras)
    log = []
    if not pous:
        log.append(('AVISO', 0, '', '', 'nenhuma POU (FUNCTION_BLOCK, FUNCTION ou PROGRAM) encontrada'))
        return linhas, log, pous, 0
    codigo = sum(1 for n, l in enumerate(linhas) if eh_codigo(l, mascaras[n]))
    r1_var_temp(linhas, mascaras, pous, log)
    if modo == 'completo':
        r4_lreal(linhas, mascaras, pous, log)
        r5_case(linhas, mascaras, pous, log)
    r2_r3_worksheet(linhas, pous, log)
    return linhas, log, pous, codigo


def relatorio(log, pous, codigo, entrada, modo):
    editadas = sorted({n for r, n, *_ in log if r in ('R1', 'R4', 'R5')})
    marcacoes = sum(1 for r, *_ in log if r in ('R2', 'R3'))
    txt = ['Relatório do pós-processamento (pos_plccoder.py)',
           'Arquivo de entrada: %s' % entrada,
           'Modo: %s' % modo,
           'POU encontradas: %s' % ', '.join('%s %s' % (p['tipo'], p['nome']) for p in pous),
           '',
           'Linhas de código (sem comentários e sem linhas em branco): %d' % codigo,
           'Linhas de código alteradas: %d' % len(editadas),
           'Marcações da worksheet inseridas: %d' % marcacoes]
    if codigo:
        txt.append('Proporção de linhas alteradas: %.1f %%' % (100.0 * len(editadas) / codigo))
    txt += ['', 'Ajustes aplicados (linha no arquivo de entrada):']
    for r, n, antes, depois, desc in sorted(log, key=lambda x: (x[1], x[0])):
        if r == 'AVISO':
            txt.append('  AVISO: %s' % desc)
            continue
        txt.append('  %s, linha %d: %s' % (r, n + 1, desc))
        if antes:
            txt.append('      antes:  %s' % antes.strip())
        txt.append('      depois: %s' % depois.strip())
    return '\n'.join(txt) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description='Pós-processamento do .st do Simulink PLC Coder '
                                             'para o Logic Designer (Rota B).')
    ap.add_argument('entrada', help='arquivo .st gerado pelo PLC Coder (Target IDE "Generic")')
    ap.add_argument('-o', '--saida', help='arquivo de saída (padrão: <entrada>_LogicDesigner.ST)')
    ap.add_argument('--modo', choices=['estrutural', 'completo'], default='completo',
                    help='estrutural: só as adequações de importação; completo: também as de tipo')
    ap.add_argument('--relatorio', help='grava o relatório neste arquivo (padrão: mostra na tela)')
    a = ap.parse_args(argv)

    linhas, fmt = ler(a.entrada)
    saida_linhas, log, pous, codigo = processar(linhas, a.modo)
    saida = a.saida or re.sub(r'\.st$', '', a.entrada, flags=re.I) + '_LogicDesigner.ST'
    escrever(saida, saida_linhas, fmt)
    rel = relatorio(log, pous, codigo, a.entrada, a.modo)
    if a.relatorio:
        with open(a.relatorio, 'w', encoding='utf-8') as f:
            f.write(rel)
    else:
        sys.stdout.write(rel)
    print('Arquivo gerado: %s' % saida)
    return 0


if __name__ == '__main__':
    sys.exit(main())
