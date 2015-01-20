//Stack menu when collapsed
$('#page-navbar-collapse').on('show.bs.collapse', function() {
    $('.nav-pills').addClass('nav-stacked');
});

//Unstack menu when not collapsed
$('#page-navbar-collapse').on('hide.bs.collapse', function() {
    $('.nav-pills').removeClass('nav-stacked');
});