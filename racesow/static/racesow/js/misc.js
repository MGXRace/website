$(function(){
    $("[data-toggle='tooltip']").tooltip({
        container: 'body',
        delay: 250
    });
});

/**
 * Handle clicks on timezone dropdown menu
 * */
$(document.body).on('click', '.dropdown-menu li', function (event) {
    var $target = $(event.currentTarget);

    // clicking the button should do nothing
    if ($target.hasClass('.current-tz'))
        return false;

    // clicking same tz should not post
    if ($("#tz").val() == $target.text())
        return false;

    $target.closest('#tz-form').find('.dropdown-toggle').dropdown('toggle');
    $('#tz').val($target.text());
    $('#tz-form').submit();
    event.stopPropagation(); // prevent handler from being run twice
});
