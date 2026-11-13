"""Testes do pos_plccoder_v2.py. Executar a partir da raiz: python -m unittest discover testes"""
import os, sys, unittest
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import pos_plccoder_v2 as pp

EX = os.path.join(RAIZ, 'exemplos')

class TestApendicesV2(unittest.TestCase):
    def test_pi_igual_apendice_H_com_tipos_trocados(self):
        """Saída = Apêndice H com LREAL -> REAL e SINT -> INT apenas nas declarações."""
        ent, _ = pp.ler(os.path.join(EX, 'Controlador_PI.st'))
        esp, _ = pp.ler(os.path.join(EX, 'Controlador_PI_Modificado_esperado.ST'))
        esp = [l.replace('SINT;', 'INT;').replace('LREAL;', 'REAL;') if l.strip().endswith(('SINT;', 'LREAL;')) else l
               for l in esp]
        saida, log, pous, cod = pp.processar(ent)
        self.assertEqual(saida, esp)
        self.assertNotIn('LREAL#', '\n'.join(saida))
        self.assertIn('CASE ssMethodType OF', saida)
        self.assertEqual(len({n for r, n, *_ in log if r in ('R1', 'R6')}), 7)

class TestCasosLimiteV2(unittest.TestCase):
    def test_comentario_intacto_e_usint_preservado(self):
        ent = ['FUNCTION_BLOCK X', 'VAR', 'a: LREAL; (* tipo LREAL *)', 'b: USINT;', 'c: SINT;', 'END_VAR',
               'a := 1.5;', 'END_FUNCTION_BLOCK']
        s, *_ = pp.processar(ent)
        self.assertIn('a: REAL; (* tipo LREAL *)', s)
        self.assertIn('b: USINT;', s)
        self.assertIn('c: INT;', s)
        self.assertIn('a := 1.5;', s)

    def test_literais_tipados_e_conversoes(self):
        ent = ['FUNCTION F : LREAL', 'VAR_INPUT u: SINT; END_VAR',
               'F := SINT_TO_LREAL(u) * LREAL#2.0 + LREAL_TO_SINT(SINT#3);', 'END_FUNCTION']
        s, log, *_ = pp.processar(ent)
        self.assertIn('FUNCTION F : REAL', s)
        self.assertIn('F := INT_TO_REAL(u) * REAL#2.0 + REAL_TO_INT(INT#3);', s)

    def test_aviso_conversao_redundante(self):
        ent = ['FUNCTION_BLOCK X', 'VAR', 'a: REAL;', 'b: LREAL;', 'END_VAR', 'b := REAL_TO_LREAL(a);', 'END_FUNCTION_BLOCK']
        s, log, *_ = pp.processar(ent)
        self.assertIn('b := REAL_TO_REAL(a);', s)
        self.assertTrue(any(r == 'AVISO' for r, *_ in log))

if __name__ == '__main__':
    unittest.main()
