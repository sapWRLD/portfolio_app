// Set current year in the footer
$(document).ready(function() {
    $('#spanYear').html(new Date().getFullYear());

    // Highlight active navbar link
    var path = window.location.pathname;
    $('.nav-list li a').each(function() {
        if ($(this).attr('href') === path) {
            $(this).addClass('active');
        }
    });
    var path = window.location.pathname;
    $('.admin-list li a').each(function() {
        if ($(this).attr('href') === path) {
            $(this).addClass('active');
        }
    });
});
