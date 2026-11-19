"""Teste do fork helios-ptbr: a apuração lê as cédulas em lotes (`iterator`).

Sem isso, `Election.compute_tally` carrega todos os eleitores na memória (9,5 GiB com 50 mil
eleitores). Medições em docs/relatorio-carga.md. Não altera os testes do upstream.
"""
from unittest import mock

from django.test import SimpleTestCase

from helios import models


class ApuracaoEmLotesTest(SimpleTestCase):
    def test_compute_tally_usa_iterator_com_lote_de_500(self):
        votos = ['voto-1', 'voto-2', 'voto-3']
        eleitores = [mock.Mock(vote=v) for v in votos]
        qs = mock.MagicMock()
        qs.iterator.return_value = iter(eleitores)
        eleicao = models.Election()
        tally = mock.Mock()
        with mock.patch.object(models.Election, 'voter_set', new_callable=mock.PropertyMock) as vs, \
                mock.patch.object(models.Election, 'init_tally', return_value=tally), \
                mock.patch.object(models.Election, 'save') as salvar:
            vs.return_value.exclude.return_value = qs
            eleicao.compute_tally()
        qs.iterator.assert_called_once_with(chunk_size=500)
        self.assertEqual([c.args[0] for c in tally.add_vote.call_args_list], votos)
        salvar.assert_called_once()
        self.assertIs(eleicao.encrypted_tally, tally)
