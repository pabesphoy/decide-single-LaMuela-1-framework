from django.test import TestCase, Client
from base.tests import BaseTestCase
from voting.models import Voting, Question, QuestionOption, Auth
from django.conf import settings
from base import mods
import datetime

class CensusTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.create_voting()

    def tearDown(self):
        super().tearDown()
        self.voting = None

    def create_voting(self):
        q = Question(desc='test question')
        now = datetime.datetime.now()
        opts = []
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
            opts.append({
                'option': opt.option,
                'number': opt.number,
                'votes': i
            })
        data = { 'type': 'IDENTITY', 'options': opts }
        postp = mods.post('postproc', json=data)
        v = Voting(name='test voting', question=q, postproc = postp, start_date = now, end_date = now)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def test_decide_statistics_main_page(self):
        c = Client()
        response = c.get("/decide_statistics/")
        self.assertEquals(response.status_code, 200)
        
    def test_decide_statistics_show_votings_positive(self):
        c = Client()
        graph_types = ["line", "bar", "horizontal_bar", "dots", "line"]
        for type in graph_types:
            response = c.get("/decide_statistics/?voting="+str(Voting.objects.all()[0].pk)+"&graph_type="+ type)
            self.assertEquals(response.status_code, 200)
            self.assertNotIn("Tipo de gráfico no válido", response.content.decode('utf-8'))
            self.assertIn("graph.png", response.content.decode('utf-8'))

    def test_decide_statistics_show_votings_negative(self):
        c = Client()
        graph_types = ["1", "13", "aaaaaaaaaaaaa", "."]
        for type in graph_types:
            response = c.get("/decide_statistics/?voting="+str(Voting.objects.all()[0].pk)+"&graph_type="+ type)
            self.assertEquals(response.status_code, 200)
            self.assertIn("Tipo de gráfico no válido", response.content.decode('utf-8'))
            self.assertNotIn("graph.png", response.content.decode('utf-8'))
        

    