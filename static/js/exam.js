function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Get cookie "matr" and set on <b> element with id="matr"
matr = getCookie("matr");
document.getElementById("matr").innerHTML = matr;