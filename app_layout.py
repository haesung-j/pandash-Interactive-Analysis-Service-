import os
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import Input, Output, State, dash_table, dcc, html, no_update
from dash_iconify import DashIconify

from layout_component import get_chips

def user_input() -> dbc.InputGroup:
    return dbc.InputGroup(
        children=[
            dbc.Input(id="user-input", placeholder="Write to the pandasAI...", type="text",
                      ),
            dbc.Button(id="submit-button-state", children="submit!", n_clicks=0,
                       color='dark')
    ]
)


def conversation() -> html.Div:
    """
    대화 history를 아래서부터 위로 출력하도록 정의
    """
    return html.Div(
        html.Div(id="display-conversation"),
        style={
            "overflow-y": "auto",
            "display": "flex",
            "height": "calc(90vh - 200px)",
            "flex-direction": "column-reverse",
        },
    )


def make_layout() -> dmc.Stack:
    ui = user_input()
    conv = conversation()

    layout = dmc.Stack(
        [
            dmc.Alert(
                children="유효한 OpenAI API key를 입력해주세요. 유효하지 않은 key인 경우, 추후 분석이 불가합니다.",
                title="Welcome!",
                id="alert-message",
                color="dark",
                withCloseButton=True
            ),
            dmc.Stepper(
                id="stepper",
                contentPadding=30,
                active=0,
                size="md",
                breakpoint="sm",
                color='black',
                children=[
                    # 1번째 페이지: API key 제출란
                    dmc.StepperStep(
                        label="OpenAI API key",
                        description="API key를 입력하세요.",
                        icon=DashIconify(icon="bi:bar-chart"),
                        progressIcon=DashIconify(icon="bi:key"),
                        completedIcon=DashIconify(icon="bi:key-fill"),
                        color='black',
                        children=[
                            dbc.Container(
                                children=[
                                    html.Hr(),
                                    dmc.Center(
                                        children=[
                                            dmc.PasswordInput(id='api-token_input',
                                                              placeholder='API 키를 입력하세요...',
                                                              label="Your API key",
                                                              ml=10, mt=20, mr=10,
                                                              size='sm',
                                                              required=True,
                                                              style={'width': '70%'}
                                                              ),
                                            dmc.Button(id='submit-api-token-button',
                                                       children="Submit",
                                                       color='dark',
                                                       mt=47
                                                       ),
                                        ]
                                    ),
                                ]
                            )
                        ]
                    ),
                    # 2번째 페이지: 데이터 업로드
                    dmc.StepperStep(
                        label="Upload CSV files",
                        description="csv 파일을 선택하세요.",
                        icon=DashIconify(icon="line-md:upload-outline"),
                        progressIcon=DashIconify(icon="line-md:upload-loop"),
                        completedIcon=DashIconify(icon="line-md:upload-outline"),
                        color='black',
                        children=[
                            dmc.Stack(
                                [
                                    # dmc.Alert(
                                    #     "로컬 혹은 data 폴더 내에서 데이터를 선택해주세요. 데이터는 CSV 형식이어야 합니다."
                                    #     "1개 이상의 파일을 선택 후 Select Data 버튼을 클릭하세요.",
                                    #     title="Select Data for Analysis",
                                    #     color="dark",
                                    # ),
                                    dmc.Title("Local Upload", order=4, color="primary"),
                                    dcc.Upload(
                                        id="upload-data",
                                        children=html.Div(
                                            [
                                                "Drag and Drop or",
                                                dmc.Button(
                                                    "Select CSV File",
                                                    ml=10,
                                                    color='dark',
                                                    leftIcon=DashIconify(
                                                        icon="material-symbols:upload"
                                                    ),
                                                ),
                                            ]
                                        ),
                                        max_size=5 * 1024 * 1024,  # 5MB
                                        style={
                                            "borderWidth": "1px",
                                            "borderStyle": "dashed",
                                            "borderRadius": "5px",
                                            "textAlign": "center",
                                            "padding": "10px",
                                            "backgroundColor": "#fafafa",
                                        },
                                        style_reject={
                                            "borderColor": "red",
                                        },
                                        multiple=False,
                                    ),
                                    html.Hr(),
                                    # 실행 위치 data 폴더 내 label:filename을 children으로 갖는 Chips 생성 파트
                                    dmc.Title("Data Folder", order=4, color="primary"),
                                    dmc.ChipGroup(
                                        children=get_chips([os.path.join(os.getcwd(), 'data'),
                                                            os.path.join(os.getcwd(), 'data2')]),
                                        id='chips-callback',
                                        multiple=True,
                                        mb=10
                                    ),
                                    dmc.Center(
                                        dmc.Button("Select Data",
                                                   id='select-data-button',
                                                   color='dark',
                                                   style={"padding": "10px",
                                                          'width': '140px',
                                                          'height': '37px',
                                                          'display': 'inline-block'})
                                    ),
                                    # 작업 완료 시까지 spinner
                                    dbc.Spinner(html.Div(id="loading-component1")),
                                    html.Hr(),
                                    # 불러온 데이터 출력 파트
                                    dmc.Title("Data Preview", order=4, color="primary"),
                                    html.Div(id="output-data-uploaded"),
                                ]
                            )
                        ],
                    ),
                    # 3번째 페이지: pandas ai 채팅창
                    dmc.StepperStep(
                        label="Analyze Your Data",
                        description="대화형으로 분석하세요🔥",
                        icon=DashIconify(icon="cil:zoom"),
                        progressIcon=DashIconify(icon="cil:zoom"),
                        completedIcon=DashIconify(icon="cil:zoom"),
                        color='black',
                        children=[
                            dmc.Alert(
                                # "대화 형식으로 데이터를 분석해보세요!",
                                title="Tip!",
                                color="dark",
                                id='problem-type',
                                withCloseButton=True
                            ),
                            dbc.Container(
                                fluid=False,
                                children=[
                                    dcc.Store(id='prompt-store'),
                                    dcc.Store(id='result-store'),
                                    dcc.Store(id='result-type-store'),
                                    conv,
                                    html.Div([
                                        # dbc Collapse 사용해도 됨(Collapse는 클릭 시 아래 숨겨진 창 생기고 다시 클릭하면 사라짐)
                                        dbc.Button('Show Code', outline=True, color='dark', id='show-code-button',
                                                   size="sm", n_clicks=0),
                                        dbc.Button('Download Result', outline=True, color='dark', id='download-button',
                                                   size="sm"),
                                        dcc.Download(id="download-contents"),
                                        dbc.Button("Execute Code", outline=True, color='dark', id='execute-code-button',
                                                   size="sm"),
                                        dbc.Collapse(
                                            id="show-code-contents",
                                            # is_open=False,
                                        ),
                                    ]),
                                    ui,
                                    dbc.Spinner(html.Div(id="loading-component2")),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # Back, Next 버튼
            dmc.Group(
                [
                    dmc.Button(
                        "Back",
                        id="stepper-back",
                        display="none",
                        size="md",
                        variant="outline",
                        radius="xl",
                        color='dark',
                        leftIcon=DashIconify(icon="ic:round-arrow-back"),
                    ),
                    dmc.Button(
                        "Next",
                        id="stepper-next",
                        size="md",
                        radius="xl",
                        color='dark',
                        rightIcon=DashIconify(
                            icon="ic:round-arrow-forward", id="icon-next"
                        ),
                    ),
                ],
                position="center",
                mb=20,
            ),
        ]
    )

    return layout
