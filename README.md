# Geração Automática de Código para CLP com ferramentas do MATLAB/Simulink

Arquivos do Trabalho de Conclusão de Curso de João Vitor de Lima Silva, Bacharelado em Engenharia de Controle e Automação, IFSP – Campus Cubatão (2026), orientado pelo Prof. Marcelo Saraiva Coelho.

O controlador PI foi modelado no MATLAB/Simulink (R2026b online), exportado pelo Simulink PLC Coder nas rotas PLCopen XML e .st e implantado no CLP STARDOM (Yokogawa, NFJT100-H100S2U-H22-F11) através do Logic Designer.

## Conteúdo

| Pasta | Conteúdo | No TCC |
|---|---|---|
| `1_modelos_simulink/continuo` | Modelo Simulink do sistema em tempo contínuo | Seção 3.1 |
| `1_modelos_simulink/discreto` | Modelo Simulink do sistema em tempo discreto | Seção 3.1 |
| `1_modelos_simulink/subsistema_controlador` | Modelo com o controlador PI como subsistema atômico, usado na geração de código | Seções 3.1 e 3.2 |
| `2_projeto_logic_designer` | Projeto de destino no Logic Designer (`Sistema.mwt`), com as POUs `Controlador`, `Planta`, `Sistema` e `Main` | Seções 3.3 a 3.5 |
| `3_codigo_st/original` | Arquivos .st gerados pelo Simulink PLC Coder (Target IDE “Generic”) | Apêndices F e I |
| `3_codigo_st/adaptado` | Arquivos .st adaptados para a importação no Logic Designer | Apêndices H e J |
| `4_codigo_xml/original` | Arquivo PLCopen XML gerado pelo Simulink PLC Coder | Apêndice A |
| `4_codigo_xml/modificado` | Arquivos PLCopen XML modificados (namespace `tc6.xsd` e `tc6_0201`) | Apêndices C e D |
| `5_validacao_xsd` | Esquemas XSD das versões 2.01 e 1.0b do PLCopen XML e notebooks da validação (Google Colab) | Seção 3.3, Apêndice E |
| `6_scripts` | Scripts de pós-processamento da rota .st (versões 1 e 2), testes e exemplos | Seção 3.7, Apêndices K e L |

Os esquemas XSD são de autoria da PLCopen: a versão 2.01 está disponível em https://www.plcopen.org/downloads/ e a versão 1.0b foi obtida do repositório https://github.com/suifei/plcopen-go.

## Controlador PID fuzzy (Seção 3.6)

O modelo do controlador PID *fuzzy* não é distribuído aqui, por ser um exemplo da MathWorks. Ele é aberto no MATLAB (com o Fuzzy Logic Toolbox) pelo comando:

```matlab
openExample('fuzzy/GenerateStructuredTextForFuzzySystemUsingPLCCoderExample','supportingFile','fuzzyPID');
```

O código gerado e o adaptado estão em `3_codigo_st`.
