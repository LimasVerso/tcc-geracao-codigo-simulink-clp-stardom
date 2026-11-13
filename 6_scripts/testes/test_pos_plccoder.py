"""Testes do pos_plccoder.py. Executar a partir da raiz: python -m unittest discover testes"""
import os, sys, unittest, tempfile
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import pos_plccoder as pp

EX = os.path.join(RAIZ, 'exemplos')

class TestApendices(unittest.TestCase):
    def test_estrutural_igual_apendice_H(self):
        """Entrada: Apêndice F do TCC; saída esperada: Apêndice H (arquivo aceito pelo Logic Designer)."""
        ent, _ = pp.ler(os.path.join(EX, 'Controlador_PI.st'))
        esp, _ = pp.ler(os.path.join(EX, 'Controlador_PI_Modificado_esperado.ST'))
        saida, log, pous, cod = pp.processar(ent, 'estrutural')
        self.assertEqual(saida, esp)

    def test_completo_ajustes_da_tabela_4(self):
        ent, _ = pp.ler(os.path.join(EX, 'Controlador_PI.st'))
        saida, log, pous, cod = pp.processar(ent, 'completo')
        txt = '\n'.join(saida)
        self.assertIn('CASE SINT_TO_INT(ssMethodType) OF', txt)
        for lit in ('LREAL#0.0;', 'LREAL#1.1 *', 'LREAL#1.83 *', 'LREAL#0.1)'):
            self.assertIn(lit, txt)
        self.assertIn('Model sample time               : 0.1s', txt)   # comentário intacto
        self.assertEqual(cod, 24)
        self.assertEqual(len({n for r, n, *_ in log if r in ('R1', 'R4', 'R5')}), 5)

class TestCasosLimite(unittest.TestCase):
    def test_literal_em_comentario_nao_muda(self):
        ent = ['FUNCTION_BLOCK X', 'VAR a: LREAL; END_VAR',
               '(* ganho 2.5 *) a := 2.5; // 3.5', 'END_FUNCTION_BLOCK']
        s, *_ = pp.processar(ent)
        self.assertIn('(* ganho 2.5 *) a := LREAL#2.5; // 3.5', s)

    def test_nao_duplica_prefixo_e_expoente(self):
        ent = ['FUNCTION_BLOCK X', 'VAR', 'a: LREAL;', 'END_VAR',
               'a := LREAL#1.0 + 1.0E-3;', 'END_FUNCTION_BLOCK']
        s, *_ = pp.processar(ent)
        self.assertIn('a := LREAL#1.0 + LREAL#1.0E-3;', s)

    def test_real_gera_aviso_sem_prefixo(self):
        ent = ['FUNCTION_BLOCK X', 'VAR', 'a: REAL;', 'END_VAR', 'a := 1.5;', 'END_FUNCTION_BLOCK']
        s, log, *_ = pp.processar(ent)
        self.assertIn('a := 1.5;', s)
        self.assertTrue(any(r == 'AVISO' for r, *_ in log))

    def test_varias_pous(self):
        ent = ['FUNCTION F1 : LREAL', 'VAR_INPUT u: LREAL; END_VAR', 'F1 := u;', 'END_FUNCTION',
               'FUNCTION_BLOCK B2', 'VAR_TEMP t: LREAL; END_VAR', 't := 0.5;', 'END_FUNCTION_BLOCK']
        s, log, pous, _ = pp.processar(ent)
        self.assertEqual([p['nome'] for p in pous], ['F1', 'B2'])
        self.assertEqual(s.count('IEC_LANGUAGE: ST'), 2)
        self.assertIn('NAME: B2', s)
        self.assertFalse(any(r == 'AVISO' for r, *_ in log))
        self.assertEqual(s[s.index('NAME: B2') - 1:s.index('NAME: B2')], ['(*@KEY@: WORKSHEET'])
        self.assertIn('VAR t: LREAL; END_VAR', s)

    def test_crlf_preservado(self):
        with tempfile.TemporaryDirectory() as d:
            e, o = os.path.join(d, 'e.st'), os.path.join(d, 'o.ST')
            with open(e, 'wb') as f: f.write(b'FUNCTION_BLOCK X\r\nVAR\r\na: LREAL;\r\nEND_VAR\r\na := 1.0;\r\nEND_FUNCTION_BLOCK\r\n')
            pp.main([e, '-o', o, '--relatorio', os.path.join(d, 'r.txt')])
            with open(o, 'rb') as f: dados = f.read()
            self.assertIn(b'LREAL#1.0;\r\n', dados)
            self.assertNotIn(b'\n\n', dados.replace(b'\r\n', b''))

if __name__ == '__main__':
    unittest.main()
