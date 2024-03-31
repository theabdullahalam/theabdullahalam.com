function loadDarkMode(){
    setDarkMode(false);
    // let darkmode = getCookieVal('darkmode');
    
    // if (darkmode === null){
    //     document.cookie = 'darkmode=false; path=/; SameSite=Lax';
    //     darkmode = getCookieVal('darkmode');
    // }


    // if (darkmode === 'false'){
    //     setDarkMode(false)
    // }

    // if (darkmode === 'true'){
    //     setDarkMode(true)
    // }
    
}


function setDarkMode(state){
    let body = document.getElementById('body');
    if (state){
        body.classList.add('darkmode');
    }else{
        body.classList.remove('darkmode');
    }
}


function animateChange(state){
    let body = document.getElementById('body');
    if (state){
        body.classList.add('animatefade');
    }else{
        body.classList.remove('animatefade');
    }
}


function toggleDarkMode(){

    // GET COOKIE
    let cookie_val = getCookieVal('darkmode');
    // This is some crazy cool stuff

    // TEMPORARILY ENABLE ANIMATIONS FOR ONE SECOND
    animateChange(true)
    setTimeout(()=>{
        animateChange(false)
    }, 1000);

    // TOGGLE DARKMODE
    if (cookie_val === 'true'){
        cookie_val = 'false';
        setDarkMode(false)
    }else{
        cookie_val = 'true';
        setDarkMode(true)
    }

    // UPDATE COOKIE
    document.cookie = 'darkmode=' + cookie_val + '; path=/; SameSite=Lax'

}

function getCookieVal(key){

    cookiestring = document.cookie
    keyvals = null

    // IF COOKIE STRING CONTAINS ;
    if(cookiestring.includes('; ')){
        cookies = cookiestring.split('; ')
        for (i = 0; i < cookies.length; i++){
            cookie = cookies[i]
            keyvals = cookie.split('=')

            if (keyvals[0] == key){
                return(keyvals[1])
            }
        }
    } else {
        keyvals = cookiestring.split('=')

        if (keyvals[0] == key){
            return(keyvals[1])
        }
    }

    return(null)


}


// LOAD DARK MODE ON LOAD
loadDarkMode()
