"""Main module."""
__description__ = "This module provides the MaterialsGraphAIO class for creating interactive materials graphs."
__author__ = "Your Name"
__url__ = "data-analyzer"
__version__ = "0.1.0"
__preview__ = "/assets/preview.png" 

from dash import html, dcc, callback, Input, Output, State, MATCH, no_update, dash_table, Patch 
from dash.exceptions import PreventUpdate
import dash_ag_grid as dag
import pandas as pd
from mp_api.client import MPRester
import dash
from pymatgen.core.structure import Structure, Composition, Lattice
import altair as alt
import dash_vega_components as dvc
import plotly.graph_objects as go
import json

from mpships.vega_graph_table import VegaGraphTableAIO


class MaterialsGraphAIO(html.Div):

    class ids:
        search_bar = lambda aio:{
            "component": "MaterialsGraphAIO",
            "aio": aio,
            "subcomponents": "searchUIAIO"
        } 
        quickFilter = lambda aio:{
            "component": "MaterialsGraphAIO",
            "aio": aio,
            "subcomponents": "quickFilter"
        }
        button = lambda aio:{
            "component": "MaterialsGraphAIO",
            "aio": aio,
            "subcomponents": "button"
        }
        datatable = lambda aio:{
            "component": "MaterialsGraphAIO",
            "aio": aio,
            "subcomponents": "datatable"
        }
        vega_output = lambda aio:{
            "component": "MaterialsGraphAIO",
            "aio": aio,
            "subcomponents": "vega_output"
        }

    ids = ids 

    def __init__(self, aio, **kwargs):

        self.aio = aio
        self.kwargs = kwargs

        searchbar = html.Div(
            [
            dcc.Input(id=self.ids.search_bar(aio), type='text', placeholder='Enter chemical system'),
            html.Button('Submit', n_clicks=0,  id=self.ids.button(aio))
            ]
            )
        quick_filter = dcc.Input(id=self.ids.quickFilter(aio), type='text', placeholder='Quick Filter')

        datatable = dag.AgGrid(id=self.ids.datatable(aio), dashGridOptions={'pagination':True},)

        vega_output = dcc.Loading(html.Div(id=self.ids.vega_output(aio)))

        super().__init__(children=[
            searchbar,
            quick_filter,
            datatable,
            vega_output
        ], **kwargs)

    @callback(
        Output(ids.datatable(MATCH), "dashGridOptions"),
        Input(ids.quickFilter(MATCH), "value")
    )
    def update_filter(filter_value):
        newFilter = Patch()
        newFilter['quickFilterText'] = filter_value
        return newFilter

    @callback(
        Output(ids.datatable(MATCH), "rowData"),
        Output(ids.datatable(MATCH), "columnDefs"),
        Output(ids.vega_output(MATCH), "children"),
        Input(ids.button(MATCH), "n_clicks"),
        State(ids.search_bar(MATCH), "value"),
        prevent_initial_call=True,

    )
    def update_datatable(n_clicks, value):
        if not n_clicks:
            return no_update
        mpr = MPRester()
        docs = mpr.materials.summary.search(chemsys=value)

        doc_list = [_clean_dict(doc.model_dump()) for doc in docs]

        df = pd.DataFrame(doc_list)
        column_defs = [{"field": i} for i in df.columns]

        # create a VegaGraphTableAIO object
        vega_graph_table = VegaGraphTableAIO(aio="test", df=df)

        return df.to_dict("records"), column_defs, vega_graph_table 


def _clean_dict(d):
    """
    Remove fields with None values or custom object types from the dictionary.
    """
    cleaned_dict = {}
    for key, value in d.items():
        if value is not None and not isinstance(value, (Structure, dict, Composition, Lattice, list)) :
            cleaned_dict[key] = value
    return cleaned_dict


if __name__ == "__main__":
    app = dash.Dash(__name__)
    app.layout = html.Div(MaterialsGraphAIO(aio="test"))
    app.run_server(debug=True)


