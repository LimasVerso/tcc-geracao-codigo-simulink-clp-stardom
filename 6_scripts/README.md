# pos_plccoder

Scripts de pós-processamento do código ST gerado pelo **Simulink PLC Coder** (Target IDE "Generic", arquivo `.st`) para a importação no **Logic Designer** (Yokogawa, CLP STARDOM), desenvolvido no Trabalho de Conclusão de Curso *Geração Automática de Código para CLP com ferramentas do MATLAB/Simulink* (IFSP, Campus Cubatão, 2026).

O repositório traz duas versões, que aplicam de formas diferentes as adequações identificadas no TCC para a Rota B (arquivo `.st`):

- **Versão 1 (original)**, `pos_plccoder.py`: mantém os tipos gerados pelo PLC Coder (`LREAL` e `SINT`) e acrescenta o prefixo `LREAL#` nos literais e o `SINT_TO_INT` no seletor do CASE;
- **Versão 2**, `pos_plccoder_v2.py`: troca os tipos na declaração das variáveis (`LREAL` → `REAL` e `SINT` → `INT`), dispensando o prefixo nos literais, o `SINT_TO_INT` e os conversores `REAL_TO_LREAL`/`LREAL_TO_REAL` no programa de integração.

## Versão 1 (original)

A versão 1 aplica as adequações da Tabela 4 do TCC:

| Regra | Adequação | Modo |
|---|---|---|
| R1 | Troca da seção `VAR_TEMP` por `VAR` | estrutural e completo |
| R2 | Marcação de abertura da *worksheet* (`(*@KEY@: WORKSHEET ... *)`) antes do corpo de cada POU | estrutural e completo |
| R3 | Marcação de fechamento da *worksheet* (`(*@KEY@: END_WORKSHEET *)`) | estrutural e completo |
| R4 | Prefixo de tipo `LREAL#` nos literais decimais, fora dos comentários | completo |
| R5 | Seletor do CASE com `SINT_TO_INT(...)` quando a variável é `SINT` | completo |

Não são tratados, por não estarem no arquivo gerado, os conversores `REAL_TO_LREAL`/`LREAL_TO_REAL` e a constante `SINT#1` do bloco `MOVE`, que pertencem ao programa de integração montado no Logic Designer, nem a renomeação das portas, que no TCC tem apenas intuito didático.

## Versão 2

| Regra | Adequação |
|---|---|
| R1 a R3 | Iguais às da versão 1 (`VAR_TEMP` → `VAR` e marcações da *worksheet*) |
| R6 | Troca de `LREAL` por `REAL` e de `SINT` por `INT` fora dos comentários: declarações, tipos de retorno, literais tipados (`LREAL#` → `REAL#`, `SINT#` → `INT#`) e nomes das funções de conversão (por exemplo, `LREAL_TO_SINT` → `REAL_TO_INT`) |

Com as variáveis em `REAL`, os literais decimais deixam de exigir prefixo e o bloco é ligado diretamente a sinais `REAL`; com o seletor em `INT`, o CASE dispensa o `SINT_TO_INT` e o bloco `MOVE` pode enviar uma constante `INT`. O número de alterações passa a depender do número de declarações, e não do número de literais.

**Precisão:** `REAL` tem precisão simples (cerca de 7 algarismos significativos) e `LREAL` tem precisão dupla (cerca de 15), de modo que a versão 2 pode reduzir a precisão dos cálculos. Isso deve ser verificado comparando a resposta no CLP com a simulação.

### Comparação para o controlador PI do TCC

| | Versão 1 | Versão 2 |
|---|---|---|
| Linhas de código alteradas no `.st` (de 24) | 5 (20,8 %) | 7 (29,2 %) |
| Marcações da *worksheet* inseridas | 2 | 2 |
| Conversores no programa de integração | 3 (`REAL_TO_LREAL` ×2 e `LREAL_TO_REAL`) | Nenhum |
| Constante do `MOVE` | `SINT#1` | Constante `INT` |
| Tipo dos cálculos | `LREAL` (precisão dupla) | `REAL` (precisão simples) |

No PI, que tem poucos literais, a versão 2 altera mais linhas do `.st`, porém elimina os conversores e o ajuste do `MOVE`; em códigos com muitos literais, a versão 2 tende a alterar menos linhas, pois depende apenas do número de declarações.

## Requisitos

Python 3.8 ou superior, apenas com a biblioteca padrão.

## Uso

```
python pos_plccoder.py Controlador_PI.st -o Controlador_PI_Modificado.ST --modo completo --relatorio relatorio.txt
python pos_plccoder_v2.py Controlador_PI.st -o Controlador_PI_Modificado_v2.ST --relatorio relatorio_v2.txt
```

- `--modo estrutural` (versão 1): aplica só as adequações de importação (R1 a R3).
- `--modo completo` (versão 1, padrão): aplica também as adequações de tipo (R4 e R5).
- `--relatorio`: grava a lista dos ajustes, com as linhas alteradas, o número de linhas de código e a proporção de linhas alteradas; sem esta opção, o relatório é mostrado na tela.

A codificação e o tipo de quebra de linha do arquivo de entrada são preservados.

## Validação

A pasta `exemplos` contém o arquivo gerado pelo PLC Coder para o controlador PI (`Controlador_PI.st`, Apêndice F do TCC) e o arquivo aceito pelo Logic Designer (`Controlador_PI_Modificado_esperado.ST`, Apêndice H do TCC). Na versão 1, no modo estrutural, a saída do script é idêntica ao Apêndice H e, no modo completo, as linhas alteradas correspondem aos ajustes de tipo da Tabela 4 do TCC. Na versão 2, a saída é igual ao Apêndice H com a troca de tipos apenas nas seis declarações.

```
python -m unittest discover testes -v
```

## Limitações

- Versão 1: o prefixo `LREAL#` é aplicado apenas em POU sem variáveis `REAL`; se houver variáveis `REAL`, o script emite um aviso e não altera os literais daquela POU.
- Versão 2: a troca de tipos vale para todo o arquivo, de modo que, se uma conversão resultar em `REAL_TO_REAL` ou `INT_TO_INT`, o script emite um aviso para que ela seja conferida.
- As duas versões: a troca de `VAR_TEMP` por `VAR` é segura quando cada variável temporária é escrita antes de ser lida, como no controlador PI do TCC; para outros controladores, isso deve ser conferido.
- [completar dados: resultado do teste de importação no Logic Designer do arquivo gerado pela versão 1 no modo completo]
- [completar dados: resultado do teste de importação, compilação e resposta no CLP do arquivo gerado pela versão 2, com a planta em REAL ligada diretamente ao bloco]

## Repositório

[completar dados: endereço do repositório]
