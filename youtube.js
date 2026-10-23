// Swaps a video thumbnail for the YouTube player when it's clicked, so the
// "Channels I learn from" section doesn't load a dozen players up front.
document.querySelectorAll('.yt-embed').forEach(function (button) {
  button.addEventListener('click', function () {
    var frame = document.createElement('iframe');
    frame.src = 'https://www.youtube-nocookie.com/embed/' + button.dataset.video + '?autoplay=1';
    frame.title = button.dataset.title;
    frame.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    frame.referrerPolicy = 'strict-origin-when-cross-origin';
    frame.allowFullscreen = true;
    button.replaceWith(frame);
    if (window.goatcounter && window.goatcounter.count) {
      window.goatcounter.count({ path: 'video: ' + button.dataset.video, title: button.dataset.title, event: true });
    }
  });
});
