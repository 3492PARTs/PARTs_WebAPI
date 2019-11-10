from datetime import datetime

import pytz
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, connection
from django.db.models.functions import TruncMonth
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from api.api.serializers import *
from .models import *
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response


class MainQueryParameters(APIView):
    """
    API endpoint to get a list of all of the locations, base stations, and nodes and time to search on
    """

    def generate_data(self):
        ret = dict()

        ret['locs'] = []

        loc = Location.objects.filter(void_ind='n')

        for l in loc:
            l_temp = dict()

            l_temp['loc_id'] = l.loc_id
            l_temp['loc_nm'] = l.loc_nm
            l_temp['checked'] = False

            bs = BaseStation.objects.filter(Q(loc=l) & Q(void_ind='n'))
            bss_temp = []

            for b in bs:
                bs_temp = dict()

                bs_temp['base_id'] = b.base_id
                bs_temp['base_nm'] = b.base_nm
                bs_temp['checked'] = False

                no = Node.objects.filter(Q(base=b) & Q(void_ind='n') & ~Q(model_typ_cd_id='r'))
                nos_temp = []

                for n in no:
                    no_temp = dict()

                    no_temp['node_id'] = n.node_id
                    no_temp['node_nm'] = n.node_nm
                    no_temp['checked'] = False

                    nos_temp.append(no_temp)

                bs_temp['nodes'] = nos_temp
                bss_temp.append(bs_temp)

            l_temp['bases'] = bss_temp
            ret['locs'].append(l_temp)
            ret['date_st'] = timezone.now() - timezone.timedelta(days=1)
            ret['date_end'] = timezone.now()

            ret['date_st'] = ret['date_st'].strftime("%Y-%m-%d %H:%M").replace(" ", "T")
            ret['date_end'] = ret['date_end'].strftime("%Y-%m-%d %H:%M").replace(" ", "T")

        return ret

    def get(self, request, format=None):
        ret = self.generate_data()
        serializer = MainQuerySerializer(ret)
        return Response(serializer.data)


class GetData(APIView):
    """
    API endpoint to get data based on the modified Query Parameters
    """

    def generate_data(self, req):
        req['date_st'] = datetime.strptime(req['date_st'].replace('T', ' ') + ' +0000', '%Y-%m-%d %H:%M %z')
        req['date_end'] = datetime.strptime(req['date_end'].replace('T', ' ') + ' +0000', '%Y-%m-%d %H:%M %z')

        print(req['date_st'].astimezone())

        for l in req['locs']:
            for b in l['bases']:
                for n in b['nodes']:
                    if n['checked']:
                        node = Node.objects.get(Q(node_id=n['node_id']) & Q(void_ind='n'))

                        sens_typ_cds = []

                        if node.model_typ_cd.s1 is not None:
                            sens_typ_cds.append(node.model_typ_cd.s1)
                        if node.model_typ_cd.s2 is not None:
                            sens_typ_cds.append(node.model_typ_cd.s2)
                        if node.model_typ_cd.s3 is not None:
                            sens_typ_cds.append(node.model_typ_cd.s3)
                        if node.model_typ_cd.s4 is not None:
                            sens_typ_cds.append(node.model_typ_cd.s4)
                        if node.model_typ_cd.s5 is not None:
                            sens_typ_cds.append(node.model_typ_cd.s5)

                        for s in sens_typ_cds:
                            """data = Data.objects.values_list('data', 'audit_user_crea_dtm')\
                                .filter(
                                    Q(node=node) &
                                    Q(sens_typ_cd=s) &
                                    Q(audit_user_crea_dtm__range=(req['date_st'], req['date_end'])) &
                                    Q(void_ind='n')
                                ).order_by('-audit_user_crea_dtm')"""

                            point = Data.objects.values_list('data', flat=True) \
                                .filter(
                                Q(node=node) &
                                Q(sens_typ_cd=s) &
                                Q(audit_user_crea_dtm__range=(req['date_st'], req['date_end'])) &
                                Q(void_ind='n')
                            ).order_by('audit_user_crea_dtm')

                            """time = Data.objects.values_list('audit_user_crea_dtm', flat=True) \
                                .filter(
                                Q(node=node) &
                                Q(sens_typ_cd=s) &
                                Q(audit_user_crea_dtm__range=(req['date_st'], req['date_end'])) &
                                Q(void_ind='n')
                            ).order_by('audit_user_crea_dtm')"""

                            time = list(Data.objects.extra(select={
                                'date': "date_format(audit_user_crea_dtm, \'%%y/%%m/%%e %%l:%%i %%p\')"}).values_list(
                                'date', flat='true').filter(
                                Q(node=node) &
                                Q(sens_typ_cd=s) &
                                Q(audit_user_crea_dtm__range=(req['date_st'], req['date_end'])) &
                                Q(void_ind='n')
                            ).order_by('audit_user_crea_dtm'))


                            if n.get('dataset', None) is None:
                                n['dataset'] = []

                            #n['dataset'].append({'sens': s.sens_nm, 'values': list(data)})
                            n['dataset'].append({'sens': s.sens_nm, 'lineChartData': [{'data': list(point), 'label': s.sens_nm}], 'lineChartLabels': list(time)})
        return req

    def post(self, request, format=None):
        serializer = MainQuerySerializer(data=request.data)
        if serializer.is_valid():
            req = self.generate_data(serializer.data)
            serializer = MainQuerySerializer(req)
            return Response(serializer.data)
        return HttpResponse(status=400)


class InsertData(APIView):
    """
    API endpoint to insert data
    """

    def insert_data(self, req):
        date = timezone.now()  # TODO make sure time zone stuff
        try:
            n = Node.objects.get(Q(node_id=req['node_id']) & Q(void_ind='n'))

            if req.get('dataset', False):
                for dp in req['dataset']:
                    d = Data(sens_typ_cd_id=dp['sens_typ_cd'], data=dp['data'], node=n, loc=n.loc, audit_user_crea_id=1, audit_user_crea_dtm=date)
                    d.save()

            if req.get('error_list', False):
                for er in req['error_list']:
                    e = Error(err_def_id=er, node=n, audit_user_crea_id=1, audit_user_crea_dtm=date)
                    e.save()

            n.heartbeat = date
            n.base_id = req['base_id']
            n.audit_user_upd_id = 1
            n.audit_user_upd_dtm = date

            n.save()

            return HttpResponse(status=200)
        except ObjectDoesNotExist as e:
            print(e)
            return HttpResponse(status=400)
        except IntegrityError as e:
            print(e)
            return HttpResponse(status=400)

    def post(self, request, format=None):
        print(request.data)
        serializer = InsertDataSerializer(data=request.data)
        if serializer.is_valid():
            return self.insert_data(serializer.data)
        print(request.content_type)
        print(serializer.errors)
        return HttpResponse(status=400)
