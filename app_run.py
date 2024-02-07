import base64
import io
import os
import shutil

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
from dash import Input, Output, State, dash_table, dcc, html, no_update
from dash_iconify import DashIconify
from pandasai import SmartDataframe, SmartDatalake
from pandasai.llm import OpenAI
from PIL import Image

from app_layout import make_layout
from layout_component import (display_data_preview, generate_table, move_plots, textbox)

assets_dir = os.path.join(os.getcwd(), 'assets')
if os.path.exists(assets_dir):
    shutil.rmtree(assets_dir)
os.makedirs(assets_dir)

global df  # 분석 대상 dataframe df global 변수 선언
global llm

# api_token = os.getenv('API_key')
# llm = OpenAI(api_token=api_token)
llm = None

# define layout
external_stylesheets=[dbc.themes.BOOTSTRAP]
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    assets_folder=assets_dir,
    include_assets_files=True,
    prevent_initial_callbacks="initial_duplicate"
)

app.layout = dbc.Container(
    children=[
        html.Hr(),
        make_layout()
    ]
)


@app.callback(
    Output("submit-api-token-button", "loading"),
    Input("submit-api-token-button", "n_clicks"),
    State(component_id='api-token_input', component_property='value'),
    prevent_initial_call=True,
)
def init_llm(n_clicks, api_token):
    global llm
    if n_clicks > 0:
        # 사용자로부터 입력받은 API 키를 사용하여 OpenAI 객체 초기화
        if not api_token:
            return False

        # OpenAI 객체가 초기화되지 않았다면 사용자로부터 입력받은 API 키를 사용하여 초기화
        if llm is None or llm.api_token != api_token:
            llm = OpenAI(api_token=api_token)
            return False


# 데이터 불러오기 함수
@app.callback(
    Output('output-data-uploaded', 'children'),    # Data Preview
    Output("problem-type", "children"),    # Problem type guess using llm
    Output("loading-component1", "children"),
    Input('select-data-button', 'n_clicks'),
    State('upload-data', 'contents'),
    State("chips-callback", "value"),
    State('upload-data', 'filename')
)
def chips_values(n_clicks, contents, value, filename):
    """
    dmc.chips를 통해 받은 value는 리스트 형태로 입력받음
    이와 동시에 SmartDataLake 객체를 선언하고 해당 분석 문제의 타입을 모델에게 물어보는 프롬프트를 날림
    """
    global df
    global llm
    if value is None and contents is None:
        return None, None, None
    if n_clicks > 0 and (value is not None or contents is not None):
        preview_output = []
        dfs_loaded = []

        if contents is not None:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            file = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            df_name = filename
            preview_output += display_data_preview(file, df_name)
            dfs_loaded.append(file)

        if value is not None:
            for data_path in value:
                file = pd.read_csv(data_path)
                df_name = data_path.split('\\')[-1]
                preview_output += display_data_preview(file, df_name)
                dfs_loaded.append(file)

        df = SmartDatalake(dfs_loaded, config={'llm': llm, 'save_charts': True, 'save_charts_path': 'assets'})

        result = df.chat("Is it more likely a classification, a multi-classification or a regression problem? "
                         "And what column am I more likely wanting to predict?")

        return html.Div(preview_output), result, None


@app.callback(
    Output("stepper", "active"),
    Input("stepper-next", "n_clicks"),
    Input("stepper-back", "n_clicks"),
    State("stepper", "active"),
    prevent_initial_call=True,
)
def update_stepper(stepper_next, stepper_back, current):
    ctx = dash.callback_context  # callback내에서만 사용하는 전역변수로, 어떤 component/property pair가 callback을 trigger했는지 저장하는 변수
    id_clicked = ctx.triggered[0]["prop_id"]
    if id_clicked == "stepper-next.n_clicks" and current < 2:  # stepper-next의 n_click으로 발생했다면, 그리고 ~~
        return current + 1
    elif id_clicked == "stepper-back.n_clicks":
        return current - 1
    return no_update


@app.callback(
    Output("alert-message", "children"),
    Output("alert-message", "title"),
    Output("alert-message", "hide"),
    Input("stepper", "active"),
    prevent_initial_call=True,
)
def update_alert(current):
    """
    각 페이지별 dmc.Alart components 변경
    """
    if current == 0:
        child = "유효한 OpenAI API key를 입력해주세요. 유효하지 않은 key인 경우, 추후 분석이 불가합니다."
        title = "Welcome!"
        return child, title, False
    elif current == 1:
        child = "로컬 혹은 data 폴더 내에서 데이터를 선택해주세요. 데이터는 CSV 형식이어야 합니다."\
                "1개 이상의 파일을 선택 후 Select Data 버튼을 클릭하세요.",
        title = "Select Data for Analysis"
        return child, title, False
    else:
        return None, None, True


@app.callback(
    Output("stepper-next", "disabled"),
    Output("stepper-back", "disabled"),
    Output("stepper-next", "display"),
    Output("stepper-back", "display"),
    Output("stepper-next", "children"),
    Output("icon-next", "icon"),
    Input("stepper", "active"),
    Input("output-data-uploaded", "children"),
    Input("submit-api-token-button", "n_clicks"),
)
def update_stepper_buttons(current, data, n_clicks):
    if current == 0 and n_clicks is None:
        return True, False, 'block', 'none', 'Next', "ic:round-arrow-forward"
    elif current == 0 and n_clicks > 0:
        return False, False, 'block', 'none', 'Next', "ic:round-arrow-forward"
    # 0번째 페이지고, data가 업로드 되었다면 Next button "활성화"
    if current == 1 and data is not None:
        return False, False, "block", "block", "Next", "ic:round-arrow-forward"
    # 0번째 페이지고, data가 업로드 되지 않았다면 Next button "비활성화"
    elif current == 1 and data is None:
        return True, False, "block", "block", "Next", "ic:round-arrow-forward"
    # 1번째 페이지로 넘어갔다면, Back Button 활성화 및 Next 비활성화
    elif current >= 2:
        return (
            False,
            False,
            "none",
            "block",
            "Next",
            "ic:round-arrow-forward",
        )


# submit button 클릭 시 input clear
@app.callback(
    Output("user-input", "value"),
    Input("submit-button-state", "n_clicks"),
    Input("user-input", "n_submit")
)
def clear_input(n_clicks, n_submit):
    return ""


@app.callback(
    # Output('display-conversation', 'children'),
    Output('prompt-store', 'data'),
    Input('submit-button-state', 'n_clicks'),
    State('user-input', 'value'),
    State('prompt-store', 'data')
)
def update_prompt(n_clicks, input_prompt, prompt_store):
    prompt_list = prompt_store or []  # 이전 결과를 가져와 리스트로 초기화

    if n_clicks > 0:
        prompt_list.append(input_prompt)
    return prompt_list

@app.callback(
    [Output('result-store', 'data'),
     Output("loading-component2", "children")],
    Input('submit-button-state', 'n_clicks'),
    [State('user-input', 'value'),
     State('result-store', 'data'),
     State('result-type-store', 'data')],
)
def update_result(n_clicks, input_prompt, result_store, result_type_store):
    global llm
    global df
    result_list = result_store or []  # 이전 결과를 가져와 리스트로 초기화
    result_type_list = result_type_store or []

    if n_clicks > 0:
        df.chat(input_prompt)
        result = df.last_result['value']
        result_type = df.last_result['type']
        result_type_list.append(result_type)

        if result_type == 'dataframe':
            result_list.append(generate_table(result, max_rows=len(result)))
        elif result_type in ['string', 'number']:
            result_list.append(result)
        else:
            move_plots()
            pil_image = Image.open(os.path.join(assets_dir, 'temp_chart.png'))
            result_list.append(dbc.CardImg(src=pil_image))
    return result_list, None


@app.callback(
    Output('display-conversation', 'children'),
    Output('show-code-contents', 'children'),
    Output('show-code-contents', 'is_open', allow_duplicate=True),
    Input('prompt-store', 'data'),
    Input('result-store', 'data'),
)
def update_display(prompt_list, result_list):
    global df
    display_texts = []
    code_executed = None

    for i in range(len(prompt_list)):
        display_texts.append(textbox(prompt_list[i], user=True))
        display_texts.append(textbox(result_list[i], user=False))

        # show code button 내 content
        code_executed = df.last_code_executed.split('"""')[0].replace('\n', '') + df.last_code_executed.split('"""')[-1]
        code_executed = dmc.Prism(code_executed,
                                  language="python",
                                  withLineNumbers=True)

    return display_texts, code_executed, False


# Show code button 클릭 시 Collapse open <-> close 함수
@app.callback(
    Output("show-code-contents", "is_open", allow_duplicate=True),
    [Input("show-code-button", "n_clicks")],
    [State("show-code-contents", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("download-contents", "data"),
    Input("download-button", "n_clicks"),
    prevent_initial_call=True
)
def download_contents(n_clicks):
    global df
    content = df.last_result['value']
    content_type = df.last_result['type']
    if content_type == 'dataframe':
        return dcc.send_data_frame(content.to_csv, "result.csv")
    elif content_type in ['string', 'number']:
        return dict(content=content, filename="result.txt")
    else:
        return dcc.send_file(
            os.path.join(assets_dir, "temp_chart.png")
        )


if __name__ == "__main__":
    app.run_server(debug=True, dev_tools_hot_reload=False)