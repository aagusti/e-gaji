import os
import uuid
from ..tools import row2dict, xls_reader
from datetime import datetime
from sqlalchemy import not_, func
from pyramid.view import (
    view_config,
    )
from pyramid.httpexceptions import (
    HTTPFound,
    )
import colander
from deform import (
    Form,
    widget,
    ValidationFailure,
    )
from ..models import (
    DBSession,
    Group
    )
from ..models.gaji import GajiPegawai

from datatables import ColumnDT, DataTables
from ..views.base_view import BaseViews
    

SESS_ADD_FAILED = 'Tambah gaji gagal'
SESS_EDIT_FAILED = 'Edit gaji gagal'
       

class AddSchema(colander.Schema):
    nip = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(max=18),
                    title = "NIP" )
                    
    nama = colander.SchemaNode(
                    colander.String(),
                    readonly=True)

    gaji_kotor = colander.SchemaNode(
                    colander.Integer(),
                    readonly=True)
    potongan = colander.SchemaNode(
                    colander.Integer(),
                    readonly=True)
    gaji_bersih = colander.SchemaNode(
                    colander.Integer(),
                    readonly=True)
                    

class EditSchema(AddSchema):
    pass

class view_gajipegawai(BaseViews):
    ########                    
    # List #
    ########    
    @view_config(route_name='gaji', renderer='templates/gajipegawai/list.pt',
                 permission='edit')
    def view_gaji(self):
        return dict(a={})
        
    ##########                    
    # Action #
    ##########    
    @view_config(route_name='gaji-act', renderer='json',
                 permission='edit')
    def gaji_act(self):
        ses = self.request.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        
        if url_dict['act']=='grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('nip'))
            columns.append(ColumnDT('nama'))
            columns.append(ColumnDT('gaji_kotor',  filter=self._number_format))
            columns.append(ColumnDT('potongan',  filter=self._number_format))
            columns.append(ColumnDT('gaji_bersih',  filter=self._number_format))
            query = DBSession.query(GajiPegawai).filter(
                      GajiPegawai.tahun == ses['tahun'],
                      GajiPegawai.bulan == ses['bulan'],
                      GajiPegawai.unitkd == ses['unit_kd'],
                    )
            rowTable = DataTables(req, GajiPegawai, query, columns)
            return rowTable.output_result()
