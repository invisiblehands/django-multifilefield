$(function interstitial(){
  var $overlay, $interstatial;

  function closeHandler(evt){
    if (evt) evt.preventDefault();

    $interstitial.removeClass('interstitial-show');
    $interstitial.off('click');
    $overlay.off('click');
  }

  function openHandler(evt){
    if (evt) evt.preventDefault();

    $interstitial.addClass('interstitial-show');
    $overlay.on('click', closeHandler);
  }

  function popup(){
    $interstitial.find('.close').on('click', closeHandler);

    openHandler();
  }

  function linkHandler(evt){
    $interstitial.removeClass('interstitial-show');
    $interstitial.off('click');
    $overlay.off('click');
  }
  

  $overlay = $('.interstitial-overlay');
  $interstitial = $('#interstitial');

  if (!$interstitial) return;

  $interstitial.find('.interstitial-content').on('click', linkHandler);
  $interstitial.find('.interstitial-close').on('click', closeHandler);

  setTimeout(function(){
    popup($interstitial, $overlay);
  }, 4000);
});