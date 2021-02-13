*** Settings ***
Documentation     A resource file with reusable keywords and variables.
...
...               The system specific keywords created here form our own
...               domain specific language. They utilize keywords provided
...               by the imported SeleniumLibrary.
Library           SeleniumLibrary

*** Variables ***
${SERVER}         localhost:8082
${BROWSER}        Chrome
# ${BROWSER}        Firefox
${DELAY}          0
${VALID USER}     test
${VALID PASSWORD}    test123
${LOGIN URL}      http://${SERVER}/auth/login
${WELCOME URL}    http://${SERVER}/main/index
${ERROR URL}      http://${SERVER}/error.html

*** Keywords ***
Welcome Page Should Be Open
    Location Should Be    ${WELCOME URL}
    Title Should Be    Welcome

Open Browser To Login Page
    Open Browser    ${LOGIN URL}    ${BROWSER}
    Maximize Browser Window
    Set Selenium Speed    ${DELAY}
    Login Page Should Be Open

Login Page Should Be Open
    Title Should Be    Login Page

Go To Login Page
    Go To    ${LOGIN URL}
    Login Page Should Be Open

Input Username
    [Arguments]    ${username}
    Input Text    //*[@id="username"]    ${username}

Input Password
    [Arguments]    ${password}
    Input Text    //*[@id="password"]    ${password}

Submit Credentials
    Click Button    //*[@id="submit"]

