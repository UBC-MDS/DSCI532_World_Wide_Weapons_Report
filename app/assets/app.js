$(document).ready(function () {
    setInterval(function () {
        // Ugly hack, but need to overcome html.Iframe component limitation somehow
        $('iframe').attr('scrolling', 'no')
    }, 100)
})