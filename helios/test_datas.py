"""Testes de datas do fork helios-ptbr: início e fim da votação, limites e fusos.

O servidor guarda e compara tudo em UTC (datetime.utcnow(), sem fuso). Estes testes
provam que o fuso de quem digita ou de quem vota não muda o resultado: o que vale é o
instante em UTC. Não alteram os testes do upstream.
"""
import datetime
import types
from unittest import mock
from zoneinfo import ZoneInfo

from django.test import override_settings
from django.urls import reverse
from django_webtest import WebTest

from helios import models
from helios_auth import models as auth_models

UTC = datetime.timezone.utc

# Todos os fusos do Brasil (nomes IANA). Aragarças (GO) usa America/Sao_Paulo,
# Barra do Garças (MT) usa America/Cuiaba: cidades vizinhas, 1 hora de diferença.
FUSOS_BR = {
    'America/Noronha': -2,
    'America/Sao_Paulo': -3, 'America/Bahia': -3, 'America/Fortaleza': -3,
    'America/Recife': -3, 'America/Belem': -3, 'America/Maceio': -3,
    'America/Araguaina': -3, 'America/Santarem': -3,
    'America/Campo_Grande': -4, 'America/Cuiaba': -4, 'America/Manaus': -4,
    'America/Porto_Velho': -4, 'America/Boa_Vista': -4,
    'America/Rio_Branco': -5, 'America/Eirunepe': -5,
}
ARAGARCAS = 'America/Sao_Paulo'
BARRA_DO_GARCAS = 'America/Cuiaba'


def local_para_utc(texto, fuso):
    """'2026-12-01T09:00' digitado em `fuso` -> datetime ingênuo em UTC."""
    local = datetime.datetime.strptime(texto, '%Y-%m-%dT%H:%M').replace(tzinfo=ZoneInfo(fuso))
    return local.astimezone(UTC).replace(tzinfo=None)


def utc_para_local(utc_ingenuo, fuso):
    return utc_ingenuo.replace(tzinfo=UTC).astimezone(ZoneInfo(fuso)).replace(tzinfo=None)


def relogio(agora):
    """Troca o relógio de helios.models por um fixo (só o que o módulo usa)."""
    class Falso(datetime.datetime):
        @classmethod
        def utcnow(cls):
            return agora
    falso = types.SimpleNamespace(datetime=Falso, timedelta=datetime.timedelta, date=datetime.date,
                                  timezone=datetime.timezone)
    return mock.patch('helios.models.datetime', falso)


class FusosDoBrasilTests(WebTest):
    """Sanidade dos dados de fuso: o Brasil não tem horário de verão em 2026."""

    def test_sem_horario_de_verao_em_2026(self):
        for fuso, horas in FUSOS_BR.items():
            for mes in range(1, 13):
                for dia in (1, 15, 28):
                    d = datetime.datetime(2026, mes, dia, 12, 0, tzinfo=ZoneInfo(fuso))
                    self.assertEqual(d.utcoffset(), datetime.timedelta(hours=horas), (fuso, mes, dia))

    def test_aragarcas_e_barra_do_garcas_diferem_em_uma_hora(self):
        a = local_para_utc('2026-12-01T09:00', ARAGARCAS)
        b = local_para_utc('2026-12-01T09:00', BARRA_DO_GARCAS)
        self.assertEqual(b - a, datetime.timedelta(hours=1))


class JanelaDeVotacaoTests(WebTest):
    """voting_has_started e voting_has_stopped nos limites, para cada fuso de quem digitou."""
    fixtures = ['users.json', 'election.json']
    allow_database_queries = True

    def setUp(self):
        self.e = models.Election.objects.all()[0]
        self.e.frozen_at = datetime.datetime(2026, 11, 1, 12, 0)

    def configurar(self, fuso, inicio='2026-12-01T09:00', fim='2026-12-01T18:00'):
        self.e.voting_starts_at = local_para_utc(inicio, fuso)
        self.e.voting_ends_at = local_para_utc(fim, fuso)

    def estado(self, agora):
        with relogio(agora):
            return bool(self.e.voting_has_started()), bool(self.e.voting_has_stopped())

    def test_limites_em_todos_os_fusos(self):
        um_s = datetime.timedelta(seconds=1)
        um_us = datetime.timedelta(microseconds=1)
        for fuso in FUSOS_BR:
            self.configurar(fuso)
            ini, fim = self.e.voting_starts_at, self.e.voting_ends_at
            with self.subTest(fuso=fuso):
                self.assertEqual(self.estado(ini - um_s), (False, False))
                self.assertEqual(self.estado(ini - um_us), (False, False))
                self.assertEqual(self.estado(ini), (True, False))          # no instante exato: abre
                self.assertEqual(self.estado(ini + um_s), (True, False))
                self.assertEqual(self.estado(fim - um_us), (True, False))  # um instante antes: ainda aberto
                self.assertEqual(self.estado(fim), (True, True))           # no instante exato: fecha
                self.assertEqual(self.estado(fim + um_s), (True, True))

    def test_mesma_hora_de_parede_em_fusos_diferentes_abre_em_instantes_diferentes(self):
        """09:00 no Acre abre depois de 09:00 em Noronha: 7 horas de diferença."""
        self.configurar('America/Noronha')
        noronha = self.e.voting_starts_at
        self.configurar('America/Rio_Branco')
        acre = self.e.voting_starts_at
        self.assertEqual(acre - noronha, datetime.timedelta(hours=3))
        # Noronha UTC-2: 09:00 = 11:00 UTC. Acre UTC-5: 09:00 = 14:00 UTC.
        self.assertEqual(noronha, datetime.datetime(2026, 12, 1, 11, 0))
        self.assertEqual(acre, datetime.datetime(2026, 12, 1, 14, 0))

    def test_aragarcas_e_barra_do_garcas(self):
        """Quem criou em Barra do Garças (UTC-4) e quem vota em Aragarças (UTC-3)."""
        self.configurar(BARRA_DO_GARCAS)  # 09:00-18:00 de Barra = 13:00-22:00 UTC
        # Em Aragarças são 09:59 (12:59 UTC): ainda não abriu. Para a pessoa de Barra são 08:59.
        agora = local_para_utc('2026-12-01T09:59', ARAGARCAS)
        self.assertEqual(agora, datetime.datetime(2026, 12, 1, 12, 59))
        self.assertEqual(self.estado(agora), (False, False))
        # Em Aragarças são 10:00 (13:00 UTC): abriu. Em Barra são 09:00.
        agora = local_para_utc('2026-12-01T10:00', ARAGARCAS)
        self.assertEqual(utc_para_local(agora, BARRA_DO_GARCAS), datetime.datetime(2026, 12, 1, 9, 0))
        self.assertEqual(self.estado(agora), (True, False))
        # Em Aragarças são 18:59 (21:59 UTC): aberto. Em Barra são 17:59.
        self.assertEqual(self.estado(local_para_utc('2026-12-01T18:59', ARAGARCAS)), (True, False))
        # Em Aragarças são 19:00 (22:00 UTC): fechou. Em Barra são 18:00.
        agora = local_para_utc('2026-12-01T19:00', ARAGARCAS)
        self.assertEqual(utc_para_local(agora, BARRA_DO_GARCAS), datetime.datetime(2026, 12, 1, 18, 0))
        self.assertEqual(self.estado(agora), (True, True))

    def test_criada_em_aragarcas_vista_em_barra(self):
        self.configurar(ARAGARCAS)  # 09:00-18:00 de Aragarças = 12:00-21:00 UTC
        self.assertEqual(utc_para_local(self.e.voting_starts_at, BARRA_DO_GARCAS),
                         datetime.datetime(2026, 12, 1, 8, 0))
        self.assertEqual(utc_para_local(self.e.voting_ends_at, BARRA_DO_GARCAS),
                         datetime.datetime(2026, 12, 1, 17, 0))
        # Quando em Barra são 08:00, já abriu em Aragarças.
        self.assertEqual(self.estado(local_para_utc('2026-12-01T08:00', BARRA_DO_GARCAS)), (True, False))
        self.assertEqual(self.estado(local_para_utc('2026-12-01T07:59', BARRA_DO_GARCAS)), (False, False))

    def test_virada_de_dia_mes_e_ano(self):
        """Fim às 23:30 do dia 31/12 no Acre é 04:30 UTC de 01/01 do ano seguinte."""
        self.configurar('America/Rio_Branco', '2026-12-31T08:00', '2026-12-31T23:30')
        self.assertEqual(self.e.voting_ends_at, datetime.datetime(2027, 1, 1, 4, 30))
        self.assertEqual(self.estado(datetime.datetime(2027, 1, 1, 4, 29, 59)), (True, False))
        self.assertEqual(self.estado(datetime.datetime(2027, 1, 1, 4, 30)), (True, True))

    def test_29_de_fevereiro(self):
        self.configurar('America/Manaus', '2028-02-29T00:00', '2028-02-29T23:59')
        self.assertEqual(self.e.voting_starts_at, datetime.datetime(2028, 2, 29, 4, 0))
        self.assertEqual(self.e.voting_ends_at, datetime.datetime(2028, 3, 1, 3, 59))

    def test_sem_datas_abre_ao_congelar_e_nunca_fecha_sozinha(self):
        self.e.voting_starts_at = None
        self.e.voting_ends_at = None
        self.assertEqual(self.estado(datetime.datetime(2026, 11, 1, 12, 0)), (True, False))
        self.assertEqual(self.estado(datetime.datetime(2099, 1, 1)), (True, False))

    def test_nao_congelada_nunca_abre(self):
        self.e.frozen_at = None
        self.configurar('America/Sao_Paulo')
        self.assertEqual(self.estado(datetime.datetime(2026, 12, 1, 15, 0)), (False, False))

    def test_prorrogacao(self):
        """Prorrogar até 20:00 (Acre) = 01:00 UTC do dia seguinte."""
        self.configurar('America/Rio_Branco')  # termina 18:00 Acre = 23:00 UTC
        self.e.voting_extended_until = local_para_utc('2026-12-01T20:00', 'America/Rio_Branco')
        self.assertEqual(self.e.voting_extended_until, datetime.datetime(2026, 12, 2, 1, 0))
        self.assertEqual(self.estado(datetime.datetime(2026, 12, 1, 23, 0)), (True, False))   # passou do fim original
        self.assertEqual(self.estado(datetime.datetime(2026, 12, 2, 0, 59, 59)), (True, False))
        self.assertEqual(self.estado(datetime.datetime(2026, 12, 2, 1, 0)), (True, True))
        self.assertEqual(self.e.voting_end_at, datetime.datetime(2026, 12, 2, 1, 0))

    def test_fim_antecipado_vale_mais_que_o_fim_marcado(self):
        self.configurar('America/Sao_Paulo')  # termina 18:00 = 21:00 UTC
        self.e.voting_ended_at = datetime.datetime(2026, 12, 1, 15, 0)
        self.assertEqual(self.estado(datetime.datetime(2026, 12, 1, 14, 59, 59)), (True, False))
        self.assertEqual(self.estado(datetime.datetime(2026, 12, 1, 15, 0)), (True, True))

    def test_inicio_forcado_antes_da_data_marcada(self):
        self.configurar('America/Sao_Paulo')  # abre 09:00 = 12:00 UTC
        self.e.voting_started_at = datetime.datetime(2026, 12, 1, 10, 0)
        self.assertEqual(self.estado(datetime.datetime(2026, 12, 1, 9, 59, 59)), (False, False))
        self.assertEqual(self.estado(datetime.datetime(2026, 12, 1, 10, 0)), (True, False))

    def test_apuracao_encerra_antes_do_horario(self):
        self.configurar('America/Sao_Paulo')
        self.e.encrypted_tally = 'x'
        self.assertTrue(self.estado(datetime.datetime(2026, 12, 1, 13, 0))[1])


class FormularioDeDatasTests(WebTest):
    """O servidor lê o texto do formulário como UTC, e devolve UTC. O fuso fica no navegador."""
    fixtures = ['users.json', 'election.json']
    allow_database_queries = True

    def setUp(self):
        self.e = models.Election.objects.all()[0]
        self.user = auth_models.User.objects.get(user_id='ben@adida.net', user_type='google')
        self.client.get('/')
        s = self.client.session
        s['user'] = {'type': self.user.user_type, 'user_id': self.user.user_id}
        s.save()

    def editar(self, inicio, fim):
        url = '/helios/elections/%s/edit' % self.e.uuid
        self.client.get(url)
        return self.client.post(url, {
            'short_name': self.e.short_name, 'name': self.e.name,
            'description': self.e.description, 'election_type': self.e.election_type,
            'use_voter_aliases': self.e.use_voter_aliases,
            'voting_starts_at': inicio, 'voting_ends_at': fim,
            'csrf_token': self.client.session['csrf_token']})

    def test_guarda_exatamente_o_que_o_navegador_enviou(self):
        r = self.editar('2026-12-01T14:00', '2026-12-01T23:00')
        self.assertEqual(r.status_code, 302)
        e = models.Election.objects.get(uuid=self.e.uuid)
        self.assertEqual(e.voting_starts_at, datetime.datetime(2026, 12, 1, 14, 0))
        self.assertEqual(e.voting_ends_at, datetime.datetime(2026, 12, 1, 23, 0))

    def test_tela_de_edicao_devolve_utc_para_o_navegador_converter(self):
        self.editar('2026-12-01T14:00', '2026-12-02T01:30')
        r = self.client.get('/helios/elections/%s/edit' % self.e.uuid)
        html = r.content.decode()
        self.assertIn('value="2026-12-01T14:00"', html)
        self.assertIn('value="2026-12-02T01:30"', html)
        self.assertIn('/static/helios/timezone-display.js', html)

    def test_aceita_segundos(self):
        self.editar('2026-12-01T14:00:30', '2026-12-01T23:00:00')
        e = models.Election.objects.get(uuid=self.e.uuid)
        self.assertEqual(e.voting_starts_at, datetime.datetime(2026, 12, 1, 14, 0, 30))

    def test_vazio_limpa_a_data(self):
        self.editar('2026-12-01T14:00', '2026-12-01T23:00')
        self.editar('', '')
        e = models.Election.objects.get(uuid=self.e.uuid)
        self.assertIsNone(e.voting_starts_at)
        self.assertIsNone(e.voting_ends_at)

    def test_data_invalida_nao_grava(self):
        r = self.editar('2026-13-45T25:61', '2026-12-01T23:00')
        self.assertEqual(r.status_code, 200)
        e = models.Election.objects.get(uuid=self.e.uuid)
        self.assertIsNone(e.voting_starts_at)

    def test_conhecido_texto_com_deslocamento_vira_horario_da_california(self):
        """Comportamento do upstream (TIME_ZONE=America/Los_Angeles, USE_TZ=False).
        O navegador manda 'AAAA-MM-DDTHH:MM' sem deslocamento, então isto não acontece pela tela.
        Só um pedido feito à mão com 'Z' ou '-03:00' cai aqui, e o valor guardado fica errado."""
        self.editar('2026-12-01T14:00Z', '')
        e = models.Election.objects.get(uuid=self.e.uuid)
        self.assertEqual(e.voting_starts_at, datetime.datetime(2026, 12, 1, 6, 0))  # devia ser 14:00

    def test_prorrogar(self):
        url = '/helios/elections/%s/extend' % self.e.uuid
        self.client.get(url)
        r = self.client.post(url, {'voting_extended_until': '2026-12-02T01:00',
                                   'csrf_token': self.client.session['csrf_token']})
        self.assertEqual(r.status_code, 302)
        e = models.Election.objects.get(uuid=self.e.uuid)
        self.assertEqual(e.voting_extended_until, datetime.datetime(2026, 12, 2, 1, 0))


class PaginaDeVotoTests(WebTest):
    """O atalho /vote mostra 'ainda não começou' ou 'já terminou' conforme o instante em UTC."""
    fixtures = ['users.json', 'election.json']
    allow_database_queries = True

    def setUp(self):
        self.e = models.Election.objects.all()[0]
        self.e.frozen_at = datetime.datetime(2026, 11, 1, 12, 0)
        self.e.voting_starts_at = local_para_utc('2026-12-01T09:00', BARRA_DO_GARCAS)  # 13:00 UTC
        self.e.voting_ends_at = local_para_utc('2026-12-01T18:00', BARRA_DO_GARCAS)    # 22:00 UTC
        self.e.save()
        self.url = '/helios/e/%s/vote' % self.e.short_name

    def abrir(self, agora):
        with relogio(agora):
            return self.client.get(self.url)

    def test_antes_do_inicio(self):
        r = self.abrir(datetime.datetime(2026, 12, 1, 12, 59, 59))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'helios/templates/election_not_started.html')

    def test_no_inicio_redireciona_para_a_cabine(self):
        r = self.abrir(datetime.datetime(2026, 12, 1, 13, 0))
        self.assertEqual(r.status_code, 302)

    def test_no_fim_mostra_encerrada(self):
        r = self.abrir(datetime.datetime(2026, 12, 1, 22, 0))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'helios/templates/election_tallied.html')

    def test_um_instante_antes_do_fim_ainda_vota(self):
        r = self.abrir(datetime.datetime(2026, 12, 1, 21, 59, 59))
        self.assertEqual(r.status_code, 302)

    def test_resultado_independe_do_fuso_de_quem_acessa(self):
        """Quem acessa de Aragarças ou de Barra no mesmo instante vê a mesma página."""
        instante = local_para_utc('2026-12-01T09:59', ARAGARCAS)  # 12:59 UTC, 08:59 em Barra
        self.assertEqual(utc_para_local(instante, BARRA_DO_GARCAS), datetime.datetime(2026, 12, 1, 8, 59))
        self.assertTemplateUsed(self.abrir(instante), 'helios/templates/election_not_started.html')
        instante = local_para_utc('2026-12-01T10:00', ARAGARCAS)  # 13:00 UTC, 09:00 em Barra
        self.assertEqual(self.abrir(instante).status_code, 302)
