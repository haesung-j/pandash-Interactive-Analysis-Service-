import os
import shutil

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from dash import Input, Output, State, dash_table, dcc, html, no_update
from typing import List


def move_plots() -> None:
    """
    pandasai가 생성한 이미지를 global variable plot_cnt를 하나씩 증가시키며 /assets 폴더 내로 이동시키는 함수
    :return: None
    """
    img_path = (os.path.join(os.getcwd(), 'assets'))
    if os.path.exists(os.path.join(img_path, 'temp_chart.png')):
        os.remove(os.path.join(img_path, 'temp_chart.png'))

    img_name = os.listdir(os.path.join(os.getcwd(), 'assets'))[0]
    old_name = os.path.join(img_path, img_name)
    os.rename(old_name, os.path.join(img_path, 'temp_chart.png'))


def generate_table(dataframe: pd.DataFrame,
                   max_rows: int = 100,
                   dark_mode: bool = False,
                   **kwargs) -> dash_table.DataTable:
    """
    pandas DataFrame을 입력받아 max_row만큼 app layout에 표현가능하도록 dash_table.DataTable 객체 반환
    :param dataframe: 표시하고자 하는 pandas DataFrame 객체
    :param max_rows: 표시하고 싶은 row의 수
    :param dark_mode: 다크 모드 여부
    """
    if dark_mode:
        style_header = {
                'backgroundColor': 'rgb(30, 30, 30)',
                'color': 'white'}
        style_data = {
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'}
    else:
        style_header = {}
        style_data = {}

    dataframe = dataframe.reset_index()
    return dash_table.DataTable(
        dataframe[:max_rows].to_dict('records'),
        columns=[{'id': c, 'name': c} for c in dataframe.columns],

        page_size=5,
        style_cell={'textAlign': 'left',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                    },
        style_header=style_header,
        style_data=style_data,
        style_table={'overflowX': 'auto'},
        tooltip_data=[
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in dataframe.to_dict('records')
        ],
        tooltip_duration=None,
        **kwargs
    )


def get_chips(data_paths: List[str]) -> list:
    """
    주어진 경로에 존재하는 파일을 읽어와 dmc.Chip()객체를 생성하는 함수
    :param data_paths: 경로
    :return: dmc.Chip 객체를 원소로 갖는 리스트 chips
    """
    chips = []
    for path in data_paths:
        if os.path.exists(path):
            for file in os.listdir(path):
                chips.append(dmc.Chip(
                    children=f'{path}: ' + file,
                    value=os.path.join(path, file),
                    variant='outline'
                ))
    if len(chips) == 0:
        chips.append(dmc.Chip(
            children="There are no files in the data folder.",
            value=None,
            variant='outline'
        ))
    return chips


def display_data_preview(file: pd.DataFrame,
                         filename: str) -> list:
    """
    데이터 프레임과 해당 파일의 이름을 입력받아 generate_table 함수를 이용하여 app layout을 구성하는 list 생성
    :param file: pandas DataFrame 객체
    :param filename: padnas DataFrame의 display name
    :return: app layout 내 children으로 입력 가능한 list
    """
    return [f'파일 이름: {filename}, shape={file.shape}',
            html.Br(),
            generate_table(file, max_rows=len(file)),
            html.Hr()]


# 대화 기록 출력 창
def textbox(text: str,
            user: bool = True) -> dbc.Card:
    """
    :param text: 출력 내용(prompt or answer)
    :param user: True면 code제외 및 오른쪽 출력, False면 Accordion(code, download) 포함 왼쪽 출력
    :return: dbc.Card 객체
    """
    style = {
        "max-width": "100%",
        "width": "max-content",
        "border-radius": 20,
        "margin-bottom": 25,
        'height': 'auto'
    }

    if user:
        style['margin-left'] = 'auto'
        style['margin-right'] = 0
        return dbc.Card(text, style=style, body=True, color="dark", inverse=True)

    else:
        style['margin-left'] = 0
        style['margin-right'] = 'auto'
        return dbc.Card(dbc.CardBody(text),
                        style=style, body=True, color="light", inverse=False)


if __name__ == '__main__':
    paths = os.path.join(os.getcwd(), 'data')
    print(get_chips(paths))

