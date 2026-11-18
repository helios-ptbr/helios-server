"""Testa timezone-display.js no Chromium com cada fuso do Brasil (variável TZ).

Prova, para cada fuso:
1. ao abrir o formulário, o UTC do servidor aparece como horário local;
2. ao enviar, o horário local digitado volta como UTC;
3. abrir e enviar sem mexer não muda a data.
E testa todos os pares "quem criou" x "quem olha", inclusive Aragarças x Barra do Garças.
Pula se não houver Chromium.
"""
import datetime
import sys
import unittest
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fusos_harness

UTC = datetime.timezone.utc
FMT = '%Y-%m-%dT%H:%M'

FUSOS_BR = [
    'America/Noronha',
    'America/Sao_Paulo', 'America/Bahia', 'America/Fortaleza', 'America/Recife', 'America/Belem',
    'America/Maceio', 'America/Araguaina', 'America/Santarem',
    'America/Campo_Grande', 'America/Cuiaba', 'America/Manaus', 'America/Porto_Velho', 'America/Boa_Vista',
    'America/Rio_Branco', 'America/Eirunepe',
]
ARAGARCAS = 'America/Sao_Paulo'
BARRA_DO_GARCAS = 'America/Cuiaba'

DIAS = ['2026-01-01', '2026-03-01', '2026-06-30', '2026-10-31', '2026-12-01', '2026-12-31', '2028-02-29']
HORAS = ['00:00', '00:01', '08:59', '09:00', '12:00', '17:59', '18:00', '22:00', '23:00', '23:59']
LOCAIS = ['%sT%s' % (d, h) for d in DIAS for h in HORAS]


def local_para_utc(texto, fuso):
    d = datetime.datetime.strptime(texto, FMT).replace(tzinfo=ZoneInfo(fuso))
    return d.astimezone(UTC).strftime(FMT)


def utc_para_local(texto, fuso):
    d = datetime.datetime.strptime(texto, FMT).replace(tzinfo=UTC)
    return d.astimezone(ZoneInfo(fuso)).strftime(FMT)


@unittest.skipUnless(fusos_harness.navegador(), "precisa de chromium ou google-chrome")
class FusosNoNavegadorTests(unittest.TestCase):

    def test_digitar_local_envia_utc_em_todos_os_fusos(self):
        casos = [{'utc': '2026-01-01T00:00', 'digitado': t} for t in LOCAIS]
        for fuso in FUSOS_BR:
            with self.subTest(fuso=fuso):
                saida = fusos_harness.executar(fuso, casos)
                self.assertEqual(saida['tz'], fuso)
                self.assertEqual(saida['enviado'], [local_para_utc(t, fuso) for t in LOCAIS])

    def test_abrir_mostra_o_utc_como_local_em_todos_os_fusos(self):
        utcs = list(LOCAIS)  # cada valor é lido como UTC
        casos = [{'utc': t} for t in utcs]
        for fuso in FUSOS_BR:
            with self.subTest(fuso=fuso):
                saida = fusos_harness.executar(fuso, casos)
                self.assertEqual(saida['aberto'], [utc_para_local(t, fuso) for t in utcs])

    def test_abrir_e_enviar_sem_mexer_nao_muda_a_data(self):
        casos = [{'utc': t} for t in LOCAIS]
        for fuso in FUSOS_BR:
            with self.subTest(fuso=fuso):
                saida = fusos_harness.executar(fuso, casos)
                self.assertEqual(saida['enviado'], LOCAIS)

    def test_data_com_texto_mostra_utc_e_local(self):
        for fuso in FUSOS_BR:
            with self.subTest(fuso=fuso):
                saida = fusos_harness.executar(fuso, [], ts='2026-12-01 12:00')
                local = utc_para_local('2026-12-01T12:00', fuso)[-5:]
                self.assertIn('12:00 UTC', saida['ts'])
                self.assertIn(local, saida['ts'])

    def test_fuso_de_quem_digita_nao_muda_o_instante_para_quem_olha(self):
        """Cada pessoa cria no seu fuso; cada outra pessoa abre no seu e vê o mesmo instante."""
        digitado = ['2026-12-01T09:00', '2026-12-01T18:00', '2026-12-31T23:30', '2026-12-01T00:00']
        enviados = {}
        for criador in FUSOS_BR:
            saida = fusos_harness.executar(criador, [{'utc': '2026-01-01T00:00', 'digitado': t} for t in digitado])
            enviados[criador] = saida['enviado']
            self.assertEqual(saida['enviado'], [local_para_utc(t, criador) for t in digitado])
        for leitor in FUSOS_BR:
            casos, rotulos = [], []
            for criador, utcs in enviados.items():
                for t, u in zip(digitado, utcs):
                    casos.append({'utc': u})
                    rotulos.append((criador, t))
            saida = fusos_harness.executar(leitor, casos)
            for (criador, t), visto in zip(rotulos, saida['aberto']):
                with self.subTest(criador=criador, leitor=leitor, digitado=t):
                    instante = datetime.datetime.strptime(t, FMT).replace(tzinfo=ZoneInfo(criador))
                    visto_dt = datetime.datetime.strptime(visto, FMT).replace(tzinfo=ZoneInfo(leitor))
                    self.assertEqual(visto_dt, instante)

    def test_aragarcas_e_barra_do_garcas(self):
        """Mesmo instante, duas cidades vizinhas, uma hora de diferença na tela."""
        barra = fusos_harness.executar(BARRA_DO_GARCAS, [{'utc': '2026-01-01T00:00', 'digitado': '2026-12-01T09:00'}])
        self.assertEqual(barra['enviado'], ['2026-12-01T13:00'])    # criou às 09:00 em Barra
        arag = fusos_harness.executar(ARAGARCAS, [{'utc': '2026-12-01T13:00'}])
        self.assertEqual(arag['aberto'], ['2026-12-01T10:00'])      # Aragarças vê 10:00
        arag = fusos_harness.executar(ARAGARCAS, [{'utc': '2026-01-01T00:00', 'digitado': '2026-12-01T09:00'}])
        self.assertEqual(arag['enviado'], ['2026-12-01T12:00'])     # criou às 09:00 em Aragarças
        barra = fusos_harness.executar(BARRA_DO_GARCAS, [{'utc': '2026-12-01T12:00'}])
        self.assertEqual(barra['aberto'], ['2026-12-01T08:00'])     # Barra vê 08:00

    def test_ingles_e_portugues_enviam_o_mesmo_valor(self):
        casos = [{'utc': '2026-01-01T00:00', 'digitado': '2026-12-01T09:00'}]
        a = fusos_harness.executar('America/Rio_Branco', casos, lang='pt-BR')
        b = fusos_harness.executar('America/Rio_Branco', casos, lang='en')
        self.assertEqual(a['enviado'], b['enviado'])


if __name__ == '__main__':
    unittest.main()
