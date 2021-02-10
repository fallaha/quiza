
// initial
// gotoURL(login_page(),'login','login')
class quizaHandler {
    constructor() {
        this.current_quiz = null
        this.current_question = null
        this.all_quizzes = null
        this.token = null
        this.QuestionType = {
            MultiOption: 1,
            Textual: 2,
            FileUpload: 4
        }
        this.quizViewId = 1
        this.question_timer = null
        this.question_timer_count = 0

    }

    setQuizViewMode(id) {
        this.quizViewId = parseInt(id)
    }
    getQuizViewMode() {
        return this.quizViewId
    }

    setAllQuizzes(quizzes) {
        this.all_quizzes = quizzes
    }

    getAllQuizzes() {
        return this.all_quizzes
    }

    setCurrentQuiz(quiz) {
        this.current_quiz = quiz;
    }
    getCurrentQuiz() {
        return this.current_quiz
    }
    setCurrentQuestion(question) {
        this.current_question = question
    }
    getCurrentQuestion() {
        return this.current_question
    }
    getAuthorizationToken() {
        let token = getCookie('token')
        //console.log(token)
        if (token == null) {
            gotoLoginPage();
            return;
        }
        return "Bearer " + token
    }

    getQuizByUuidOffline(uuid) {
        return this.all_quizzes.find(quiz => quiz.uuid === uuid)
    }

    async postRequest(url, body = "") {
        var myHeaders = new Headers();
        myHeaders.append("Authorization", this.getAuthorizationToken());

        var requestOptions = {
            method: 'POST',
            headers: myHeaders,
            redirect: 'follow',
            body: body
        };
        let request = await fetch(url, requestOptions)
        let json_response = await request.json()
        //console.log(json_response)
        return json_response
    }

    async getRequest(url) {
        var myHeaders = new Headers();
        myHeaders.append("Authorization", this.getAuthorizationToken());

        var requestOptions = {
            method: 'GET',
            headers: myHeaders,
            redirect: 'follow',
        };
        let request = await fetch(url, requestOptions)
        let json_response = await request.json()
        //console.log(json_response)
        return json_response
    }

    async sendAnswer(answer) {
        var raw = JSON.stringify(answer)
        let response = await this.postRequest(`http://localhost/quiz/${this.current_quiz.uuid}/question/${this.current_question.number}/answer`, raw)
        return response
    }



    startTimerForQuestion(seconds){
        var question_timer_count = seconds
        let setTimerToHtml = () => {

            let seconds = question_timer_count % 60
            let minutes = Math.floor(question_timer_count / 60 % 60)
            let hour = Math.floor(question_timer_count / 3600 % 24)
            question_timer_count -= 1
            let check_question_page = document.querySelector(".question .header .remaining-time #timer-seconds")
            if (check_question_page === null){
                clearInterval(this.question_timer);
                return
            }
            document.querySelector(".question .header .remaining-time #timer-seconds").innerText = seconds
            document.querySelector(".question .header .remaining-time #timer-minutes").innerText = minutes
            document.querySelector(".question .header .remaining-time #timer-hour").innerText = hour

            if (question_timer_count <= 0) {
                clearInterval(this.question_timer);
                nextQuestionClicked()
                //console.log("line 121 :) ",this.current_question)
            }
        }
        if (this.question_timer !== null){
            clearInterval(this.question_timer);
        }
        //console.log("line 127 :) ",this.current_question)
        this.question_timer = setInterval(setTimerToHtml, 1000);
    }

    stopTimerForQuestion(){
        clearInterval(this.question_timer);
    }
}



let quiza = new quizaHandler()
gotoHomePage()

window.onhashchange = function () {
    //console.log("changed page")
}

window.onpopstate = function (e) {
    if (e.state) {
        document.getElementById("root").innerHTML = e.state.html;
        document.title = e.state.pageTitle;
    }
};

function gotoLoginPage() {
    gotoURL(login_page(), 'ورود', '/login')
}

function gotoRegisterPage() {
    gotoURL(register_page(), 'ثبت نام', '/register')
}
async function gotoHomePage() {
    json_response = await quiza.getRequest("http://localhost/quizzes")
    quiza.setAllQuizzes(json_response.data.quizzes)
    user_home_page().then(html => gotoURL(html, 'خانه', '/panel'))

}
function gotoQuestionPage() {
    name = quiza.getCurrentQuiz().name
    if (name == null)
        name = "کوییز"
    question_page().then(html => gotoURL(html, name, '/quiz'))
}


function goBack() {
    window.history.back();
}

function gotoURL(html, pageTitle, urlPath) {
    document.getElementById("root").innerHTML = html;
    document.title = pageTitle;
    window.history.pushState({ "html": html, "pageTitle": pageTitle }, "", urlPath);
}

function refreshHomePage() {
    user_home_page().then(html => replaceURL(html, 'خانه', '/panel'))
}

function refreshQuestionPage() {
    name = quiza.getCurrentQuiz().name
    if (name == null)
        name = "کوییز"
    question_page().then(html => replaceURL(html, name, '/quiz'))
}

function replaceURL(html, pageTitle, urlPath) {
    document.getElementById("root").innerHTML = html;
    document.title = pageTitle;
    window.history.replaceState({ "html": html, "pageTitle": pageTitle }, "", urlPath);
}

function setCookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/";
}
function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}


// function setTimerForQuestion(reamin_seconds) {

//     let setTimerToHtml = () => {
//         if (question == null){
//             question = quiza.getCurrentQuestion
//         }
//         //console.log(question)
//         if (quiza.getCurrentQuestion.uuid != question.uuid){
//             clearInterval(x);
//         }

//         seconds = reamin_seconds % 60
//         minutes = Math.floor(reamin_seconds / 60 % 60)
//         hour = Math.floor(reamin_seconds / 3600 % 24)
//         reamin_seconds -= 1
//         document.querySelector(".question .header .remaining-time #timer-seconds").innerText = seconds
//         document.querySelector(".question .header .remaining-time #timer-minutes").innerText = minutes
//         document.querySelector(".question .header .remaining-time #timer-hour").innerText = hour

//         if (seconds+minutes+hour <= 0) {
//             clearInterval(x);
//             nextQuestionClicked()
//         }
//     }
//     var x = setInterval(setTimerToHtml, 1000);

// }


async function login_to_quiza(username, password) {
    var myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/x-www-form-urlencoded");

    var urlencoded = new URLSearchParams();
    urlencoded.append("grant_type", "password");
    urlencoded.append("username", username);
    urlencoded.append("password", password);

    var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: urlencoded,
        redirect: 'follow'
    };
    nextstation = "io"
    myrequest = await fetch("http://localhost/auth/token", requestOptions)
    json_response = await myrequest.json()

    if (myrequest.status == 200) {
        setCookie('token', json_response.access_token);
        return true;
    }
    else
        return false;
}


async function login_clicked() {
    username = document.querySelector('#login_register_page input[name="username"]').value
    password = document.querySelector('#login_register_page input[name="password"]').value
    //console.log(username, password)
    res = await login_to_quiza(username, password)
    if (!res) {
        login_page_set_warning('نام کاربری یا رمز عبور اشتباه است')
        return;
    }

    gotoHomePage()

}

function viewModeClicked(btn) {
    //console.log(btn)
    viewid = parseInt(btn.getAttribute("viewid"))
    quiza.setQuizViewMode(viewid)
    refreshHomePage()
    // items = document.querySelectorAll(".quiz-view-mode .item")
    // items.forEach(item => {
    //     item.setAttribute('class','item')
    // });
    // btn.setAttribute('class','item-selected item ')
    // btn.
}

async function register_clicked() {
    fullname = document.querySelector('#login_register_page input[name="fullname"]').value
    username = document.querySelector('#login_register_page input[name="username"]').value
    password = document.querySelector('#login_register_page input[name="password"]').value
    
    var raw = JSON.stringify({
        name: fullname,
        email:username,
        password:password
    });

    var requestOptions = {
    method: 'POST',
    body: raw,
    redirect: 'follow'
    };

    request = await fetch("http://localhost/auth/register", requestOptions)
    json_response = await request.json()
    if (json_response.code === -20){
        login_page_set_warning("این ایمیل قبلا ثبت شده است")
        return;
    }
    if (json_response.code === 200){
        login_page_set_warning("ثبت نام انجام شد","")
    }

}

async function nextQuestionClicked() {    
    answer = {}
    if (quiza.getCurrentQuestion().qtype == quiza.QuestionType.MultiOption) {
        selectedOption = document.querySelector('input[name="answer"]:checked');
        if (selectedOption != null) {
            selectedOption = selectedOption.value;
            answer['option_answer'] = parseInt(selectedOption)
        }
    }
    else if (quiza.getCurrentQuestion().qtype == quiza.QuestionType.Textual) {
        answer['text_answer'] = document.querySelector('.question .content .answer .textual #answer-text').value
    }
    else if (quiza.getCurrentQuestion().qtype == quiza.QuestionType.FileUpload) {
        answer['uploded_file_url'] = "http://example.com/not/yet/implemented/why.jpg"
    }
    res = await quiza.sendAnswer(answer)
    refreshQuestionPage()

}

function login_page_set_warning(text, note = "خطا:") {
    warning = document.querySelector('#login_register_page .warning')
    warning.innerHTML = `<span style="color: red;">${note}</span> ${text}`

}



function register_page() {
    html = `\       
    <div id="login_register_page"> 
        <div class="login register">
            <form method="GET">
                <lable class="login-input-label">نام و نام خانوادگی</lable></br>
                <input class="login-input" type="text" name="fullname" /></br>
                <lable class="login-input-label">نام کاربری</lable></br>
                <input class="login-input" type="text" name="username" /></br>
                <label class="login-input-label">رمز عبور</label></br>
                <input class="login-input" type="password" name="password" /></br>
                <div class="login-button">
                    <input class="login-submit" onclick="register_clicked()" type="button" value="ثبت نام"  /> 
                    <input class="login-register" onclick="goBack()" type="button" value=" بازگشت" /> 
                </div>
            </form>
            <div class="warning"></div>
        </div>
    </div>`
    return html
    login_register_page = document.getElementById("root")
    login_register_page.innerHTML = html
}

function login_page() {
    html = `\
    <div id="login_register_page"> 
        <div class="login">
            <form method="GET">
                <lable class="login-input-label">نام کاربری</lable></br>
                <input class="login-input" type="text" name="username" /></br>
                <label class="login-input-label">رمز عبور</label></br>
                <input class="login-input" type="password" name="password" /></br>
                <div class="login-button">
                    <input class="login-submit" onclick="login_clicked()" type="button" value="ورود"  /> 
                    <input class="login-register" onclick="gotoRegisterPage()" type="button" value="ثبت نام" /> 
                </div>
            </form>
            <div class="warning"></div>
        </div>
    </div>`
    return html
    login_register_page = document.getElementById("root")
    login_register_page.innerHTML = html
}

function starQuizClicked(uuid) {
    //console.log("quiz ", uuid, " started")
    quiz = quiza.getQuizByUuidOffline(uuid)
    quiza.setCurrentQuiz(quiz)
    gotoQuestionPage()
}

async function user_home_page() {
    allquizitems = quiza.getAllQuizzes()


    if (quiza.quizViewId == 1)
        quizzes_array = allquizitems
    else if (quiza.quizViewId == 2) {
        
        quizzes_array = allquizitems.filter(quiz => {
            end_date = new Date(quiz.end_time)
            start_date = new Date(quiz.start_time)
            return ((Date.now() < end_date.getTime()) && (Date.now() > start_date.getTime()))
    
        })
    }
    else if (quiza.quizViewId == 3) {
        quizzes_array = allquizitems.filter(item => item.public == false)
    }


    quizitems = quizzes_array.map(quiz => {
        isdisable = 0
        end_date = new Date(quiz.end_time)
        start_date = new Date(quiz.start_time)
        if ((Date.now() > end_date.getTime()) || (Date.now() < start_date.getTime())) {
            isdisable = 1
        }

        item = `
            <div class="item ${isdisable && "item-disabled"}">
                <div class="information">
                    <div class="name">
                        ${quiz.name}
                    </div>
                    <div class="attribute">
                        <div class="attr-name">
                            تاریخ شروع
                        </div>
                        <div class="attr-value">
                            ${quiz.start_time_shamsi}
                        </div>
                    </div>
                    <div class="attribute">
                        <div class="attr-name">
                            تاریخ پایان
                        </div>
                        <div class="attr-value">
                            ${quiz.end_time_shamsi}
                        </div>
                    </div>

                    <div class="attribute">
                        <div class="attr-name">
                            تعداد سوالات
                        </div>
                        <div class="attr-value">
                            ${quiz.question_count}
                        </div>
                    </div>

                    <div class="attribute">
                        <div class="attr-name">
                            نام استاد
                        </div>
                        <div class="attr-value">
                            ${quiz.teacher_name}
                        </div>
                    </div>
                </div>
                <div class="quiz-action" ${!isdisable && 'onclick="starQuizClicked(\'' + quiz.uuid + '\')"'}>
                    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M3.96867 13.9157L13.6592 4.41662C14.906 3.19446 16.9283 3.19446 18.175 4.41662L19.4694 5.6854C20.7162 6.90755 20.7162 8.88985 19.4694 10.112L9.74061 19.6486C9.1843 20.1939 8.43007 20.4999 7.64282 20.4999H3.65854C3.28841 20.4999 2.99098 20.201 3.00021 19.8383L3.10043 15.8975C3.12036 15.1526 3.43127 14.4425 3.96867 13.9157ZM18.5381 6.59831L17.2437 5.32953C16.5113 4.61156 15.323 4.61156 14.5905 5.32953L13.8382 6.06697L17.7862 9.93612L18.5381 9.19909C19.2705 8.48112 19.2705 7.31628 18.5381 6.59831ZM4.89998 14.8287L12.9069 6.97989L16.8549 10.849L8.8093 18.7357L8.70228 18.8317C8.4067 19.0745 8.03222 19.2088 7.64282 19.2088L4.33345 19.2084L4.41707 15.9305C4.42814 15.5169 4.60126 15.1215 4.89998 14.8287ZM21 19.8545C21 19.498 20.7052 19.2089 20.3415 19.2089H13.471L13.3816 19.2148C13.0602 19.2576 12.8125 19.5277 12.8125 19.8545C12.8125 20.211 13.1073 20.5 13.471 20.5H20.3415L20.4308 20.4941C20.7523 20.4514 21 20.1813 21 19.8545Z" />
                    </svg>
                        
                </div>
            </div>`
        return item
    })

    html = `    <div class="main">
    <div class="right-sidebar">
        <div class="right-sidebar-items">
            <div class="item" id="item-selected">
                <div class="icon">
                    <svg class="icon-svg" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M20.3394 7.65929C21.0094 8.17829 21.4204 8.94929 21.4904 9.78829L21.5004 9.98929V18.0983C21.5004 20.1883 19.8494 21.8883 17.7804 21.9983H15.7904C14.8394 21.9793 14.0704 21.2393 14.0004 20.3093L13.9904 20.1683V17.3093C13.9904 16.9983 13.7594 16.7393 13.4504 16.6883L13.3604 16.6783H10.6894C10.3704 16.6883 10.1104 16.9183 10.0704 17.2183L10.0604 17.3093V20.1593C10.0604 20.2183 10.0494 20.2883 10.0404 20.3383L10.0304 20.3593L10.0194 20.4283C9.9004 21.2793 9.2004 21.9283 8.3304 21.9893L8.2004 21.9983H6.4104C4.3204 21.9983 2.6104 20.3593 2.5004 18.2983V9.98929C2.5094 9.13829 2.8804 8.34829 3.5004 7.79829L9.7304 2.78829C11.0004 1.77929 12.7804 1.73929 14.0894 2.66829L14.2504 2.78829L20.3394 7.65929ZM20.0994 18.2583L20.1104 18.0983V9.99829C20.0994 9.56929 19.9204 9.16829 19.6104 8.86929L19.4804 8.75829L13.3804 3.87829C12.6204 3.26829 11.5404 3.23929 10.7404 3.76829L10.5894 3.87829L4.5094 8.77929C4.1604 9.03829 3.9504 9.42829 3.9004 9.83829L3.8894 9.99829V18.0983C3.8894 19.4283 4.9294 20.5183 6.2504 20.5983H8.2004C8.4204 20.5983 8.6104 20.4493 8.6394 20.2393L8.6604 20.0593L8.6704 20.0083V17.3093C8.6704 16.2393 9.4904 15.3693 10.5404 15.2883H13.3604C14.4294 15.2883 15.2994 16.1093 15.3804 17.1593V20.1683C15.3804 20.3783 15.5304 20.5593 15.7304 20.5983H17.5894C18.9294 20.5983 20.0194 19.5693 20.0994 18.2583Z"/>
                    </svg>
                </div>
                <div class="text">
                    <span class="text-css">کوییز ها</span>
                </div>
            </div>
            <div class="item">
                <div class="icon">
                    <svg class="icon-svg"  viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M13.423 2.00105C13.0474 1.98661 12.6739 2.12156 12.3925 2.37643C12.1684 2.57938 12.0162 2.84619 11.957 3.13824L11.9349 3.30295L11.9299 3.44914L12.3741 9.97348C12.4295 10.8051 13.1615 11.4382 14.0133 11.39L20.6588 10.9567C21.0477 10.9286 21.4041 10.7524 21.6545 10.4668C21.8538 10.2393 21.9737 9.95621 21.9977 9.65855L22 9.4567L21.9904 9.34084C21.3029 5.20162 17.7085 2.12227 13.423 2.00105ZM13.4113 3.44902L13.6287 3.45932C17.0119 3.66443 19.8318 6.0802 20.4854 9.33352L20.5182 9.51352L13.9214 9.94502C13.888 9.94688 13.8537 9.91719 13.8511 9.87814L13.4113 3.44902ZM8.7814 5.84532C9.502 5.74681 10.211 6.12453 10.4978 6.7606C10.5855 6.93485 10.6382 7.12392 10.6533 7.32102L11.0419 12.8095C11.0471 12.8847 11.0827 12.9548 11.1409 13.0042C11.1845 13.0413 11.2381 13.0645 11.298 13.0712L11.3599 13.0724L16.9341 12.7366C17.3867 12.71 17.8305 12.8675 18.1604 13.1719C18.4902 13.4763 18.6768 13.9004 18.6744 14.3912C18.4265 18.0037 15.773 21.0237 12.159 21.8065C8.54503 22.5893 4.83611 20.9474 3.05781 17.7848C2.58229 16.9695 2.26178 16.0778 2.1138 15.1749L2.06643 14.8359C2.0253 14.5821 2.00319 14.3257 2 14.0795L2.00311 13.8372C2.0134 10.0655 4.66156 6.80403 8.38809 5.92434L8.64383 5.86807L8.7814 5.84532ZM9.01643 7.27813L8.93217 7.28772L8.70369 7.33933C5.73526 8.05478 3.6062 10.6103 3.48796 13.621L3.4828 13.8661C3.47569 14.0525 3.4825 14.2392 3.50499 14.4378L3.53277 14.6408C3.63212 15.495 3.90795 16.3206 4.34914 17.0772C5.81632 19.6863 8.86669 21.0367 11.839 20.3929C14.8113 19.7491 16.9936 17.2653 17.1958 14.3414C17.1959 14.2974 17.1774 14.2552 17.1446 14.225C17.1228 14.2049 17.0959 14.1912 17.0675 14.1851L17.024 14.1817L11.459 14.5169C10.9894 14.5503 10.5255 14.3992 10.17 14.0971C9.81456 13.7951 9.59684 13.3669 9.56522 12.91L9.17702 7.42617C9.17632 7.41708 9.17385 7.40822 9.15682 7.37299C9.1315 7.31695 9.07648 7.28131 9.01643 7.27813Z"/>
                    </svg>                            
                </div>        
                <div class="text">
                    <span class="text-css">نمرات</span>
                </div>
            </div>
            <div class="item">
                <div class="icon">
                    <svg class="icon-svg" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" clip-rule="evenodd" d="M12.058 2.00026C8.54635 1.98615 5.28554 3.80703 3.46059 6.80012C1.63541 9.79361 1.51288 13.5227 3.13765 16.6292L3.32147 16.9875C3.39175 17.1192 3.40531 17.2613 3.36458 17.3927C3.10204 18.0865 2.87136 18.8357 2.6873 19.597L2.66776 19.761C2.66776 20.5264 3.07616 21.0523 3.88671 21.0343L4.02167 21.0181C4.75798 20.8555 5.4831 20.646 6.19261 20.3909C6.28665 20.3671 6.4407 20.3763 6.57971 20.4332L7.26224 20.8195C7.26378 20.8242 7.26493 20.8278 7.27208 20.832L7.31788 20.848C10.9929 22.7804 15.4812 22.2473 18.5997 19.5079C21.7187 16.7681 22.8199 12.3901 21.3675 8.50389C19.9153 4.61805 16.2115 2.03079 12.058 2.00026ZM11.7675 3.39905L12.0484 3.39465C15.6231 3.42184 18.8109 5.64864 20.0605 8.99237C21.31 12.3357 20.3626 16.1021 17.6788 18.4596L17.4587 18.6466C14.8626 20.7781 11.2582 21.2077 8.23269 19.7468L7.94496 19.6026L7.95729 19.6042L7.93909 19.5993L7.51677 19.3569C7.36471 19.271 7.24408 19.2059 7.14685 19.1591C6.6837 18.9681 6.21354 18.94 5.77133 19.0617L5.35272 19.2055C5.07605 19.2969 4.80372 19.3795 4.53273 19.4541L4.13767 19.5573L4.04356 19.9249C4.21419 19.2192 4.42804 18.5247 4.68389 17.8451C4.84853 17.3183 4.79818 16.7905 4.55755 16.3402L4.37662 15.9874C2.97627 13.3099 3.08168 10.1019 4.65196 7.52651C6.17338 5.03123 8.85494 3.48238 11.7675 3.39905ZM6.4746 12.0002C6.4746 11.37 6.98586 10.8596 7.61596 10.8596C8.24606 10.8596 8.75732 11.37 8.75732 12.0002C8.75732 12.6304 8.24606 13.1409 7.61596 13.1409C6.98586 13.1409 6.4746 12.6304 6.4746 12.0002ZM10.9115 12.0002C10.9115 11.37 11.4227 10.8596 12.0528 10.8596C12.6829 10.8596 13.1942 11.37 13.1942 12.0002C13.1942 12.6304 12.6829 13.1409 12.0528 13.1409C11.4227 13.1409 10.9115 12.6304 10.9115 12.0002ZM16.4897 10.8596C15.8596 10.8596 15.3484 11.37 15.3484 12.0002C15.3484 12.6304 15.8596 13.1409 16.4897 13.1409C17.1198 13.1409 17.6311 12.6304 17.6311 12.0002C17.6311 11.37 17.1198 10.8596 16.4897 10.8596Z"/>
                    </svg>
                </div>                            
                <div class="text">
                    <span class="text-css">درخواست ها</span>
                </div>
            </div>

        </div>
    </div>
    <div class="content">
        <div class="quiz-view-mode">
            <div class="item ${quiza.getQuizViewMode() == 1 && "item-selected"}"  viewid="1"  onclick="viewModeClicked(this)">
                همه کوییز ها
            </div>
            <div class="item ${quiza.getQuizViewMode() == 2 && "item-selected"}" viewid="2" onclick="viewModeClicked(this)">
                کوییز های فعال
            </div>
            <div class="item ${quiza.getQuizViewMode() == 3 && "item-selected"}" viewid="3" onclick="viewModeClicked(this)">
                کوییز های اختصاصی
            </div>
        </div>
        <div class="quizzes">
            ${quizitems.join('\n')}

        </div>
    </div>
</div>
`
    return html;
}

async function question_page() {
    //console.log("next question")
    
    quiz = quiza.getCurrentQuiz();
    json_response = await quiza.getRequest(`http://localhost/quiz/${quiz.uuid}/question/next`)
    question = json_response.data
    quiza.setCurrentQuestion(question)
    console.log(question)
    if (json_response.code === -14) {
        html = `
        <div class="quiz-finished">
            <p>
                سوالی برای پاسخ دادن وجود ندارد
            </p>
            <div class="general-boutton" onclick="goBack()">
                بازگشت
            </div>
        </div>
    `
        return html;
    }

    options_list = question.options
    options = options_list.map(option => {
        option_div = `                    
        <div class="option">
            <input type="radio" id="op${option.number}" name="answer" value="${option.number}">
            <label for="op${option.number}">${option.content}</label>
            <span class="checkmark"></span>
        </div>`
        return option_div

    })

    questionHasTime = question.quantum != null && question.quantum != 0
    if (questionHasTime){
        user_start_time = new Date(question.user_start_time)
        user_start_time = user_start_time.getTime()
        end_time = user_start_time + question.quantum*1000
        remaining_time = end_time - Date.now()
        remaining_time = Math.floor(remaining_time / 1000)
    }
    
    html = `
    <div class="question">
    <div class="content">
        <div class="header">
            <div class="number">
                ${"سوال " + question.nth + " از " + quiz.question_count}
            </div>
            <div class="remaining-time" ${!questionHasTime && 'style="display:none"'}> 
                <div id="timer-hour">
                </div>
                <span class="timer-spliter">:</span>
                <div id="timer-minutes">
                </div>
                <span class="timer-spliter">:</span>
                <div id="timer-seconds">
                </div>
            </div>
        </div>
        <div class="question-text">
        ${question.text}
        </div>
        <div class="question-image">
            <img src="" />
        </div>
        <div class="answer">
            <div class="multipleoption" ${question.qtype !== quiza.QuestionType.MultiOption && 'style="display:none;"'}>
                <form>
                ${options.join("\n")}
                </form>
                
            </div>
            <div class="textual" ${question.qtype !== quiza.QuestionType.Textual && 'style="display:none;"'}>
                <textarea id="answer-text"></textarea>
            </div>
            <div class="fileupload" ${question.qtype !== quiza.QuestionType.FileUpload && 'style="display:none;"'}>

            </div>
        </div>
    </div>
    <div class="left-sidebar">
        <div class="information">
            <div class="name">
                ${quiz.name}
            </div>
            <div class="teacher-name">
                ${quiz.teacher_name}
            </div>
        </div>
        <div class="next-question-btn" onclick="nextQuestionClicked()">
            سوال بعد
        </div>
    </div>
</div>
`
    //console.log("iam question : ", questionHasTime)
 
    questionHasTime ? quiza.startTimerForQuestion(remaining_time) : quiza.stopTimerForQuestion();
    return html
}