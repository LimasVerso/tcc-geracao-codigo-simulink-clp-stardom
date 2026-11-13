#!/usr/bin/env python3
"""
pos_plccoder_v2.py - Pós-processamento do código ST gerado pelo Simulink PLC Coder
(Target IDE "Generic", arquivo .st) para importação no Logic Designer (Yokogawa),
versão 2: troca dos tipos na declaração das variáveis.

Em vez de acrescentar o prefixo LREAL# em cada literal decimal e converter o seletor
do CASE com SINT_TO_INT (versão 1, pos_plccoder.py), esta versão troca os tipos:

  R1  troca da seção VAR_TEMP por VAR;
  R2  marcação de abertura da worksheet, antes do corpo de cada POU;
  R3  marcação de fechamento da worksheet, depois do corpo de cada POU;
  R6  troca dos tipos LREAL -> REAL e SINT -> INT fora dos comentários, ou seja, nas
      declarações das variáveis, nos tipos de retorno, nos literais tipados
      (LREAL# -> REAL#, SINT# -> INT#) e nos nomes das funções de conversão
      (por exemplo, LREAL_TO_SINT -> REAL_TO_INT).

Com as variáveis em REAL, os literais decimais deixam de exigir o prefixo de tipo, e o
bloco do controlador passa a ser ligado diretamente a uma planta em REAL, sem os
conversores REAL_TO_LREAL e LREAL_TO_REAL; com o seletor em INT, o CASE dispensa o
SINT_TO_INT e o bloco MOVE pode enviar uma constante INT. O número de alterações passa a
depender do número de declarações, e não do número de literais no código.

Atenção: REAL tem precisão simples (cerca de 7 algarismos significativos), enquanto
LREAL tem precisão dupla (cerca de 15), de modo que a troca pode reduzir a precisão dos
cálculos, o que deve ser verificado comparando a resposta no CLP com a simulação.

Uso:
    python pos_plccoder_v2.py ENTRADA.st [-o SAIDA.ST] [--relatorio RELATORIO.txt]

Requer apenas a biblioteca padrão do Python (3.8 ou superior).
"""

import argparse
import re
import sys

POU_INICIO = re.compile(r'^\s*(FUNCTION_BLOCK|FUNCTION|PROGRAM)\s+([A-Za-z_]\w*)', re.I)
POU_FIM = re.compile(r'^\s*END_(FUNCTION_BLOCK|FUNCTION|PROGRAM)\b', re.I)
SECAO_VAR = re.compile(r'^\s*VAR(_INPUT|_OUTPUT|_IN_OUT|_TEMP|_EXTERNAL|_GLOBAL)?\b', re.I)
FIM_VAR = re.compile(r'^\s*END_VAR\b', re.I)
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


MAPA_TIPOS = {'LREAL': 'REAL', 'SINT': 'INT'}
TOKEN_TIPO = re.compile(r'\b(LREAL|SINT)\b(#?)')
CONVERSAO = re.compile(r'\b([A-Z]+)_TO_([A-Z]+)\b')


def r6_tipos(linhas, mascaras, pous, log):
    """Troca LREAL -> REAL e SINT -> INT fora dos comentários."""
    def troca_conv(m):
        de, para = MAPA_TIPOS.get(m.group(1), m.group(1)), MAPA_TIPOS.get(m.group(2), m.group(2))
        return '%s_TO_%s' % (de, para)

    for n, linha in enumerate(linhas):
        mk = mascaras[n]
        if not eh_codigo(linha, mk):
            continue
        # monta a linha trocando apenas os trechos fora de comentário
        novo, i = [], 0
        while i < len(linha):
            j = i
            while j < len(linha) and mk[j] == mk[i]:
                j += 1
            trecho = linha[i:j]
            if not mk[i]:
                trecho = CONVERSAO.sub(troca_conv, trecho)
                trecho = TOKEN_TIPO.sub(lambda m: MAPA_TIPOS[m.group(1)] + m.group(2), trecho)
            novo.append(trecho)
            i = j
        novo = ''.join(novo)
        if novo != linha:
            desc = 'troca de tipo (LREAL -> REAL, SINT -> INT)'
            for m in CONVERSAO.finditer(novo):
                if m.group(1) == m.group(2):
                    log.append(('AVISO', n, '', '', 'linha %d: conversão %s_TO_%s resultante da troca '
                                'de tipos; conferir se pode ser removida' % (n + 1, m.group(1), m.group(2))))
            log.append(('R6', n, linha, novo, desc))
            linhas[n] = novo
            mascaras[n] = mascara_comentarios([novo])[0]


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
def processar(linhas):
    linhas = list(linhas)
    mascaras = mascara_comentarios(linhas)
    pous = localizar_pous(linhas, mascaras)
    log = []
    if not pous:
        log.append(('AVISO', 0, '', '', 'nenhuma POU (FUNCTION_BLOCK, FUNCTION ou PROGRAM) encontrada'))
        return linhas, log, pous, 0
    codigo = sum(1 for n, l in enumerate(linhas) if eh_codigo(l, mascaras[n]))
    r1_var_temp(linhas, mascaras, pous, log)
    r6_tipos(linhas, mascaras, pous, log)
    r2_r3_worksheet(linhas, pous, log)
    return linhas, log, pous, codigo


def relatorio(log, pous, codigo, entrada):
    editadas = sorted({n for r, n, *_ in log if r in ('R1', 'R6')})
    marcacoes = sum(1 for r, *_ in log if r in ('R2', 'R3'))
    txt = ['Relatório do pós-processamento (pos_plccoder_v2.py)',
           'Arquivo de entrada: %s' % entrada,
           'Versão 2: troca de tipos LREAL -> REAL e SINT -> INT',
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
                                             'para o Logic Designer (Rota B), versão 2.')
    ap.add_argument('entrada', help='arquivo .st gerado pelo PLC Coder (Target IDE "Generic")')
    ap.add_argument('-o', '--saida', help='arquivo de saída (padrão: <entrada>_LogicDesigner.ST)')
    ap.add_argument('--relatorio', help='grava o relatório neste arquivo (padrão: mostra na tela)')
    a = ap.parse_args(argv)

    linhas, fmt = ler(a.entrada)
    saida_linhas, log, pous, codigo = processar(linhas)
    saida = a.saida or re.sub(r'\.st$', '', a.entrada, flags=re.I) + '_LogicDesigner_v2.ST'
    escrever(saida, saida_linhas, fmt)
    rel = relatorio(log, pous, codigo, a.entrada)
    if a.relatorio:
        with open(a.relatorio, 'w', encoding='utf-8') as f:
            f.write(rel)
    else:
        sys.stdout.write(rel)
    print('Arquivo gerado: %s' % saida)
    return 0


if __name__ == '__main__':
    sys.exit(main())
