# Copyright (C) 2023 Authors of the MCDA project - All Rights Reserved

from geo.Geoserver import Geoserver
import config

def open_conncection(url: str, user: str, password: str) -> Geoserver:
    return Geoserver(url + '/geoserver', username=user, password=password)

def create_workspace(geo: Geoserver, workspace_name: str):
    geo.create_workspace(workspace=workspace_name)

def delete_workspace(geo: Geoserver, workspace_name: str):
    geo.delete_workspace(workspace_name)

def add_featurestore(geo: Geoserver, store_name: str, workspace: str, table_name: str):
    try:
        geo.delete_featurestore(featurestore_name=store_name, workspace=workspace)
    except:
        pass

    geo.create_featurestore(store_name=store_name, workspace=workspace, db='dvan', host=config.POSTGIS_HOST, pg_user='user', pg_password='password')
    geo.publish_featurestore(workspace=workspace, store_name=store_name, pg_table=table_name)

def delete_featurestore(geo: Geoserver, store_name: str, workspace: str):
    geo.delete_featurestore(featurestore_name=store_name, workspace=workspace)

