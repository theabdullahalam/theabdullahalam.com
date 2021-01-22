function toggleDarkMode(){
    
    // GET DARK MODE SHEET 
    let darksheet = document.getElementById('darkmodesheet');

    // ENABLE ANIMATION STYLESHEET
    let animationsheet = document.getElementById('darkanimation');
    animationsheet.disabled = false

    // SWITCH
    darksheet.disabled = !darksheet.disabled

    // DISABLE ANIMATION SHEET AFTER ANIMATION IS COMPLETE
    setTimeout(() => {animationsheet.disabled = true}, 1000)

    // REMEMBER
    document.cookie = 'darksheet=' + String(darksheet.disabled) + '; path=/; SameSite=Lax'

}

function getCookieVal(key){

    cookiestring = document.cookie
    keyvals = null

    // IF COOKIE STRING CONTAINS ;
    if(cookiestring.includes('; ')){
        cookies = cookiestring.split('; ')
        for (i = 0; i < cookies.length - 1; i++){
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

function updateDarkMode(){

    // darksheet COOKIE VAL
    let darksheetcookie = getCookieVal('darksheet')
    console.log(darksheetcookie !== null)

    // GET DARK MODE SHEET 
    var darksheet = document.getElementById('darkmodesheet');

    // SWITCH
    if(darksheetcookie !== null){ // DO NOTHING ON FIRST LOAD
        darksheet.disabled = (getCookieVal('darksheet') === 'true')
    }    
    
}


// UPDATE DARK MODE ON LOAD
updateDarkMode()